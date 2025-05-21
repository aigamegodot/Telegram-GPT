import os
import logging
import requests
from flask import Flask, request

app = Flask(__name__)

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Токены
TELEGRAM_TOKEN = "8090532343:AAFM3AosXFH6dY6r3ukPq4LWCOS0Gl9G_Xc"
DEEPSEEK_API_KEY = "sk-65464c1f4d804f77bb6978f06d7d8895"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Главная страница
@app.route("/")
def index():
    return "Бот работает!"

# Вебхук для Telegram
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Получено сообщение от Telegram: {data}")

    try:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]
    except KeyError:
        return "ok"

    reply = ask_deepseek(user_message)
    send_telegram_message(chat_id, reply)
    return "ok"

# Запрос к DeepSeek
def ask_deepseek(message):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": message}
        ]
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        logging.info(f"Ответ от DeepSeek: {response.status_code} — {response.text}")

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]

        elif response.status_code == 401:
            return "Ошибка: Неверный API ключ DeepSeek."

        elif response.status_code == 429:
            return "Ошибка: Превышен лимит запросов к DeepSeek."

        elif response.status_code == 404:
            return "Ошибка: DeepSeek API недоступен или неверный URL."

        else:
            return f"Неизвестная ошибка DeepSeek: {response.status_code}"

    except Exception as e:
        logging.error(f"Исключение при запросе к DeepSeek: {e}")
        return "Произошла ошибка при обращении к DeepSeek."

# Ответ пользователю в Telegram
def send_telegram_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(TELEGRAM_API_URL, json=payload)

# Запуск на Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
