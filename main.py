from fastapi import FastAPI, Request
from sms import send_sms

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}
