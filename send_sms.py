import africastalking

# Initialize
username = "sandbox"  # Use 'sandbox' for testing
api_key = "atsk_2fcfbda6154e6871153dbbe329df056eafb268bf09fd0ff9d75c793baaa69af1ee65b765"  # Replace with your sandbox or production key
africastalking.initialize(username, api_key)

sms = africastalking.SMS

# Send SMS
try:
    response = sms.send("Hello from Africa's Talking!", ["+250788615868"])
    print(response)
except Exception as e:
    print(f"Error: {e}")

