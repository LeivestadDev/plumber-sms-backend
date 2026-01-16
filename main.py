import os
from fastapi import FastAPI, Request
from sms import send_sms
from conversation import get_state, update_state

app = FastAPI()

# Environment variables
PLUMBER_PHONE = os.getenv("PLUMBER_PHONE")

if not PLUMBER_PHONE:
    print("⚠️ ADVARSEL: PLUMBER_PHONE er ikke satt")

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/incoming-sms")
async def incoming_sms(request: Request):
    # Twilio sender application/x-www-form-urlencoded
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

    # --- START ---
    if step == "start":
        update_state(phone, "problem", {})
        send_sms(
            phone,
            "Hei! 👋 Hva kan vi hjelpe deg med i dag?"
        )
        return {"status": "started"}

    # --- PROBLEM ---
    if step == "problem":
        data["problem"] = txt
        update_state(phone, "adresse", data)
        send_sms(
            phone,
            "Takk! Hvor gjelder dette? (adresse eller område)"
        )
        return {"status": "problem_saved"}

    # --- ADRESSE ---
    if step == "adresse":
        data["adresse"] = txt
        update_state(phone, "tidspunkt", data)
        send_sms(
            phone,
            "Når trenger du hjelp?\n"
            "1️⃣ Akutt\n"
            "2️⃣ I dag\n"
            "3️⃣ Senere"
        )
        return {"status": "adresse_saved"}

    # --- TIDSPUNKT ---
    if step == "tidspunkt":
        data["tidspunkt"] = txt
        update_state(phone, "done", data)

        # Bekreftelse til kunde
        send_sms(
            phone,
            "Supert 👍 Vi har mottatt henvendelsen din og kontakter deg snart."
        )

        # Send lead til rørlegger
        lead_text = (
            "🔧 NYTT OPPDRAG\n\n"
            f"📞 Telefon: {phone}\n"
            f"❗ Problem: {data.get('problem')}\n"
            f"📍 Adresse: {data.get('adresse')}\n"
            f"⏰ Tidspunkt: {data.get('tidspunkt')}"
        )

        send_sms(PLUMBER_PHONE, lead_text)

        print("FERDIG LEAD:", {
            "telefon": phone,
            **data
        })

        return {"status": "completed"}

    # --- DONE ---
    if step == "done":
        send_sms(
            phone,
            "Vi har allerede mottatt henvendelsen 👍"
        )
        return {"status": "already_done"}

    return {"status": "unknown_state"}
