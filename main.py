@app.get("/")
def health():
    return {"status": "ok"}
from sms import send_sms

@app.get("/test-sms")
def test_sms():
    send_sms("+4795330248", "Test fra Front SMS Gateway")
    return {"status": "sent"}

