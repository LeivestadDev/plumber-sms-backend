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

    print("=== INNKOMMENDE SMS ===")
    print("RAW PARAMS:", params)

    # Front kan sende enten phonern eller fromid
    raw_phone = params.get("phonern") or params.get("fromid")
    txt = params.get("txt")

    print("RAW_PHONE:", raw_phone)
    print("TXT:", txt)

    if not raw_phone or not txt:
        print("Mangler nummer eller tekst – ignorerer")
        return {"status": "ignored"}

    # Normaliser nummer til +47...
    if raw_phone.startswith("00"):
        phone = "+" + raw_phone[2:]
    elif raw_phone.startswith("+"):
        phone = raw_phone
    else:
        phone = "+" + raw_phone

    print("NORMALISERT NUMMER:", phone)

    # Hent samtalestatus
    state = get_state(phone)
    step = state["step"]
    data = state["data"]

    print("STEP:", step)
    print("DATA FØR:", data)

    # Samtaleflyt
    if step == "problem":
        data["problem"] = txt
        update_state(phone, "adresse", data)

        send_sms(
            phone,
            "Takk. Hvor gjelder dette? (adresse eller område)"
        )

    elif step == "adresse":
        data["adresse"] = txt
        update_state(phone, "tidspunkt", data)

        send_sms(
            phone,
            "Når trenger du hjelp?\n1️⃣ Akutt\n2️⃣ I dag\n3️⃣ Senere"
        )

    elif step == "tidspunkt":
        data["tidspunkt"] = txt
        update_state(phone, "done", data)

        send_sms(
            phone,
            "Takk! Vi tar kontakt straks."
        )

        print("FULL LEAD:", data)

    else:
        # fallback hvis state er ukjent
        update_state(phone, "problem", {})
        send_sms(
            phone,
            "Hei! Hva gjelder henvendelsen?"
        )

    return {"status": "ok"}
