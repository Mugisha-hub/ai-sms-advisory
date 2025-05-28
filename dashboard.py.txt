from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_messages():
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute("SELECT phone, text, reply, timestamp FROM messages ORDER BY timestamp DESC")
    messages = cursor.fetchall()
    conn.close()
    return messages

@app.route("/dashboard")
def dashboard():
    messages = get_messages()
    return render_template("dashboard.html", messages=messages)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
