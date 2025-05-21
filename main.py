import os
import requests
from flask import Flask, request
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_BOT_TOKEN = '8090532343:AAFM3AosXFH6dY6r3ukPq4LWCOS0Gl9G_Xc'
DEEPSEEK_API_KEY = 'sk-65464c1f4d804f77bb6978f06d7d8895'

def ask_deepseek(message):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": message}],
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        logging.info(f"DeepSeek response status: {response.status_code}")
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        elif response.status_code == 401:
            return "Ошибка: Неверный API ключ DeepSeek."
        elif response.status_code == 429:
            return "Ошибка: Превышен лимит DeepSeek API."
        else:
            return f"Неизвестная ошибка DeepSeek: {response.status_code}"
    except Exception as e:
        logging.error(f"DeepSeek Error: {e}")
        return "Произошла ошибка при обращении к DeepSeek."

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, json=data)

@app.route('/')
def index():
    return "Бот работает!"

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    logging.info(f"Получено сообщение от Telegram: {data}")
    try:
        message = data['message']['text']
        chat_id = data['message']['chat']['id']
        reply = ask_deepseek(message)
        send_message(chat_id, reply)
    except Exception as e:
        logging.error(f"Ошибка обработки сообщения: {e}")
        send_message(chat_id, "Произошла ошибка. Попробуйте позже.")
    return 'ok'
