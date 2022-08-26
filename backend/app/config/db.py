import typing

from sqlalchemy import orm
from sqlalchemy.ext import asyncio

from app.config import general

settings = general.get_settings()

engine = asyncio.create_async_engine(settings.DATABASE_URL)

AsyncSession: typing.TypeAlias = asyncio.AsyncSession


# TODO: Change to AsyncSession from the SQLModel when
# https://github.com/tiangolo/sqlmodel/issues/54 will be resolved.
# Then replace session.execute with session.exec in the whole codebase.
SessionLocal = orm.sessionmaker(
    engine, class_=asyncio.AsyncSession, expire_on_commit=False
)


def get_session() -> AsyncSession:
    return SessionLocal()
