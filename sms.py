import os
from twilio.rest import Client

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_NUMBER")

client = Client(account_sid, auth_token)

def send_sms(to: str, message: str):
    msg = client.messages.create(
        to=to,
        from_=from_number,
        body=message
    )
    print("TWILIO MESSAGE SID:", msg.sid)
