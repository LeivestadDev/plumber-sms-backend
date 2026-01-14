import os
import requests
from requests.auth import HTTPBasicAuth

# Front SMS Gateway endpoint
FRONT_API_URL = "https://www.pling.as/psk/push.php"

# Credentials fra Render Environment Variables
SERVICE_ID = os.getenv("FRONT_SERVICE_ID")
PASSWORD = os.getenv("FRONT_GATEWAY_PASSWORD")

# Avsender (kan være registrert avsendernavn eller nummer)
SENDER = os.getenv("SENDER_NUMBER")

def send_sms(to: str, message: str):
    if not SERVICE_ID or not PASSWORD:
        raise ValueError("Front credentials mangler (SERVICE_ID eller PASSWORD)")

    payload = {
        "serviceid": SERVICE_ID,
        "fromid": SENDER,
        "phoneno": to,
        "txt": message,
        "unicode": False
    }

    response = requests.post(
        FRONT_API_URL,
        json=payload,
        auth=HTTPBasicAuth(SERVICE_ID, PASSWORD),
        headers={"Content-Type": "application/json"},
        timeout=10
    )

    # Hvis Front svarer
