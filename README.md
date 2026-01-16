# Plumber SMS Lead Generator

Automatisk SMS-basert lead capture for rørleggerbedrifter.

Systemet svarer kunder via SMS når de tar kontakt, samler inn:
- Problem
- Adresse
- Tidspunkt

og sender ferdig strukturert lead til rørlegger.

---

## 🚀 Funksjoner
- Twilio SMS webhook
- Samtaleflyt via SMS
- Automatisk lead-oppsummering
- Klar for flere kunder (multi-tenant)

---

## 🛠️ Teknologi
- Python
- FastAPI
- Twilio API
- Render (hosting)

---

## ⚙️ Environment variables

Disse må settes i Render / produksjon:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_NUMBER`
- `PLUMBER_PHONE`

---

## 📩 Webhook
Twilio må peke til:

