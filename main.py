from fastapi import FastAPI, Request
import os
from twilio.rest import Client

app = FastAPI()

# ===== ENV =====
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
PLUMBER_PHONE = os.getenv("PLUMBER_PHONE")

CALENDLY_LINK = "https://calendly.com/svardirekte/befaring-rorleggerhjelp"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ===== STATE =====
STATE = {}

def send_sms(to, msg):
    client.messages.create(
        from_=TWILIO_NUMBER,
        to=to,
        body=msg
    )

def is_akutt(text):
    text = text.lower()
    return text in ["1", "akutt"]

def is_ikke_akutt(text):
    text = text.lower()
    return text in ["2", "3", "i dag", "idag", "senere"]

@app.post("/incoming-sms")
async def incoming_sms(request: Request):
    form = await request.form()
    from_phone = form.get("From")
    txt = form.get("Body")

    if not from_phone or not txt:
        return {"status": "ignored"}

    txt = txt.strip()

    state = STATE.get(from_phone)

    # ===== START =====
    if not state:
        STATE[from_phone] = {
            "step": "problem",
            "data": {}
        }
        send_sms(from_phone, "Hei! Hva kan vi hjelpe deg med i dag?")
        return {"status": "ok"}

    step = state["step"]
    data = state["data"]

    # ===== PROBLEM =====
    if step == "problem":
        data["problem"] = txt
        STATE[from_phone]["step"] = "adresse"
        send_sms(from_phone, "Hvor gjelder dette? (adresse)")
        return {"status": "ok"}

    # ===== ADRESSE =====
    if step == "adresse":
        data["adresse"] = txt
        STATE[from_phone]["step"] = "tidspunkt"
        send_sms(
            from_phone,
            "Når trenger du hjelp?\n\n"
            "1 = Akutt\n"
            "2 = I dag\n"
            "3 = Senere"
        )
        return {"status": "ok"}

    # ===== TIDSPUNKT =====
    if step == "tidspunkt":
        data["tidspunkt"] = txt.lower()

        # 🔴 AKUTT
        if is_akutt(txt):
            send_sms(
                PLUMBER_PHONE,
                "🚨 AKUTT OPPDRAG\n\n"
                f"📞 {from_phone}\n"
                f"❗ {data['problem']}\n"
                f"📍 {data['adresse']}"
            )
            send_sms(
                from_phone,
                "🚨 Dette er registrert som akutt. Rørlegger er varslet."
            )
            STATE.pop(from_phone, None)
            return {"status": "ok"}

        # 🟢 IKKE AKUTT → CALENDLY
        if is_ikke_akutt(txt):
            send_sms(
                from_phone,
                (
                    "Takk! Henvendelsen er mottatt.\n\n"
                    "Du kan selv velge tidspunkt her:\n"
                    "https://calendly.com/svardirekte/befaring-rorleggerhjelp"
                )
            )
            STATE.pop(from_phone, None)
            return {"status": "ok"}

        # ⚠️ UKJENT SVAR
        send_sms(
            from_phone,
            "Jeg forsto ikke svaret.\n\n"
            "Svar med:\n"
            "1 = Akutt\n"
            "2 = I dag\n"
            "3 = Senere"
        )
        return {"status": "ok"}
