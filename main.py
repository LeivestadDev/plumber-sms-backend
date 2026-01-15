from fastapi import FastAPI, Request
from sms import send_sms
from conversation import get_state, update_state

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/incoming-sms")
def incoming_sms(request: Request):
    params = dict(request.query_params)

    print("INNKOMMENDE SMS MOTTATT")
    print("DATA:", params)

    raw_phone = params.get("phonern")
    txt = params.get("txt")

    if not raw_phone or not txt:
        return {"status": "ignored"}

    if raw_phone.startswith("00"):
        phonern = "+" + raw_phone[2:]
    else:
        phonern = raw_phone

    print("NORMALISERT NUMMER:", phonern)
    update_state(phonern, "start", {})


    state = get_state(phonern)
    step = state["step"]
    data = state["data"]

    if step == "start":
        update_state(phonern, "problem", {})
        send_sms(
            phonern,
            "Hei! Hva gjelder henvendelsen?"
        )
        return {"status": "started"}

    if step == "problem":
        data["problem"] = txt
        update_state(phonern, "adresse", data)

        send_sms(
            phonern,
            "Takk. Hvor gjelder dette? (adresse eller område)"
        )

    elif step == "adresse":
        data["adresse"] = txt
        update_state(phonern, "tidspunkt", data)

        send_sms(
            phonern,
            "Når trenger du hjelp?\n1️⃣ Akutt\n2️⃣ I dag\n3️⃣ Senere"
        )

    elif step == "tidspunkt":
        data["tidspunkt"] = txt
        update_state(phonern, "done", data)

        send_sms(
            phonern,
            "Takk! Book tidspunkt her: https://calendly.com/DITT-LENKE"
        )

        print("FULL LEAD:", data)

    return {"status": "ok"}



