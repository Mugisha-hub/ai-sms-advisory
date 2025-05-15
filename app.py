from flask import Flask, request
import africastalking
import cohere
import os

app = Flask(__name__)

# Africa's Talking config
username = os.getenv("AT_USERNAME", "sandbox")
at_api_key = os.getenv("AT_API_KEY", "atsk_da9f3e81061190e4275f34346dc36f5efcc115092e3357bb23f381d9c3ac73e10bc2f48c")
africastalking.initialize(username, at_api_key)
sms = africastalking.SMS

# Cohere config
cohere_api_key = os.getenv("COHERE_API_KEY", "DGd7ASeNFpOTBHffl8Gm4x1SQjhM3vS046mnhC3D")
co = cohere.Client(cohere_api_key)

@app.route('/sms', methods=['POST'])
def receive_sms():
    phone_number = request.values.get('from', '')
    text = request.values.get('text', '')

    print(f"Received from {phone_number}: {text}")

    # Get AI response from Cohere
    try:
        response = co.generate(
            model='command',
            prompt=f"You are a helpful agriculture advisor. A farmer asks: {text}",
            max_tokens=100,
            temperature=0.7
        )
        ai_reply = response.generations[0].text.strip()
    except Exception as e:
        print("Cohere Error:", e)
        ai_reply = "Sorry, I couldn't generate a response right now."

    # Send SMS reply via Africa's Talking
    try:
        sms.send(ai_reply, [phone_number])
    except Exception as e:
        print("SMS Send Error:", e)

    return "OK", 200
