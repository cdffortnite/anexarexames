import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite conexões de outros domínios (como seu frontend no AwardSpace)

# Configuração da API DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # Pegue a chave da API no Render
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# Histórico da conversa (poderia ser substituído por um banco de dados se necessário)
user_conversations = {}

# Contexto médico especializado para guiar a IA
CONTEXT_MEDICO = (
    "Você é um assistente virtual especializado em assistência médica. "
    "Responda com precisão, baseando-se em diretrizes científicas. "
    "Se um diagnóstico ou tratamento for necessário, recomende sempre que o usuário consulte um médico. "
    "Evite respostas vagas e forneça informações confiáveis sempre que possível."
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
