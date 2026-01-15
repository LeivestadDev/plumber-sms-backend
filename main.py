from fastapi import FastAPI, Request
from sms import send_sms

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/incoming-sms")
def incoming_sms(request: Request):
    params = dict(request.query_params)

    print("INNKOMMENDE SMS MOTTATT")
    print("DATA:", params)

    return {"status": "received"}

