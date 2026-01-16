from fastapi import FastAPI, Request
from sms import send_sms
from conversation import get_state, update_state

app = FastAPI()


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/incoming-sms")
async def incoming_sms(request: Request):
    form = await request.form()
    params = dict(form)

    print("=== INNKOMMENDE SMS (TWILIO) ===")
    print("RAW PARAMS:", params)

    raw_phone = params.get("From")
    txt = params.get("Body")

    print("RAW_PHONE:", raw_phone)
    print("TXT:", txt)

    if not raw_phone or not txt:
        print("Mangler nummer eller tekst – ignorerer")
        return {"status": "ignored"}

    phone = raw_phone.strip()
    txt = txt.strip()

    state = get_state(phone)
    step = state["step"]
    data = state["data"]

    print("STEP:", step)
    print("DATA FØR:", data)

    # FØRSTE MELDING
    if step == "start":
        update_state(phone, "problem", {})
        send_sms(
            phone,
            "Hei! 👋 Hva gjelder henvendelsen?"
        )
        return {"status": "started"}

    if step == "problem":
        data["problem"] = txt
        update_state(phone, "adresse", data)
        send_sms(
            phone,
            "Takk. Hvor gjelder dette? (adresse eller område)"
        )
        return {"status": "problem_received"}

    if step == "adresse":
        data["adresse"] = txt
        update_state(phone, "tidspunkt", data)
        send_sms(
            phone,
            "Når trenger du hjelp?\n1️⃣ Akutt\n2️⃣ I dag\n3️⃣ Senere"
        )
        return {"status": "adresse_received"}

    if step == "tidspunkt":
        data["tidspunkt"] = txt
        update_state(phone, "done", data)
        send_sms(
            phone,
            "Takk! Vi tar kontakt straks."
        )
        print("FULL LEAD:", data)
        return {"status": "done"}

    return {"status": "ok"}
