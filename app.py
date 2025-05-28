from flask import Flask, request
import africastalking
import os
from dotenv import load_dotenv
import cohere

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)

# Africa's Talking setup
username = os.getenv("AT_USERNAME", "sandbox")
api_key = os.getenv("AFRICASTALKING_API_KEY")
africastalking.initialize(username, api_key)
sms = africastalking.SMS

# Cohere setup
co = cohere.Client(os.getenv("COHERE_API_KEY"))

@app.route("/sms", methods=["POST"])
def receive_sms():
    sender = request.values.get("from", "").strip()
    message = request.values.get("text", "").strip()

    print(f"📩 SMS from {sender}: {message}")

    if not sender or not message:
        return "Bad Request", 400

    try:
        # Generate response with Cohere
        prompt = f"You are an agriculture advisor. Answer briefly and clearly: {message}"
        response = co.generate(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=100,
            temperature=0.5,
        )
        reply_text = response.generations[0].text.strip()
        print("🤖 Reply:", reply_text)

    except Exception as e:
        print("❌ AI error:", str(e))
        reply_text = "Sorry, I couldn't process your question. Please try again."

    try:
        sms_response = sms.send(reply_text, [sender])
        print("✅ SMS sent:", sms_response)
    except Exception as e:
        print("❌ SMS error:", str(e))

    return "OK", 200

@app.route("/")
def index():
    return "✅ AI SMS Advisor with Cohere is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
