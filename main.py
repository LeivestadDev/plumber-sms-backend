from fastapi import FastAPI, Request
from twilio.rest import Client
import os

app = FastAPI()

# =========================
# TWILIO
# =========================
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
PLUMBER_PHONE = os.getenv("PLUMBER_PHONE")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# =========================
# STATE (midlertidig)
# =========================
STATE = {}

def get_state(phone):
    return STATE.get(phone, {"step": "start", "data": {}})

def set_state(phone, step, data):
    STATE[phone] = {"step": step, "data": data}

def clear_state(phone):
    STATE.pop(phone, None)

# =========================
# SMS
# =========================
def send_sms(to, msg):
    client.messages.create(
        from_=TWILIO_NUMBER,
        to=to,
        body=msg
    )

# =========================
# AKUTT DETEKSJON
# =========================
def is_acute(txt):
    txt = txt.lower()
    keywords = [
        "akutt", "haste", "nødhjelp",
        "lekkasje", "vann", "sprukket"
    ]
    return txt == "1" or any(k in txt for k in keywords)

# =========================
# WEBHOOK
# =========================
@app.post("/incoming-sms")
async def incoming_sms(request: Request):
    form = await request.form()
    params = dict(form)

    from_phone = params.get("From")
    txt = params.get("Body")

    if not from_phone or not txt:
        return {"status": "ignored"}

    txt = txt.strip()
    txt_lower = txt.lower()

    state = get_state(from_phone)
    step = state["step"]
    data = state["data"]

    print("SMS:", from_phone, txt, step)

    # =========================
    # AKUTT – ALLTID PRIORITERT
    # =========================
    if is_acute(txt_lower):
        plumber_msg = (
            "🚨 AKUTT OPPDRAG\n\n"
            f"📞 Telefon: {from_phone}\n"
            f"❗ Problem: {data.get('problem', 'Ikke oppgitt')}\n"
            f"📍 Adresse: {data.get('adresse', 'Ikke oppgitt')}"
        )

        if PLUMBER_PHONE:
            send_sms(PLUMBER_PHONE, plumber_msg)

        send_sms(
            from_phone,
            "🚨 Dette er registrert som AKUTT.\n"
            "Rørlegger er varslet umiddelbart."
        )

        clear_state(from_phone)
        return {"status": "ok"}

    # =========================
    # START
    # =========================
    if step == "start":
        set_state(from_phone, "problem", {})
        send_sms(
            from_phone,
            "Hei! 👋\nHva kan vi hjelpe deg med i dag?"
        )
        return {"status": "ok"}

    # =========================
    # PROBLEM
    # =========================
    if step == "problem":
        data["problem"] = txt
        set_state(from_phone, "adresse", data)

        send_sms(
            from_phone,
            "Takk 👍\nHvor gjelder dette? (adresse)"
        )
        return {"status": "ok"}

    # =========================
    # ADRESSE
    # =========================
    if step == "adresse":
        data["adresse"] = txt
        set_state(from_phone, "tidspunkt", data)

        send_sms(
            from_phone,
            "Når trenger du hjelp?\n\n"
            "Eksempel:\n"
            "• I dag\n"
            "• I morgen\n"
            "• 1 = Akutt 🚨"
        )
        return {"status": "ok"}

    # =========================
    # TIDSPUNKT
    # =========================
    if step == "tidspunkt":
        data["tidspunkt"] = txt

        plumber_msg = (
            "📩 NY FORESPØRSEL\n\n"
            f"📞 Telefon: {from_phone}\n"
            f"❗ Problem: {data['problem']}\n"
            f"📍 Adresse: {data['adresse']}\n"
            f"⏰ Når: {data['tidspunkt']}"
        )

        if PLUMBER_PHONE:
            send_sms(PLUMBER_PHONE, plumber_msg)

        send_sms(
            from_phone,
            "Takk! 👌\nForespørselen er sendt videre.\n"
            "Du blir kontaktet snart."
        )

        clear_state(from_phone)
        return {"status": "ok"}

    # =========================
    # SIKKER FALLBACK
    # =========================
    clear_state(from_phone)
    send_sms(
        from_phone,
        "Hei! 👋\nLa oss starte på nytt.\nHva kan vi hjelpe deg med?"
    )
    return {"status": "ok"}
