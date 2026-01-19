import os
from fastapi import FastAPI, Request
from sms import send_sms
from conversation import get_state, update_state

app = FastAPI()

# =========================
# KUNDEKONFIGURASJON (A)
# =========================
# Nøkkel = Twilio-nummer kunden sendte SMS til
# Legg til ny kunde ved å legge til én ny blokk her
CUSTOMERS = {
    "+46734745108": {
        "company": "Bergen Rør AS",
        "plumber_phone": "+4795330248",
        "calendly": "https://calendly.com/svardirekte/befaring-rorleggerhjelp"
    }
}

# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def health():
    return {"status": "ok"}

# =========================
# INCOMING SMS (TWILIO)
# =========================
@app.post("/incoming-sms")
async def incoming_sms(request: Request):
    form = await request.form()
    params = dict(form)

    print("=== INNKOMMENDE SMS (TWILIO) ===")
    print("RAW PARAMS:", params)

    from_phone = params.get("From")
    to_number = params.get("To")
    txt = params.get("Body")

    if not from_phone or not to_number or not txt:
        print("Mangler From / To / Body – ignorerer")
        return {"status": "ignored"}

    from_phone = from_phone.strip()
    to_number = to_number.strip()
    txt = txt.strip()

    print("FROM:", from_phone)
    print("TO:", to_number)
    print("TXT:", txt)

    # Finn riktig kunde basert på Twilio-nummer
    customer = CUSTOMERS.get(to_number)
    if not customer:
        print("❌ Ingen kunde funnet for nummer:", to_number)
        return {"status": "unknown_number"}

    plumber_phone = customer["plumber_phone"]
    calendly_url = customer["calendly"]
    company = customer["company"]

    # Hent samtalestatus
    state = get_state(from_phone)
    step = state["step"]
    data = state["data"]

    print("STEP:", step)
    print("DATA FØR:", data)

    # =========================
    # RESET
    # =========================
    if txt.upper() == "NY":
        update_state(from_phone, "start", {})
        send_sms(from_phone, "OK 👍 Hva kan vi hjelpe deg med?")
        return {"status": "reset"}

    # =========================
    # START
    # =========================
    if step == "start":
        update_state(from_phone, "problem", {})
        send_sms(from_phone, "Hei! 👋 Hva kan vi hjelpe deg med i dag?")
        return {"status": "start"}

    # =========================
    # PROBLEM
    # =========================
    if step == "problem":
        data["problem"] = txt
        update_state(from_phone, "adresse", data)
        send_sms(from_phone, "Takk! Hvor gjelder dette? (adresse eller område)")
        return {"status": "problem_saved"}

    # =========================
    # ADRESSE
    # =========================
    if step == "adresse":
        data["adresse"] = txt
        update_state(from_phone, "tidspunkt", data)
        send_sms(
            from_phone,
            "Når trenger du hjelp?\n"
            "1️⃣ Akutt\n"
            "2️⃣ I dag\n"
            "3️⃣ Senere"
        )
        return {"status": "adresse_saved"}

    # =========================
    # TIDSPUNKT
    # =========================
    if step == "tidspunkt":
        tidspunkt = txt.lower()
        data["tidspunkt"] = txt
        update_state(from_phone, "done", data)

        # Bekreftelse til kunde (alltid)
        send_sms(
            from_phone,
            "Takk 👍 Vi har mottatt henvendelsen din."
        )

        # AKUTT → direkte SMS til rørlegger
        if "akutt" "1" in tidspunkt:
            plumber_msg = (
                f"🚨 AKUTT OPPDRAG – {company}\n\n"
                f"📞 Telefon: {from_phone}\n"
                f"❗ Problem: {data['problem']}\n"
                f"📍 Adresse: {data['adresse']}"
            )
            send_sms(plumber_phone, plumber_msg)

        # I DAG / SENERE → send Calendly til kunde
        else:
            send_sms(
                from_phone,
                "Hvis du ønsker kan du foreslå ønsket tidspunkt her:\n"
                f"{calendly_url}\n\n"
                "Merk: tidspunktet bekreftes av rørlegger før det er endelig."
            )

        print("=== FERDIG LEAD ===")
        print({
            "kunde": company,
            "telefon": from_phone,
            **data
        })

        return {"status": "completed"}

    # =========================
    # DONE
    # =========================
    if step == "done":
        send_sms(from_phone, "Vi har allerede mottatt henvendelsen 👍")
        return {"status": "done"}

    return {"status": "unknown_state"}

