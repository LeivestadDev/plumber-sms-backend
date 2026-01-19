from fastapi import FastAPI, Request
from twilio.rest import Client
import os

app = FastAPI()

# =========================
# ENV / TWILIO
# =========================
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# =========================
# MIDLERLIG STATE (kan byttes til DB senere)
# =========================
STATE = {}

def get_state(phone):
    return STATE.get(phone, {
        "step": "start",
        "data": {}
    })

def update_state(phone, step, data):
    STATE[phone] = {
        "step": step,
        "data": data
    }

def clear_state(phone):
    if phone in STATE:
        del STATE[phone]

# =========================
# SMS SENDER
# =========================
def send_sms(to, message):
    client.messages.create(
        from_=TWILIO_NUMBER,
        to=to,
        body=message
    )

# =========================
# AKUTT DETEKSJON
# =========================
def is_acute(txt):
    keywords = [
        "akutt", "haste", "nødhjelp", "krise",
        "lekkasje", "vann overalt", "sprukket rør"
    ]
    return txt == "1" or any(word in txt for word in keywords)

# =========================
# WEBHOOK
# =========================
@app.post("/incoming-sms")
async def incoming_sms(request: Request):
    form = await request.form()
    params = dict(form)

    from_phone = params.get("From")
    txt = params.get("Body")

    print("=== INNKOMMENDE SMS ===")
    print("FROM:", from_phone)
    print("TXT:", txt)

    if not from_phone or not txt:
        return {"status": "ignored"}

    txt = txt.strip().lower()

    state = get_state(from_phone)
    step = state["step"]
    data = state["data"]

    # =========================
    # START / NY SAMTALE
    # =========================
    if step == "start":
        update_state(from_phone, "problem", {})
        send_sms(
            from_phone,
            "Hei! 👋\nHva kan vi hjelpe deg med i dag?\n\n"
            "Beskriv problemet kort.\n"
            "Skriv *1* eller *akutt* hvis det haster 🚨"
        )
        return {"status": "ok"}

    # =========================
    # AKUTT – FUNKER OVERALT
    # =========================
    if is_acute(txt):
        company = "Rørlegger"
        plumber_phone = os.getenv("PLUMBER_PHONE")

        plumber_msg = (
            f"🚨 AKUTT OPPDRAG – {company}\n\n"
            f"📞 Telefon: {from_phone}\n"
            f"❗ Problem: {data.get('problem', 'Ikke spesifisert')}\n"
            f"📍 Adresse: {data.get('adresse', 'Ukjent')}"
        )

        if plumber_phone:
            send_sms(plumber_phone, plumber_msg)

        send_sms(
            from_phone,
            "🚨 Takk! Dette er registrert som AKUTT.\n"
            "Rørlegger blir varslet umiddelbart."
        )

        clear_state(from_phone)
        return {"status": "ok"}

    # =========================
    # STEG 1 – PROBLEM
    # =========================
    if step == "problem":
        data["problem"] = txt
        update_state(from_phone, "adresse", data)

        send_sms(
            from_phone,
            "Takk 👍\nHva er adressen?"
        )
        return {"status": "ok"}

    # =========================
    # STEG 2 – ADRESSE
    # =========================
    if step == "adresse":
        data["adresse"] = txt
        update_state(from_phone, "tidspunkt", data)

        send_sms(
            from_phone,
            "Når ønsker du hjelp?\n\n"
            "Skriv f.eks:\n"
            "• I dag\n"
            "• I morgen\n"
            "• 1 = Akutt "
        )
        return {"status": "ok"}

    # =========================
    # STEG 3 – TIDSPUNKT
    # =========================
    if step == "tidspunkt":
        data["tidspunkt"] = txt

        company = "Rørlegger"
        plumber_phone = os.getenv("PLUMBER_PHONE")

        plumber_msg = (
            f"📩 AKUTT OPPDRAG 🚨 – {company}\n\n"
            f"📞 Telefon: {from_phone}\n"
            f"❗ Problem: {data['problem']}\n"
            f"📍 Adresse: {data['adresse']}\n"
            f"⏰ Tidspunkt: {data['tidspunkt']}"
        )

        if plumber_phone:
            send_sms(plumber_phone, plumber_msg)

        send_sms(
            from_phone,
            "Takk! 👌\nForespørselen er sendt videre.\n"
            "Du blir kontaktet snart."
        )

        clear_state(from_phone)
        return {"status": "ok"}

    # =========================
    # FALLBACK (SISTE SIKRING)
    # =========================
    update_state(from_phone, "start", {})
    send_sms(
        from_phone,
        "Hei! 👋\nLa oss starte på nytt.\n"
        "Hva kan vi hjelpe deg med?"
    )
    return {"status": "ok"}
