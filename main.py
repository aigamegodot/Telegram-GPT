import os
import logging
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 🔴🔴🔴 ВНИМАНИЕ! КЛЮЧИ ОТКРЫТЫ! НЕ ИСПОЛЬЗОВАТЬ В ПРОДАКШЕНЕ! 🔴🔴🔴
TELEGRAM_TOKEN = "8090532343:AAFM3AosXFH6dY6r3ukPq4LWCOS0Gl9G_Xc"
OPENROUTER_API_KEY = "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"
WEBHOOK_SECRET = "RENDER_SECRET_123!"  # Смените это значение!
# 🔴🔴🔴

MODEL_ID = "google/gemma-7b-it"
MAX_MESSAGE_LENGTH = 4096

def ask_openrouter(prompt: str) -> str:
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
        response = requests.post(url, headers=headers, json=data, timeout=15)
        logging.info(f"OpenRouter статус: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        
        error_messages = {
            401: "Ошибка: Неверный API-ключ OpenRouter.",
            402: "Ошибка: Платёжная проблема!",
            429: "Ошибка: Слишком много запросов.",
        }
        return error_messages.get(response.status_code, f"Ошибка {response.status_code}")

    except requests.exceptions.Timeout:
        return "Ошибка: Таймаут запроса."
    except Exception as e:
        logging.error(f"OpenRouter ошибка: {str(e)}")
        return "Ошибка обработки запроса."

def send_message(chat_id: int, text: str) -> None:
    truncated_text = text[:MAX_MESSAGE_LENGTH]
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": truncated_text}
    
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logging.error(f"Ошибка отправки: {str(e)}")

@app.route('/')
def home():
    return "Бот активен! Используйте Telegram."

@app.route('/', methods=['POST'])
def webhook():
    # Проверка секретного токена
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != WEBHOOK_SECRET:
        logging.warning("Попытка взлома!")
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json()
    
    try:
        message = data['message']
        chat_id = message['chat']['id']
        
        if 'text' not in message:
            send_message(chat_id, "Только текст!")
            return jsonify({"status": "ignored"}), 200
            
        user_message = message['text']
        reply = ask_openrouter(user_message)
        send_message(chat_id, reply)

    except KeyError as e:
        logging.error(f"Ошибка формата: {str(e)}")
        return jsonify({"status": "bad request"}), 400
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        send_message(chat_id, "Внутренняя ошибка!")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
