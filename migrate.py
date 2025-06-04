from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as connection:
    connection.execute(text("ALTER TABLE messages ADD COLUMN tags TEXT;"))
    print("✅ Tags column added!")
