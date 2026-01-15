import os
import requests
from requests.auth import HTTPBasicAuth

FRONT_API_URL = "https://www.pling.as/psk/push.php"

SERVICE_ID = os.getenv("FRONT_SERVICE_ID")
PASSWORD = os.getenv("FRONT_GATEWAY_PASSWORD")
SENDER = os.getenv("SENDER_NUMBER")


def send_sms(to: str, message: str):
    if not SERVICE_ID or not PASSWORD or not SENDER:
        raise ValueError("Manglende Front credentials")

    payload = {
        "serviceid": SERVICE_ID,
        "fromid": SENDER,
        "phoneno": to,
        "txt": message,
    }

    response = requests.post(
        FRONT_API_URL,
        data=payload,  # VIKTIG: data, ikke json
        auth=HTTPBasicAuth(SERVICE_ID, PASSWORD),
        timeout=10,
    )

    print("FRONT RESPONSE:", response.status_code, response.text)

    return response
