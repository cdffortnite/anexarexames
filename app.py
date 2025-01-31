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

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    try:
        # Simulação de leitura do arquivo (caso seja texto)
        file_content = file.read().decode("utf-8") if file.filename.endswith(".txt") else file.filename

        # Enviar o texto para DeepSeek
        deepseek_response = deepseek_analyze(file_content)

        return jsonify({
            "laudo": deepseek_response,  # Agora a resposta é realmente da DeepSeek
            "status": "Arquivo enviado com sucesso!"
        })
    
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
        "messages": [{"role": "user", "content": f"Analise este exame: {texto}"}]
    }

    response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return f"Erro ao processar laudo: {response.status_code}"

    deepseek_result = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erro na resposta")
    return deepseek_result

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()

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
