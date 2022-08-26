import datetime
import typing
import uuid

import pydantic
import sqlmodel
import strawberry


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


TodoTitle: typing.TypeAlias = str
TodoDescription: typing.TypeAlias = str
TodoRemindAt: typing.TypeAlias = datetime.datetime


class Todo(sqlmodel.SQLModel, table=True):
    id: uuid.UUID = sqlmodel.Field(
        primary_key=True, default_factory=generate_fixed_uuid, nullable=False
    )
    title: TodoTitle = sqlmodel.Field(min_length=4, max_length=128)
    description: TodoDescription | None = sqlmodel.Field(max_length=2048)
    remind_at: TodoRemindAt | None
    created_at: datetime.datetime = sqlmodel.Field(default_factory=get_utcnow)
    updated_at: datetime.datetime = sqlmodel.Field(
        default_factory=get_utcnow, sa_column_kwargs={"onupdate": get_utcnow}
    )


class TodoFilters(pydantic.BaseModel):
    title: TodoTitle | None = None


@strawberry.type
class TodoSchema:
    title: TodoTitle
    description: TodoDescription | None
    remind_at: TodoRemindAt | None
