from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy instance (to be used in app.py)
db = SQLAlchemy()

# Message model definition
class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(50))
    text = db.Column(db.Text)
    reply = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message from {self.phone} at {self.timestamp}>"

# Function to insert a message (replaces previous SQLite version)
def insert_message(phone, text, reply):
    msg = Message(phone=phone, text=text, reply=reply)
    db.session.add(msg)
    db.session.commit()
