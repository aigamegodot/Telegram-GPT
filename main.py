import os
import requests
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHATGPT_API_KEY = os.environ['CHATGPT_API_KEY']
URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def ask_chatgpt(prompt):
    headers = {
        "Authorization": f"Bearer {CHATGPT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']

@app.route('/', methods=["POST"])
def webhook():
    data = request.get_json()
    message = data["message"]["text"]
    chat_id = data["message"]["chat"]["id"]

    reply = ask_chatgpt(message)

    payload = {
        "chat_id": chat_id,
        "text": reply
    }
    requests.post(URL, json=payload)
    return {"ok": True}

@app.route('/')
def home():
    return 'Bot is running!'
