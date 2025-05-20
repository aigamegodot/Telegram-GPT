import os
import logging
import requests
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

def ask_gemini(message):
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": message}]}]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=data)
        logging.info(f"Gemini status: {response.status_code}")
        logging.info(f"Gemini response: {response.text}")

        if response.status_code == 200:
            gemini_data = response.json()
            return gemini_data["candidates"][0]["content"]["parts"][0]["text"]
        elif response.status_code == 401:
            return "Ошибка: Неверный API ключ Gemini."
        elif response.status_code == 429:
            return "Ошибка: Превышен лимит запросов Gemini."
        elif response.status_code >= 500:
            return "Ошибка: Проблема на стороне сервера Gemini. Попробуйте позже."
        else:
            return f"Неизвестная ошибка Gemini: {response.status_code}"
    except Exception as e:
        logging.error(f"Ошибка при обращении к Gemini: {str(e)}")
        return "Ошибка при обращении к Gemini. Проверьте логи на Render."

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

@app.route("/", methods=["GET"])
def home():
    return "Telegram Gemini Bot is running."

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Получено сообщение от Telegram: {data}")

    try:
        chat_id = data["message"]["chat"]["id"]
        message_text = data["message"]["text"]
        reply = ask_gemini(message_text)
    except Exception as e:
        logging.error(f"Ошибка обработки сообщения: {str(e)}")
        reply = "Произошла ошибка при обработке сообщения."

    send_message(chat_id, reply)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
