from flask import Flask, request, render_template, redirect, url_for, session
import africastalking
import os
from dotenv import load_dotenv
import cohere
import sqlite3
from models import insert_message  # ✅ Import your database function

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")  # 🔐 Required for session handling

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

    # ✅ Log the message to the database
    try:
        insert_message(sender, message, reply_text)
    except Exception as e:
        print("❌ DB error:", str(e))

    return "OK", 200

@app.route("/")
def index():
    return "✅ AI SMS Advisor with Cohere is running."

# 🔐 Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == os.getenv("DASHBOARD_PASSWORD", "farmer123"):
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        return "Incorrect password", 403
    return render_template("login.html")

# 📊 Dashboard route with filtering
@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    phone = request.args.get("phone", "").strip()
    keyword = request.args.get("keyword", "").strip()
    date = request.args.get("date", "").strip()

    query = "SELECT * FROM messages WHERE 1=1"
    params = []

    if phone:
        query += " AND phone LIKE ?"
        params.append(f"%{phone}%")

    if keyword:
        query += " AND (text LIKE ? OR reply LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    if date:
        query += " AND DATE(timestamp) = ?"
        params.append(date)

    query += " ORDER BY timestamp DESC"

    try:
        conn = sqlite3.connect("messages.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return render_template("dashboard.html", messages=rows)
    except Exception as e:
        return f"Database error: {e}", 500

    
@app.route("/analytics")
def analytics():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    try:
        conn = sqlite3.connect("messages.db")
        cur = conn.cursor()

        # Total messages
        cur.execute("SELECT COUNT(*) FROM messages")
        total_messages = cur.fetchone()[0]

        # Unique senders
        cur.execute("SELECT COUNT(DISTINCT phone) FROM messages")
        unique_senders = cur.fetchone()[0]

        # Messages per day
        cur.execute("""
            SELECT DATE(timestamp) as day, COUNT(*) as count
            FROM messages
            GROUP BY day
            ORDER BY day DESC
            LIMIT 7
        """)
        messages_per_day = cur.fetchall()

        conn.close()

        return render_template("analytics.html",
                               total_messages=total_messages,
                               unique_senders=unique_senders,
                               messages_per_day=messages_per_day)
    except Exception as e:
        return f"Analytics error: {e}", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
