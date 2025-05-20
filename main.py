import os
import logging
import requests
import google.generativeai as genai
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

def ask_gemini(message):
    try:
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        return "Ошибка при обращении к Gemini."

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Получено сообщение: {data}")

    message = data["message"].get("text")
    if not message:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    reply = ask_gemini(message)

    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": reply}
    requests.post(send_url, json=payload)

    return {"ok": True}

@app.route("/", methods=["GET"])
def index():
    return "Бот с Gemini работает!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
