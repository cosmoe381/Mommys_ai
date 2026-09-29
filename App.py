from flask import Flask, request
import os, requests
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))

@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    try:
        # get message text
        msg_data = data.get('messageData', {})
        if 'textMessageData' in msg_data:
            text = msg_data['textMessageData']['textMessage']
        elif 'extendedTextMessageData' in msg_data:
            text = msg_data['extendedTextMessageData']['text']
        else:
            return 'ok', 200

        chat_id = data['senderData']['chatId']

        # ignore your own messages
        if data['senderData'].get('sender') == data.get('instanceData', {}).get('wid', ''):
            return 'ok', 200

        # ask Mommy's AI
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Mommy's AI, for a Grade 12 SA learner. Subjects: Life Sciences, Physical Sciences, Geography, English. Keep answers short, low-data, NSC style. Be supportive."},
                {"role": "user", "content": text}
            ]
        )
        answer = resp.choices[0].message.content

        # send back via Green API
        green_id = os.environ.get("GREEN_ID")
        green_token = os.environ.get("GREEN_TOKEN")
        url = f"https://7107.api.greenapi.com/waInstance{green_id}/sendMessage/{green_token}"
        requests.post(url, json={"chatId": chat_id, "message": answer})

    except Exception as e:
        print(e)
    return 'ok', 200

@app.route('/')
def home():
    return "Mommy's AI is running 24/7"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
