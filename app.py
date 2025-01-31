import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite conexões de outros domínios (como seu frontend no AwardSpace)

# Configuração da API DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # Pegue a chave da API no Render
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route("/")
def home():
    return jsonify({"message": "API do DeepSeek rodando!"})

@app.route("/chat", methods=["POST"])
def chat():
    """Recebe uma mensagem do usuário e retorna a resposta da API DeepSeek."""
    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Nenhuma mensagem recebida."}), 400

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": user_message}]
    }

    response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return jsonify({"error": f"Erro na API DeepSeek: {response.status_code}"}), response.status_code

    deepseek_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erro na resposta.")

    return jsonify({"response": deepseek_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
