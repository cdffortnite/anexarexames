import os
import httpx  # Substituímos o requests pelo httpx assíncrono
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_compress import Compress  # Importa a biblioteca de compressão

app = Flask(__name__)
CORS(app)      # Permite conexões de outros domínios
Compress(app)  # Ativa a compressão de respostas

# Configuração da API DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# Histórico da conversa (atenção: para múltiplos workers, considere um armazenamento externo)
user_conversations = {}

# Contexto médico especializado para guiar a IA
CONTEXT_MEDICO = (
    "Você é o assistente Sapphir, um chatbot médico projetado para fornecer respostas rápidas e diretas a profissionais de saúde, baseadas em diretrizes clínicas atualizadas e evidências científicas.\n"
    "Priorize velocidade e objetividade. Responda imediatamente sem ajustes de tom ou complexidade.\n"
    "Siga estas diretrizes:\n"
    "1. *Respostas Diretas e Rápidas*: Forneça a resposta de maneira objetiva, sem necessidade de adaptação para diferentes níveis de especialização. Utilize linguagem técnica padrão.\n"
    "2. *Base Científica*: Utilize fontes como PubMed, Cochrane, UpToDate, NICE, WHO e diretrizes médicas reconhecidas. Cite fontes apenas se explicitamente solicitado pelo usuário.\n"
    "3. *Uso de Ferramentas Clínicas*: Quando aplicável, inclua escores e cálculos médicos relevantes (ex.: CHA₂DS₂-VASc, HAS-BLED, SOFA, APACHE II, MELD, Child-Pugh, etc.).\n"
    "4. *Evite Explicações Desnecessárias*: Presuma que o usuário tem conhecimento técnico. Não forneça definições básicas ou contexto introdutório.\n"
    "5. *Tom Profissional e Objetivo*: Sempre responda como um médico experiente, focado na prática clínica.\n"
    "6. *Concisão e Eficiência*: Limite as respostas a 150 tokens, organizando-as para evitar cortes. Use emojis de forma sutil para tornar a resposta mais fluida, mas sem comprometer a formalidade médica. 😊\n"
)

# Banco de respostas rápidas para perguntas comuns
RESPOSTAS_PADRAO = {
    "quais são os sintomas de dengue?": "Os sintomas da dengue incluem febre alta, dores musculares, dor atrás dos olhos, manchas vermelhas na pele e fadiga intensa. Se houver sinais de gravidade, como sangramento ou tontura intensa, procure atendimento médico imediato.",
    "como tratar uma gripe?": "O tratamento da gripe inclui repouso, hidratação e uso de antitérmicos para febre. Se houver falta de ar ou sintomas persistentes, consulte um médico.",
    "quando tomar antibiótico?": "Antibióticos devem ser usados somente com prescrição médica para infecções bacterianas. O uso inadequado pode causar resistência aos medicamentos."
}

# Cria um cliente HTTP assíncrono global
async_client = httpx.AsyncClient()

@app.route("/")
async def home():
    """Verifica se a API está rodando corretamente"""
    return jsonify({"message": "API do DeepSeek rodando!"})

@app.route("/chat", methods=["POST"])
async def chat():
    """Mantém histórico da conversa e retorna uma resposta da API DeepSeek de forma assíncrona."""
    data = request.get_json()  # Pode ser usado também request.json
    user_message = data.get("message", "").strip()
    user_id = data.get("user_id", "default_user")  # Identifica o usuário para armazenar o contexto

    if not user_message:
        return jsonify({"error": "Nenhuma mensagem recebida."}), 400

    # Verifica se existe resposta rápida para a mensagem
    if user_message.lower() in RESPOSTAS_PADRAO:
        return jsonify({"response": RESPOSTAS_PADRAO[user_message.lower()]})

    # Mantém o histórico da conversa
    if user_id not in user_conversations:
        user_conversations[user_id] = [{"role": "system", "content": CONTEXT_MEDICO}]
    user_conversations[user_id].append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "temperature": 0.2,
        "max_tokens": 150,
        "messages": user_conversations[user_id]
    }

    try:
        response = await async_client.post(
            DEEPSEEK_URL,
            headers=headers,
            json=payload,
            timeout=10.0  # Define um timeout para evitar travamentos
        )
    except httpx.RequestError as exc:
        return jsonify({"error": f"Erro na API DeepSeek: {exc}"}), 500

    if response.status_code != 200:
        return jsonify({"error": f"Erro na API DeepSeek: {response.status_code}"}), response.status_code

    deepseek_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erro na resposta.")

    # Adiciona a resposta da IA ao histórico
    user_conversations[user_id].append({"role": "assistant", "content": deepseek_response})

    return jsonify({"response": deepseek_response})

if __name__ == "__main__":
    # Nota: Para aproveitar totalmente o assincronismo, é recomendável usar um servidor ASGI (ex: hypercorn ou uvicorn)
    app.run(host="0.0.0.0", port=5000)
