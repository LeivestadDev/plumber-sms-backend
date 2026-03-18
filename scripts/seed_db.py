#!/usr/bin/env python3
"""Create database tables and seed a test customer.

Usage:
    python scripts/seed_db.py

Environment variables used (falls back to placeholder values if not set):
    TWILIO_NUMBER, PLUMBER_PHONE, CALENDLY_URL
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.database import AsyncSessionLocal, init_db
from app.models import Customer


async def main() -> None:
    await init_db()
    print("Tables created (or already exist).")

    twilio_number = os.getenv("TWILIO_NUMBER", "+4712345678")
    plumber_phone = os.getenv("PLUMBER_PHONE", "+4795330248")
    calendly_url = os.getenv(
        "CALENDLY_URL",
        "https://calendly.com/svardirekte/befaring-rorleggerhjelp",
    )

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Customer).where(Customer.twilio_number == twilio_number)
        )
        if result.scalar_one_or_none():
            print(f"Customer with twilio_number={twilio_number} already exists, skipping.")
            return

        customer = Customer(
            company_name="Test Rørlegger AS",
            twilio_number=twilio_number,
            plumber_phone=plumber_phone,
            calendly_url=calendly_url,
            greeting_message="Hei! Hva kan vi hjelpe deg med i dag?",
        )
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        print(
            f"Seeded customer: id={customer.id}, "
            f"company='{customer.company_name}', "
            f"twilio_number={twilio_number}"
        )


if __name__ == "__main__":
    asyncio.run(main())
