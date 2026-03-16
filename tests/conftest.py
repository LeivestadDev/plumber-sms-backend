from contextlib import contextmanager
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Import all models so they register with Base.metadata before create_all
from app.models import Customer, Conversation, Message  # noqa: F401
from app.database import Base, get_db
from app.main import app
from app.providers.twilio_provider import TwilioProvider


@contextmanager
def mock_twilio_sms(return_value=True):
    """Patch TwilioProvider.send_sms for the duration of a test block."""
    with patch.object(
        TwilioProvider, "send_sms", new_callable=AsyncMock, return_value=return_value
    ) as mock:
        yield mock


@pytest_asyncio.fixture
async def test_engine(tmp_path):
    url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    engine = create_async_engine(url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    SessionLocal = async_sessionmaker(
        test_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with SessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def http_client(test_engine):
    SessionLocal = async_sessionmaker(
        test_engine, expire_on_commit=False, class_=AsyncSession
    )

    async def override_get_db():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with (
        patch("app.main.init_db", new_callable=AsyncMock),
        patch("app.main.seed_from_env_if_empty", new_callable=AsyncMock),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    app.dependency_overrides.clear()


async def make_customer(
    db: AsyncSession,
    *,
    twilio_number: str = "+4712345678",
    plumber_phone: str = "+4798765432",
    company_name: str = "Test Rørlegger AS",
    calendly_url: str = "https://calendly.com/test",
    is_active: bool = True,
    sms_provider: str = "twilio",
) -> Customer:
    customer = Customer(
        company_name=company_name,
        twilio_number=twilio_number,
        plumber_phone=plumber_phone,
        calendly_url=calendly_url,
        is_active=is_active,
        sms_provider=sms_provider,
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer
