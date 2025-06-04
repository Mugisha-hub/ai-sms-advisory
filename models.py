from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy instance (to be used in app.py)
db = SQLAlchemy()

# Message model definition
class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    phone = Column(String)
    text = Column(Text)
    reply = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tags = Column(String)  # <--- this line is causing the error

    def __repr__(self):
        return f"<Message from {self.phone} at {self.timestamp}>"

# Function to insert a message (replaces previous SQLite version)
def insert_message(phone, text, reply):
    msg = Message(phone=phone, text=text, reply=reply)
    db.session.add(msg)
    db.session.commit()
