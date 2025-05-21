import os
import logging
import requests
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Токены
TELEGRAM_TOKEN = "8090532343:AAFM3AosXFH6dY6r3ukPq4LWCOS0Gl9G_Xc"
OPENROUTER_API_KEY = "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"
MODEL_ID = "google/gemma-7b-it"  # OpenRouter ID модели (Gemma 3n 4B = 7b-it)

# Обращение к OpenRouter
def ask_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        logging.info(f"OpenRouter статус: {response.status_code}")
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "Ошибка: Неверный API-ключ OpenRouter."
        elif response.status_code == 402:
            return "Ошибка: Платёжная ошибка (возможно закончились кредиты)."
        elif response.status_code == 429:
            return "Ошибка: Слишком много запросов. Подожди немного."
        else:
            return f"Неизвестная ошибка OpenRouter: {response.status_code}"
    except Exception as e:
        logging.error(f"OpenRouter ошибка: {e}")
        return "Ошибка при обращении к OpenRouter."

# Отправка сообщения в Telegram
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=data)
    except Exception as e:
        logging.error(f"Ошибка отправки в Telegram: {e}")

# Главная страница (Render проверяет GET /)
@app.route('/')
def home():
    return "Бот запущен и работает!"

# Основной вебхук
@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    logging.info(f"Получено сообщение от Telegram: {data}")

    try:
        message = data['message']['text']
        chat_id = data['message']['chat']['id']
        reply = ask_openrouter(message)
        send_message(chat_id, reply)
    except Exception as e:
        logging.error(f"Ошибка обработки: {e}")
        try:
            send_message(chat_id, "Ошибка. Попробуй позже.")
        except:
            pass

    return 'ok'

# Запуск сервера
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
