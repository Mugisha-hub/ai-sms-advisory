import sqlite3

try:
    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, phone, text, reply, timestamp FROM messages ORDER BY timestamp DESC")
    rows = cursor.fetchall()

    print("📋 Message Log:")
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"📱 Phone: {row[1]}")
        print(f"📝 Text: {row[2]}")
        print(f"🤖 Reply: {row[3]}")
        print(f"🕒 Time: {row[4]}")
        print("-" * 40)

    conn.close()

except Exception as e:
    print("❌ Database error:", str(e))
