import dataclasses
import datetime
import typing
import uuid

import pydantic
import sqlmodel
from sqlmodel.sql import expression
import strawberry

# Bypassing a warning about caching
# TODO: Remove when https://github.com/tiangolo/sqlmodel/issues/189 is resolved
expression.SelectOfScalar.inherit_cache = True  # type: ignore
expression.Select.inherit_cache = True  # type: ignore


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


TodoID: typing.TypeAlias = uuid.UUID
TodoTitle: typing.TypeAlias = str
TodoDescription: typing.TypeAlias = str
TodoRemindAt: typing.TypeAlias = datetime.datetime


class Todo(sqlmodel.SQLModel, table=True):
    id: TodoID = sqlmodel.Field(
        primary_key=True, default_factory=generate_fixed_uuid, nullable=False
    )
    title: TodoTitle = sqlmodel.Field(min_length=4, max_length=128)
    description: TodoDescription | None = sqlmodel.Field(default=None, max_length=2048)
    remind_at: TodoRemindAt | None = None
    created_at: datetime.datetime = sqlmodel.Field(default_factory=get_utcnow)
    updated_at: datetime.datetime = sqlmodel.Field(
        default_factory=get_utcnow, sa_column_kwargs={"onupdate": get_utcnow}
    )


class TodoCreate(sqlmodel.SQLModel):
    title: TodoTitle
    description: TodoDescription | None = None
    remind_at: TodoRemindAt | None = None


class TodoFilters(pydantic.BaseModel):
    id: TodoID | None = None
    title: TodoTitle | None = None


class TodoUpdate(pydantic.BaseModel):
    title: TodoTitle | None = None
    description: TodoDescription | None = None
    remind_at: TodoRemindAt | None = None

    @classmethod
    def marshal(cls, schema: "TodoUpdateSchema") -> "TodoUpdate":
        return cls.parse_obj(
            {
                key: value
                for key, value in dataclasses.asdict(schema).items()
                if value != strawberry.UNSET
            }
        )


@strawberry.experimental.pydantic.input(model=TodoCreate)
class TodoCreateSchema:
    title: strawberry.auto
    description: strawberry.auto
    remind_at: strawberry.auto


@strawberry.experimental.pydantic.type(model=Todo)
class TodoReadSchema:
    id: strawberry.auto
    title: strawberry.auto
    description: strawberry.auto
    remind_at: strawberry.auto


@strawberry.input
class TodoUpdateSchema:
    title: TodoTitle | None = strawberry.UNSET
    description: TodoDescription | None = strawberry.UNSET
    remind_at: TodoRemindAt | None = strawberry.UNSET
