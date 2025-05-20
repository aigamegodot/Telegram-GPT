import os
import requests
import logging
from flask import Flask, request

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHATGPT_API_KEY = os.environ["CHATGPT_API_KEY"]

def ask_chatgpt(message):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {CHATGPT_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": message}]
    }

    response = requests.post(url, headers=headers, json=payload)

    logging.info("=== Ответ от OpenAI ===")
    logging.info(f"Status code: {response.status_code}")
    logging.info(f"Response text: {response.text}")
    logging.info("=======================")

    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception:
        return "Произошла ошибка при обращении к ChatGPT."

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Получено сообщение от Telegram: {data}")

    message = data["message"].get("text")
    if not message:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    reply = ask_chatgpt(message)

    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": reply}
    requests.post(send_url, json=payload)

    return {"ok": True}

@app.route("/", methods=["GET"])
def index():
    return "Бот работает!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
