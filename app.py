from flask import Flask, request, jsonify
import africastalking
import os
from dotenv import load_dotenv
from transformers import pipeline
import torch
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

# Load translation model once
print("⏳ Loading NLLB model...")
device = 0 if torch.cuda.is_available() else -1
translator = pipeline("translation", model="facebook/nllb-200-distilled-600M", device=device)
print("✅ NLLB loaded.")

# Memory store for testing (you can later connect to SQLite or Supabase)
recent_messages = []

@app.route("/sms", methods=["POST"])
def receive_sms():
    sender = request.values.get("from", "").strip()
    message = request.values.get("text", "").strip()
    print(f"📩 SMS from {sender}: {message}")

    if not sender or not message:
        return "Bad Request", 400

    try:
        # Translate Kinyarwanda ➜ English
        translated_in = translator(message, src_lang="kin_Latn", tgt_lang="eng_Latn")[0]['translation_text']
        print("🔤 Translated input:", translated_in)

        # Generate response with Cohere
        prompt = f"You are an agriculture advisor. Answer briefly and clearly: {translated_in}"
        response = co.generate(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=100,
            temperature=0.5,
        )
        english_reply = response.generations[0].text.strip()
        print("🤖 Cohere reply:", english_reply)

        # Translate English ➜ Kinyarwanda
        translated_out = translator(english_reply, src_lang="eng_Latn", tgt_lang="kin_Latn")[0]['translation_text']
        reply_text = translated_out
        print("🔁 Final reply:", reply_text)

    except Exception as e:
        print("❌ AI or translation error:", str(e))
        reply_text = "Mbabarira, sinashoboye kumva ikibazo cyawe neza. Ongera ugerageze."

    try:
        sms_response = sms.send(reply_text, [sender])
        print("✅ SMS sent:", sms_response)
    except Exception as e:
        print("❌ SMS error:", str(e))

    # Log message
    recent_messages.append({
        "from": sender,
        "input": message,
        "translated": translated_in if 'translated_in' in locals() else "—",
        "response": reply_text
    })

    return "OK", 200

@app.route("/")
def index():
    return "✅ AI SMS Advisor with Cohere is running."

@app.route("/dashboard")
def dashboard():
    return jsonify(recent_messages[-10:])  # Show last 10 messages

if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server running on port {port}...")
    serve(app, host="0.0.0.0", port=port)
