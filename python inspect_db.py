import sqlite3

try:
    conn = sqlite3.connect("messages.db")
    cursor = conn.cursor()

    # Query to get table schema
    cursor.execute("PRAGMA table_info(messages)")
    columns = cursor.fetchall()

    print("📄 Table 'messages' columns:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")

    conn.close()

except Exception as e:
    print("❌ Error inspecting database:", str(e))
