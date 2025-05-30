from flask import Flask, request, render_template, redirect, url_for, session
import africastalking
import os
from dotenv import load_dotenv
import cohere
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

# Africa's Talking setup
username = os.getenv("AT_USERNAME", "sandbox")
api_key = os.getenv("AFRICASTALKING_API_KEY")
africastalking.initialize(username, api_key)
sms = africastalking.SMS

# Cohere setup
co = cohere.Client(os.getenv("COHERE_API_KEY"))

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL connection string
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String)
    text = Column(Text)
    reply = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def insert_message(phone, text, reply):
    db = SessionLocal()
    msg = Message(phone=phone, text=text, reply=reply)
    db.add(msg)
    db.commit()
    db.close()

@app.route("/sms", methods=["POST"])
def receive_sms():
    sender = request.values.get("from", "").strip()
    message = request.values.get("text", "").strip()
    print(f"📩 SMS from {sender}: {message}")

    if not sender or not message:
        return "Bad Request", 400

    try:
        prompt = f"You are an agriculture advisor. Answer briefly and clearly: {message}"
        response = co.generate(model="command-r-plus", prompt=prompt, max_tokens=100, temperature=0.5)
        reply_text = response.generations[0].text.strip()
        print("🤖 Reply:", reply_text)
    except Exception as e:
        print("❌ AI error:", str(e))
        reply_text = "Sorry, I couldn't process your question. Please try again."

    try:
        sms.send(reply_text, [sender])
    except Exception as e:
        print("❌ SMS error:", str(e))

    try:
        insert_message(sender, message, reply_text)
    except Exception as e:
        print("❌ DB error:", str(e))

    return "OK", 200

@app.route("/")
def index():
    return "✅ AI SMS Advisor with Cohere is running."

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == os.getenv("DASHBOARD_PASSWORD", "farmer123"):
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        return "Incorrect password", 403
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    phone = request.args.get("phone", "").strip()
    keyword = request.args.get("keyword", "").strip()
    date = request.args.get("date", "").strip()

    db = SessionLocal()
    query = db.query(Message)

    if phone:
        query = query.filter(Message.phone.ilike(f"%{phone}%"))
    if keyword:
        query = query.filter((Message.text.ilike(f"%{keyword}%")) | (Message.reply.ilike(f"%{keyword}%")))
    if date:
        query = query.filter(func.date(Message.timestamp) == date)

    messages = query.order_by(Message.timestamp.desc()).all()
    db.close()
    return render_template("dashboard.html", messages=messages)

@app.route("/analytics")
def analytics():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    db = SessionLocal()

    try:
        total_messages = db.query(func.count(Message.id)).scalar()
        unique_senders = db.query(func.count(func.distinct(Message.phone))).scalar()
        messages_per_day = db.query(func.date(Message.timestamp), func.count(Message.id))\
                             .group_by(func.date(Message.timestamp))\
                             .order_by(func.date(Message.timestamp).desc())\
                             .limit(7)\
                             .all()
        db.close()

        return render_template("analytics.html",
                               total_messages=total_messages,
                               unique_senders=unique_senders,
                               messages_per_day=messages_per_day)
    except Exception as e:
        db.close()
        return f"Analytics error: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
