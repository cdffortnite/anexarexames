import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite conexões de outros domínios (frontend no AwardSpace)

# Configuração da API DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # Chave da API como variável de ambiente
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route("/")
def home():
    return jsonify({"message": "API do DeepSeek rodando!"})

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    try:
        # Simulação de processamento do exame
        laudo = f"Arquivo '{file.filename}' processado com sucesso."
        
        # Enviar para DeepSeek
        deepseek_response = deepseek_analyze(laudo)

        return jsonify({"laudo": deepseek_response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def deepseek_analyze(texto):
    """Envia um texto para análise na API DeepSeek"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": texto}]
    }

    response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return f"Erro ao processar laudo: {response.status_code}"

    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erro na resposta")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
