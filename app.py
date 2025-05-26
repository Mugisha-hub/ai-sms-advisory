from flask import Flask, request
import africastalking
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env if running locally
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Africa's Talking credentials
username = os.getenv("AT_USERNAME", "sandbox")
api_key = os.getenv("AFRICASTALKING_API_KEY")

# Initialize Africa's Talking SDK
africastalking.initialize(username, api_key)
sms = africastalking.SMS

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/sms", methods=["POST"])
def receive_sms():
    sender = request.values.get("from")
    message = request.values.get("text")

    print(f"Received message from {sender}: {message}")

    try:
        ai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful agriculture advisor."},
                {"role": "user", "content": message}
            ]
        )
        reply_text = ai_response.choices[0].message.content.strip()
    except Exception as e:
        reply_text = "Sorry, I had trouble understanding your question."
        print("OpenAI error:", str(e))

    try:
        response = sms.send(reply_text, [sender])
        print("Reply sent:", response)
    except Exception as e:
        print("Error sending reply:", str(e))

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
