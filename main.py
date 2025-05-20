import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHATGPT_API_KEY = os.environ["CHATGPT_API_KEY"]

# Функция для общения с OpenAI
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

    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("OpenAI error:", response.text)
        return "Произошла ошибка при обращении к ChatGPT."

# Обработка сообщений от Telegram
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Получены данные от Telegram:", data)

    message = data["message"].get("text")
    if not message:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    reply = ask_chatgpt(message)

    send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": reply}
    requests.post(send_url, json=payload)

    return {"ok": True}

# Проверка сервера
@app.route("/", methods=["GET"])
def index():
    return "Бот работает!"
