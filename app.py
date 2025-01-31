import os
import requests
import pytesseract
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuração da API DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
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
        # Verifica se o arquivo é uma imagem
        if file.filename.endswith((".png", ".jpg", ".jpeg")):
            image = Image.open(file)
            extracted_text = pytesseract.image_to_string(image)  # Extrai texto da imagem
            if not extracted_text.strip():
                return jsonify({"error": "Nenhum texto encontrado na imagem."}), 400
        else:
            return jsonify({"error": "Apenas imagens são suportadas."}), 400

        # Enviar para DeepSeek para análise
        deepseek_response = deepseek_analyze(extracted_text)

        return jsonify({
            "laudo": deepseek_response,
            "status": "Arquivo enviado com sucesso!"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def deepseek_analyze(texto):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": f"Analise este exame e forneça um diagnóstico: {texto}"}]
    }

    response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return f"Erro ao processar laudo: {response.status_code}"

    deepseek_result = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erro na resposta")
    return deepseek_result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
