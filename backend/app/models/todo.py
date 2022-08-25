import datetime
import uuid

import sqlmodel


def generate_fixed_uuid() -> uuid.UUID:
    """
    Make sure that uuid does not start with a leading 0.

    TODO: Remove it when https://github.com/tiangolo/sqlmodel/issues/25 will be solved.
    """
    val = uuid.uuid4()
    while val.hex[0] == "0":
        val = uuid.uuid4()
    return val


def get_utcnow() -> datetime.datetime:
    """
    Return datetime in UTC.

    It allows deferring initialization of the datetime module, thus mock it using
    freezegun.
    """
    return datetime.datetime.utcnow()


class Todo(sqlmodel.SQLModel, table=True):
    id: uuid.UUID = sqlmodel.Field(
        primary_key=True, default_factory=generate_fixed_uuid, nullable=False
    )
    title: str = sqlmodel.Field(min_length=4, max_length=128)
    description: str | None = sqlmodel.Field(max_length=2048)
    remind_at: datetime.datetime | None
    created_at: datetime.datetime = sqlmodel.Field(default_factory=get_utcnow)
    updated_at: datetime.datetime = sqlmodel.Field(
        default_factory=get_utcnow, sa_column_kwargs={"onupdate": get_utcnow}
    )
