import requests
from flask import Flask, request
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Вставь свои ключи
TELEGRAM_BOT_TOKEN = "8090532343:AAFM3AosXFH6dY6r3ukPq4LWCOS0Gl9G_Xc"
DEEPSEEK_API_KEY = "sk-65464c1f4d804f77bb6978f06d7d8895"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def ask_deepseek(message_text):
    """Отправка сообщения в DeepSeek и получение ответа."""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",  # Убедись, что модель называется именно так
        "messages": [{"role": "user", "content": message_text}],
        "temperature": 0.7
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        logging.info(f"DeepSeek Status: {response.status_code}")
        logging.info(f"DeepSeek Response: {response.text}")

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]

        elif response.status_code == 401:
            return "Ошибка: Неверный API ключ DeepSeek."

        elif response.status_code == 403:
            return "Ошибка: Доступ к DeepSeek запрещён."

        elif response.status_code == 404:
            return "Ошибка: DeepSeek API не найден (возможно, неверный URL или модель)."

        elif response.status_code == 429:
            return "Ошибка: Превышен лимит использования DeepSeek. Подожди или проверь тариф."

        elif response.status_code == 500:
            return "Ошибка: Внутренняя ошибка сервера DeepSeek."

        else:
            return f"Неизвестная ошибка DeepSeek: {response.status_code} — {response.text}"

    except requests.exceptions.RequestException as e:
        logging.error(f"Сетевая ошибка при запросе к DeepSeek: {e}")
        return f"Сетевая ошибка при обращении к DeepSeek: {e}"

@app.route("/", methods=["GET"])
def index():
    return "DeepSeek Telegram Bot активен!"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Запрос от Telegram: {data}")

    try:
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            user_message = data["message"]["text"]

            reply_text = ask_deepseek(user_message)
            send_message(chat_id, reply_text)
        else:
            logging.warning("Получены данные без текстового сообщения.")
    except Exception as e:
        logging.error(f"Ошибка при обработке webhook: {e}")
    return "ok"

def send_message(chat_id, text):
    """Отправка сообщения пользователю в Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        response = requests.post(url, json=payload)
        logging.info(f"Отправка сообщения Telegram: {response.status_code}")
    except Exception as e:
        logging.error(f"Ошибка отправки в Telegram: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
