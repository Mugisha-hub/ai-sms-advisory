from flask import Flask, request
import africastalking
import cohere
import os

app = Flask(__name__)

# Africa's Talking credentials
username = os.getenv("AT_USERNAME", "sandbox")
at_api_key = os.getenv("AT_API_KEY", "atsk_4c10fd7d07e3bab2f0bfc4ee5f195ef0e6fb629343bbaf669cd18be67e302a9f71f08f0b")
africastalking.initialize(username, at_api_key)
sms = africastalking.SMS

# Cohere credentials
cohere_api_key = os.getenv("COHERE_API_KEY", "DGd7ASeNFpOTBHffl8Gm4x1SQjhM3vS046mnhC3D")
co = cohere.Client(cohere_api_key)

@app.route('/sms', methods=['POST'])
def receive_sms():
    phone_number = request.values.get('from', '').strip()
    text = request.values.get('text', '').strip()

    # Fix the phone number format
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number

    print(f"Received from {phone_number}: {text}")

    # Generate AI reply from Cohere (or fallback)
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

    # Send SMS
    try:
        sms.send(ai_reply, [phone_number])
    except Exception as e:
        print("SMS Send Error:", e)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(debug=True, host="0.0.0.0", port=port)
