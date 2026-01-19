from fastapi import FastAPI, Request
import os
from twilio.rest import Client

app = FastAPI()

# ========= ENV =========
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")

PLUMBER_PHONE = os.getenv("PLUMBER_PHONE")

CALENDLY_LINK = "https://calendly.com/svardirekte/befaring-rorleggerhjelp"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ========= STATE =========
STATE = {}

def send_sms(to, msg):
    client.messages.create(
        from_=TWILIO_NUMBER,
        to=to,
        body=msg
    )

def is_akutt(text):
    text = text.lower()
    return any(word in text for word in [
        "akutt", "1", "nå", "med en gang", "haste", "haster", "lekkasje"
    ])

@app.post("/incoming-sms")
async def incoming_sms(request: Request):
    form = await request.form()
    from_phone = form.get("From")
    txt = form.get("Body")

    if not from_phone or not txt:
        return {"status": "ignored"}

    txt = txt.strip()

    state = STATE.get(from_phone, {"step": "start", "data": {}})
    step = state["step"]
    data = state["data"]

    # === START ===
    if step == "start":
        STATE[from_phone] = {"step": "problem", "data": {}}
        send_sms(from_phone, "Hei! Hva kan vi hjelpe deg med i dag?")
        return {"status": "ok"}

    # === PROBLEM ===
    if step == "problem":
        data["problem"] = txt

        if is_akutt(txt):
            send_sms(
                PLUMBER_PHONE,
                "🚨 AKUTT OPPDRAG\n\n"
                f"📞 {from_phone}\n"
                f"❗ {data['problem']}"
            )
            send_sms(
                from_phone,
                "🚨 Dette er registrert som akutt. Rørlegger er varslet."
            )
            STATE.pop(from_phone, None)
            return {"status": "ok"}

        STATE[from_phone] = {"step": "adresse", "data": data}
        send_sms(from_phone, "Hvor gjelder dette? (adresse)")
        return {"status": "ok"}

    # === ADRESSE ===
    if step == "adresse":
        data["adresse"] = txt
        STATE[from_phone] = {"step": "tidspunkt", "data": data}
        send_sms(
            from_phone,
            "Når trenger du hjelp?\n\n"
            "Skriv f.eks:\n"
            "• i dag\n"
            "• senere\n"
            "• 1 = akutt"
        )
        return {"status": "ok"}

    # === TIDSPUNKT ===
    if step == "tidspunkt":
        data["tidspunkt"] = txt

        send_sms(
            PLUMBER_PHONE,
            "📩 NY FORESPØRSEL\n\n"
            f"📞 {from_phone}\n"
            f"❗ {data['problem']}\n"
            f"📍 {data['adresse']}\n"
            f"⏰ {data['tidspunkt']}"
        )

        send_sms(
            from_phone,
            (
                "Takk! Henvendelsen er sendt videre.\n\n"
                "Ønsker du å booke selv kan du bruke denne lenken:\n"
                "https://calendly.com/svardirekte/befaring-rorleggerhjelp"
            )
        )

        STATE.pop(from_phone, None)
        return {"status": "ok"}

    # fallback
    STATE.pop(from_phone, None)
    send_sms(from_phone, "La oss starte på nytt. Hva kan vi hjelpe deg med?")
    return {"status": "ok"}
