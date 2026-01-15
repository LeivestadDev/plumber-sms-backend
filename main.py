from fastapi import FastAPI, Request
from sms import send_sms
from conversation import get_state, update_state

app = FastAPI()


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/incoming-sms")
def incoming_sms(request: Request):
    # 1. Hent alle query-parametere fra Front
    params = dict(request.query_params)

    print("INNKOMMENDE SMS MOTTATT")
    print("DATA:", params)

    # 2. Hent råverdier
    raw_phone = params.get("phonern") or params.get("fromid")
txt = params.get("txt")


    print("RAW_PHONE:", repr(raw_phone))
    print("TXT:", repr(txt))

    # 3. Håndter retries / tomme kall fra Front
    if raw_phone is None or txt is None:
        print("Mangler nummer eller tekst – ignorerer")
        return {"status": "ignored"}

    txt = txt.strip()
    if txt == "":
        print("Tom tekst (retry fra gateway) – ignorerer")
        return {"status": "ignored"}

    # 4. Normaliser telefonnummer
    if raw_phone.startswith("00"):
        phonern = "+" + raw_phone[2:]
    else:
        phonern = raw_phone

    print("NORMALISERT NUMMER:", phonern)

    # 5. Hent samtalestatus
    state = get_state(phonern)
    step = state["step"]
    data = state["data"]

    print("STEP:", step)

    # 6. Samtaleflyt
    if step == "problem":
        data["problem"] = txt
        update_state(phonern, "adresse", data)

        send_sms(
            phonern,
            "Takk. Hvor gjelder dette? (adresse eller område)"
        )

    elif step == "adresse":
        data["adresse"] = txt
        update_state(phonern, "tidspunkt", data)

