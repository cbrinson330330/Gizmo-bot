
from flask import Flask, request
import requests
import openai

app = Flask(__name__)

VERIFY_TOKEN = "gizmosecret123"
PAGE_ACCESS_TOKEN = "PASTE_YOUR_FACEBOOK_PAGE_TOKEN_HERE"
openai.api_key = "PASTE_YOUR_OPENAI_API_KEY_HERE"

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args["hub.challenge"], 200
        return "Verification token mismatch", 403
    return "GizmoTV Chatbot is running!", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            messaging = entry.get("messaging", [])
            for event in messaging:
                if event.get("message"):
                    sender_id = event["sender"]["id"]
                    message_text = event["message"].get("text")
                    if message_text:
                        reply = ask_chatgpt(message_text)
                        send_message(sender_id, reply)
    return "ok", 200

def ask_chatgpt(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're a helpful but chill assistant for Gizmo TV. Keep it casual, helpful, and sports-fan friendly."},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message["content"].strip()
    except Exception:
        return "Something went wrong—try again!"

def send_message(recipient_id, text):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    auth = {"access_token": PAGE_ACCESS_TOKEN}
    response = requests.post("https://graph.facebook.com/v13.0/me/messages", params=auth, json=payload)
    return response.json()

if __name__ == '__main__':
    app.run(port=5000)
