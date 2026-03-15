import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
from contextvars import ContextVar
from uuid import UUID
from typing import Optional
import logging

current_user_id_ctx: ContextVar[Optional[UUID]] = ContextVar(
    'current_user_id', default=None
)

logger = logging.getLogger(__name__)
load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Check your .env file.")

engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    connect_args={
        "server_settings": {
            "application_name": "udoo_erp",
        },
        "prepared_statement_cache_size": 0,
        "statement_cache_size": 0
    }
)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
