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
        print("Mangler nummer eller tekst – ignorerer")
        return {"status": "ignored"}

    # Normaliser nummer
    if raw_phone.startswith("00"):
        phonern = "+" + raw_phone[2:]
    else:
        phonern = raw_phone

    print("NORMALISERT NUMMER:", phonern)

    state = get_state(phonern)
    step = state.get("step", "start")
    data = state.get("data", {})

    print("STEP:", step)

    # ---- FLYT ----

    if step == "start":
        update_state(phonern, "problem", {})
        send_sms(
            phonern,
            "Hei! 👋 Hva gjelder henvendelsen?"
        )
        return {"status": "started"}

    if step == "problem":
        data["problem"] = txt
        update_state(phonern, "adresse", data)
        send_sms(
            phonern,
            "Hvor gjelder dette? (adresse eller område)"
        )
        return {"status": "problem_received"}

    if step == "adresse":
        data["adresse"] = txt
        update_state(phonern, "tidspunkt", data)
        send_sms(
            phonern,
            "Når trenger du hjelp?\n1️⃣ Akutt\n2️⃣ I dag\n3️⃣ Senere"
        )
        return {"status": "adresse_received"}

    if step == "tidspunkt":
        data["tidspunkt"] = txt
        update_state(phonern, "done", data)
        send_sms(
            phonern,
            "Takk! Vi tar kontakt veldig snart 👍"
        )
        print("FULL LEAD:", data)
        return {"status": "done"}

    return {"status": "unknown_step"}
