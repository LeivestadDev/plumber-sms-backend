from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import os

app = FastAPI()

# ===== KONFIG =====
PLUMBER_PHONE = os.getenv("PLUMBER_PHONE")  # f.eks +479XXXXXXXX
CALENDLY_LINK = os.getenv("CALENDLY_LINK")  # https://calendly.com/...
FROM_SMS = os.getenv("FROM_SMS")            # Twilio-nummeret ditt

# ===== ENKEL IN-MEMORY SESSION (OK FOR MVP) =====
sessions = {}

# ===== SMS SENDER =====
def send_sms(to, body):
    from twilio.rest import Client
    client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_AUTH"))
    client.messages.create(
        to=to,
        from_=FROM_SMS,
        body=body
    )

# ===== HJELPEFUNKSJONER =====
def is_akutt(text: str) -> bool:
    text = text.lower()
    akutt_ord = [
        "akutt", "nå", "med en gang", "straks", "haste",
        "1", "haster", "snarest"
    ]
    return any(word in text for word in akutt_ord)

def is_later(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in ["senere", "i dag", "idag", "imorgen", "morgen"])

# ===== WEBHOOK =====
@app.post("/incoming-sms")
async def incoming_sms(request: Request):
    form = await request.form()
    params = dict(form)

    from_phone = params.get("From")
    txt = params.get("Body")

    if not from_phone or not txt:
        return PlainTextResponse("")

    txt = txt.strip()

    # start ny session hvis ikke finnes
    if from_phone not in sessions:
        sessions[from_phone] = {
            "step": "problem",
            "problem": None,
            "adresse": None,
            "tidspunkt": None
        }

        send_sms(
            from_phone,
            "Hei! 👋\nHva kan vi hjelpe deg med i dag?"
        )
        return PlainTextResponse("")

    session = sessions[from_phone]

    # ===== STEG 1: PROBLEM =====
    if session["step"] == "problem":
        session["problem"] = txt
        session["step"] = "adresse"

        send_sms(
            from_phone,
            "Takk! 📍\nHvor gjelder dette? (adresse)"
        )
        return PlainTextResponse("")

    # ===== STEG 2: ADRESSE =====
    if session["step"] == "adresse":
        session["adresse"] = txt
        session["step"] = "tidspunkt"

        send_sms(
            from_phone,
            "Når trenger du hjelp?\nSkriv f.eks:\n• akutt\n• i dag\n• senere"
        )
        return PlainTextResponse("")

    # ===== STEG 3: TIDSPUNKT =====
    if session["step"] == "tidspunkt":
        session["tidspunkt"] = txt.lower()

        akutt = is_akutt(txt)
        senere = is_later(txt)

        # melding til rørlegger
        plumber_msg = (
            f"{'🚨 AKUTT OPPDRAG' if akutt else '📩 NY FORESPØRSEL'}\n\n"
            f"📞 Telefon: {from_phone}\n"
            f"❗ Problem: {session['problem']}\n"
            f"📍 Adresse: {session['adresse']}\n"
            f"⏰ Tidspunkt: {session['tidspunkt']}"
        )

        send_sms(PLUMBER_PHONE, plumber_msg)

        # svar kunde
        if akutt:
            send_sms(
                from_phone,
                "🚨 Dette er registrert som AKUTT.\nRørlegger er varslet umiddelbart."
            )
        elif senere:
            send_sms(
                from_phone,
                f"Takk! 🙌\nHenvendelsen er sendt videre.\n\n"
                f"Ønsker du å booke tid selv?\n{CALENDLY_LINK}"
            )
        else:
            send_sms(
                from_phone,
                "Takk! 🙌\nHenvendelsen er sendt videre."
            )

        # ferdig → slett session
        sessions.pop(from_phone, None)
        return PlainTextResponse("")

    return PlainTextResponse("")
