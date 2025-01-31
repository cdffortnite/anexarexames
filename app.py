import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite conexões de outros domínios (como seu frontend no AwardSpace)

# Configuração da API DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # Pegue a chave da API no Render
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# Contexto médico especializado para guiar a IA
CONTEXT_MEDICO = (
    "Você é um assistente virtual especializado em assistência médica. "
    "Responda de forma objetiva e baseada em diretrizes científicas. "
    "Se um diagnóstico ou tratamento for necessário, recomende sempre que o usuário consulte um médico. "
    "Evite respostas vagas e forneça informações confiáveis sempre que possível."
)

# Banco de respostas pré-definidas para perguntas comuns
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
    """Recebe uma mensagem do usuário e retorna uma resposta especializada da API DeepSeek."""
    data = request.json
    user_message = data.get("message", "").strip().lower()

    if not user_message:
        return jsonify({"error": "Nenhuma mensagem recebida."}), 400

    # Verifica se a pergunta tem uma resposta pré-definida
    if user_message in RESPOSTAS_PADRAO:
        return jsonify({"response": RESPOSTAS_PADRAO[user_message]})

    # Caso o usuário envie um exame para análise
    if "exame:" in user_message:
        user_message = f"Por favor, analise o seguinte exame médico e forneça um parecer técnico: {user_message.replace('exame:', '').strip()}"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "temperature": 0.3,  # Ajuste para maior precisão e menor criatividade
        "messages": [
            {"role": "system", "content": CONTEXT_MEDICO},  # Define o contexto especializado
            {"role": "user", "content": user_message}
        ]
    }

    response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return jsonify({"error": f"Erro na API DeepSeek: {response.status_code}"}), response.status_code

    deepseek_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erro na resposta.")

    return jsonify({"response": deepseek_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
