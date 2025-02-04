import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_compress import Compress  # Importa a biblioteca de compressão

app = Flask(__name__)
CORS(app)  # Permite conexões de outros domínios (como seu frontend no AwardSpace)
Compress(app)  # Ativa a compressão de respostas

# Configuração da API DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # Pegue a chave da API no Render
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# Histórico da conversa (poderia ser substituído por um banco de dados se necessário)
user_conversations = {}

# Contexto médico especializado para guiar a IA
CONTEXT_MEDICO = (
    "Você é o assistente Sapphir, ajudante virtual especializado em medicina (chatbot), projetado para auxiliar profissionais de saúde com informações precisas, baseadas em evidências científicas e diretrizes clínicas atualizadas. "
    "Sua função é fornecer respostas claras, objetivas e acessíveis, limitadas a 150 tokens por mensagem, para garantir eficiência na comunicação. "
    "Siga estas diretrizes:\n"
    "1. **Precisão e Evidências**: Baseie suas respostas em fontes confiáveis como PubMed, Cochrane, UpToDate, NICE, WHO e outras, citando-as quando relevante.\n"
    "2. **Calculadoras e Escores**: Utilize calculadoras e escores médicos (ex.: IMC, Clearance de Creatinina, Escore de Glasgow, CHA₂DS₂-VASc, HAS-BLED, SOFA, APACHE II, MELD, Child-Pugh, etc.) sempre que pertinente ao caso.\n"
    "3. **Linguagem Técnica Adequada**: Adapte a complexidade da linguagem ao contexto profissional, fornecendo informações técnicas detalhadas quando necessário.\n"
    "4. **Tom Profissional**: Formule respostas como um médico experiente, mantendo um tom profissional e direto, focado na prática clínica.\n"
    "5. **Concisão e Clareza**: Evite respostas vagas. Priorize informações práticas e diretamente aplicáveis ao contexto do usuário."
)

# Banco de respostas rápidas para perguntas comuns
RESPOSTAS_PADRAO = {
    "quais são os sintomas de dengue?": "Os sintomas da dengue incluem febre alta, dores musculares, dor atrás dos olhos, manchas vermelhas na pele e fadiga intensa. Se houver sinais de gravidade, como sangramento ou tontura intensa, procure atendimento médico imediato.",
    "como tratar uma gripe?": "O tratamento da gripe inclui repouso, hidratação e uso de antitérmicos para febre. Se houver falta de ar ou sintomas persistentes, consulte um médico.",
    "quando tomar antibiótico?": "Antibióticos devem ser usados somente com prescrição médica para infecções bacterianas. O uso inadequado pode causar resistência aos medicamentos."
}

@app.route("/")
def home():
    """Verifica se a API está rodando corretamente"""
    return jsonify({"message": "API do DeepSeek rodando!"})

@app.route("/chat", methods=["POST"])
def chat():
    """Mantém histórico da conversa e retorna uma resposta da API DeepSeek."""
    data = request.json
    user_message = data.get("message", "").strip()
    user_id = data.get("user_id", "default_user")  # Identifica o usuário para armazenar o contexto

    if not user_message:
        return jsonify({"error": "Nenhuma mensagem recebida."}), 400

    # Se a mensagem já tem uma resposta rápida no banco de dados
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
        "temperature": 0.2,  # Reduz criatividade e melhora precisão médica
        "max_tokens": 150,  # Limita o tamanho da resposta
        "messages": user_conversations[user_id]  # Mantém o histórico da conversa
    }

    response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return jsonify({"error": f"Erro na API DeepSeek: {response.status_code}"}), response.status_code

    deepseek_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erro na resposta.")

    # Adiciona resposta da IA ao histórico
    user_conversations[user_id].append({"role": "assistant", "content": deepseek_response})

    return jsonify({"response": deepseek_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
