import os
import requests
import pytesseract
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite conexões do frontend (AwardSpace)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# Função para converter imagem em texto (OCR)
def extract_text_from_image(image):
    return pytesseract.image_to_string(image).strip()

# Endpoint para análise de exames (texto ou imagem)
@app.route("/analisar-exame", methods=["POST"])
def analisar_exame():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Nenhum arquivo selecionado."}), 400

    try:
        # Verifica se é uma imagem
        if file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            image = Image.open(file)
            extracted_text = extract_text_from_image(image)
            if not extracted_text:
                return jsonify({"error": "Nenhum texto encontrado na imagem."}), 400
        else:
            return jsonify({"error": "Apenas imagens são suportadas."}), 400

        # Envia para DeepSeek para análise
        response = requests.post(DEEPSEEK_URL, headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }, json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": f"Analise este exame: {extracted_text}"}]
        })

        deepseek_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erro na resposta.")

        return jsonify({"laudo": deepseek_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
