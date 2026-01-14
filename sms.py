import os
import requests

FRONT_API_URL = "https://www.pling.as/psk/push.php"

SERVICE_ID = os.getenv("FRONT_SERVICE_ID")
PASSWORD = os.getenv("FRONT_GATEWAY_PASSWORD")
SENDER = os.getenv("SENDER_NUMBER")

def send_sms(to: str, message: str):
    if not SERVICE_ID or not PASSWORD or not SENDER:
        raise ValueError("Front credentials mangler i environment variables")

    payload = {
        "serviceid": SERVICE_ID,
        "password": PASSWORD,
        "fromid": SENDER,
        "phoneno": to,
        "txt": message,
        "unicode": False
    }

    response = requests.post(
        FRONT_API_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )

    # VIKTIG: logg responsen
    print("Front status:", response.status_code)
    print("Front response:", response.text)

    response.raise_for_status()
