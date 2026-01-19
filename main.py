from fastapi import FastAPI, Request
from sms import send_sms
from conversation import get_state, update_state

import os

app = FastAPI()

# Miljøvariabler
PLUMBER_PHONE = os.getenv("PLUMBER_PHONE")
COMPANY_NAME = os.getenv("COMPANY_NAME", "SvarDirekte")

if not PLUMBER_PHONE:
    print("⚠️ ADVARSEL: PLUMBER_PHONE er ikke satt i environment variables")


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/incoming-sms")
async def incoming_sms(request: Request):
    form = await request.form()
    params = dict(form)

    print("=== INNKOMMENDE SMS ===")
    print("RAW PARAMS:", params)

    from_phone = params.get("From")
    txt = params.get("Body")

    print("RAW_PHONE:", from_phone)
    print("TXT:", txt)

    if not from_phone or not txt:
        print("Mangler nummer eller tekst – ignorerer")
        return {"status": "ignored"}

    # Normaliser nummer
    phone = from_phone.strip()

    # Hent samtalestatus
    state = get_state(phone)
    step = state["step"]
    data = state["data"]

    print("STEP:", step)
    print("DATA FØR:", data)

    txt_clean = txt.strip()

    # === STEG 1: PROBLEM ===
    if step == "problem":
        data["problem"] = txt_clean
        update_state(phone, "adresse", data)

        send_sms(
            phone,
            "Takk. Hvor gjelder dette? (adresse eller område)"
        )

        return {"status": "ok"}

    # === STEG 2: ADRESSE ===
    if step == "adresse":
        data["adresse"] = txt_clean
        update_state(phone, "tidspunkt", data)

        send_sms(
            phone,
            "Når trenger du hjelp?\n"
            "1️⃣ Akutt\n"
            "2️⃣ I dag\n"
            "3️⃣ Senere"
        )

        return {"status": "ok"}

    # === STEG 3: TIDSPUNKT ===
    if step == "tidspunkt":
        tidspunkt_raw = txt_clean
        tidspunkt = txt_clean.lower()

        # Alle ord som betyr AKUTT
        AKUTT_KEYWORDS = [
            "akutt",
            "haster",
            "haste",
            "nå",
            "snarest",
            "med en gang",
            "lekkasje",
            "vannlekkasje",
            "sprukket",
            "oversvømmelse",
            "renner",
            "flom"
        ]

        er_akutt = (
            tidspunkt == "1"
            or any(word in tidspunkt for word in AKUTT_KEYWORDS)
        )

        data["tidspunkt"] = tidspunkt_raw
        update_state(phone, "done", data)

        # === AKUTT → VARSEL TIL RØRLEGGER ===
        if er_akutt:
            plumber_msg = (
                f"🚨 AKUTT OPPDRAG – {COMPANY_NAME}\n\n"
                f"📞 Telefon: {phone}\n"
                f"❗ Problem: {data['problem']}\n"
                f"📍 Adresse: {data['adresse']}\n\n"
                f"⏱️ Kundens svar: {tidspunkt_raw}"
            )

            send_sms(PLUMBER_PHONE, plumber_msg)

            print("🚨 AKUTT OPPDRAG SENDT")

            send_sms(
                phone,
                "Takk! Vi har varslet rørleggeren. "
                "Du vil bli kontaktet så raskt som mulig."
            )

        # === IKKE AKUTT → CALENDLY ===
        else:
            send_sms(
                phone,
                "Takk! Du kan foreslå tidspunkt her:\n"
                "https://calendly.com/svardirekte/befaring-rorleggerhjelp"
            )

        print("FERDIG LEAD:", {
            "telefon": phone,
            **data
        })

        return {"status": "ok"}

    # === FALLBACK ===
    send_sms(
        phone,
        "Hei! Kan du kort beskrive hva det gjelder?"
    )
    update_state(phone, "problem", {})

    return {"status": "ok"}
