import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite conexões do frontend (AwardSpace ou qualquer outro domínio)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# Endpoint para análise de exames
@app.route("/analisar-exame", methods=["POST"])
def analisar_exame():
    data = request.json
    exame_texto = data.get("texto", "")

    if not exame_texto:
        return jsonify({"error": "Nenhum texto de exame fornecido."}), 400

    response = requests.post(DEEPSEEK_URL, headers={
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }, json={
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": f"Analise este exame: {exame_texto}"}]
    })

    deepseek_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erro na resposta.")
    return jsonify({"laudo": deepseek_response})

# Endpoint do chatbot
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Nenhuma mensagem recebida."}), 400

    response = requests.post(DEEPSEEK_URL, headers={
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }, json={
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": user_message}]
    })

    deepseek_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erro na resposta.")
    return jsonify({"response": deepseek_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
