import os
import logging
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Константы — твои ключи
TELEGRAM_TOKEN = "8090532343:AAFM3AosXFH6dY6r3ukPq4LWCOS0Gl9G_Xc"
DEEPSEEK_API_KEY = "sk-65464c1f4d804f77bb6978f06d7d8895"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# Функция запроса к DeepSeek
def ask_deepseek(prompt: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(DEEPSEEK_URL, headers=headers, json=data)
        logging.info(f"DeepSeek status: {response.status_code}")

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "Ошибка: Неверный API-ключ DeepSeek."
        elif response.status_code == 429:
            return "Ошибка: Превышен лимит использования DeepSeek."
        elif response.status_code == 404:
            return "Ошибка: DeepSeek API не найден. Проверь URL или модель."
        else:
            return f"Неизвестная ошибка DeepSeek: {response.status_code}\n{response.text}"

    except Exception as e:
        logging.error(f"DeepSeek Error: {e}")
        return "Произошла ошибка при обращении к DeepSeek."

# Функция отправки сообщения в Telegram
def send_message(chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=payload)
        logging.info(f"Telegram response: {response.status_code}")
    except Exception as e:
        logging.error(f"Telegram send_message error: {e}")

# Тестовая страница
@app.route("/", methods=["GET"])
def home():
    return "Бот работает. Отправьте сообщение в Telegram."

# Основной обработчик Webhook
@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        logging.info(f"Получено сообщение: {data}")

        if "message" not in data or "text" not in data["message"]:
            return jsonify({"status": "no valid message"}), 200

        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"]["text"]

        reply = ask_deepseek(user_message)
        send_message(chat_id, reply)

    except Exception as e:
        logging.error(f"Ошибка обработки запроса: {e}")
        return jsonify({"status": "error", "detail": str(e)}), 500

    return jsonify({"status": "ok"}), 200
