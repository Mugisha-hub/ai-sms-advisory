import africastalking

username = "sandbox"
api_key = "atsk_da9f3e81061190e4275f34346dc36f5efcc115092e3357bb23f381d9c3ac73e10bc2f48c"  # Paste your real key here

africastalking.initialize(username, api_key)
sms = africastalking.SMS

def send_sms():
    recipients = ["+250788615868"]  # Your test phone number
    message = "Hello from AI Agri Advisor!"

    try:
        response = sms.send(message, recipients)
        print(response)
    except Exception as e:
        print(f"Error sending SMS: {e}")

send_sms()
