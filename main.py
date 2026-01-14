from fastapi import FastAPI, Request
from sms import send_sms

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/test-sms")
def test_sms():
    send_sms("+4795330248", "Test fra Front SMS Gateway")
    return {"status": "sent"}
