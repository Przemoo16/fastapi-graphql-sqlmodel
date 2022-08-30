import logging
import typing

from sqlalchemy import exc
import sqlmodel
from sqlmodel.sql import expression

from app.models import todo as todo_models

if typing.TYPE_CHECKING:
    from app.config import db

log = logging.getLogger(__name__)


async def create_todo(
    todo: todo_models.TodoCreate, *, session: "db.AsyncSession"
) -> todo_models.Todo:
    return await TodoCRUD(session).create(todo, refresh=True)


async def get_todos(
    filters: todo_models.TodoFilters, *, session: "db.AsyncSession"
) -> list[todo_models.Todo]:
    return await TodoCRUD(session).read_many(filters)


async def get_todo(
    filters: todo_models.TodoFilters, *, session: "db.AsyncSession"
) -> todo_models.Todo:
    try:
        return await TodoCRUD(session).read_one(filters)
    except exc.NoResultFound:
        log.exception("Not found todo in the DB")
        raise


async def update_todo(
    todo_db: todo_models.Todo,
    todo_update: todo_models.TodoUpdate,
    *,
    session: "db.AsyncSession",
) -> todo_models.Todo:
    return await TodoCRUD(session).update(todo_db, todo_update, refresh=True)


async def delete_todo(todo: todo_models.Todo, *, session: "db.AsyncSession") -> None:
    await TodoCRUD(session).delete(todo)


class TodoCRUD:
    def __init__(self, session: "db.AsyncSession"):
        self.session = session
        self.model = todo_models.Todo

    async def create(
        self, entry: todo_models.TodoCreate, refresh: bool = False
    ) -> todo_models.Todo:
        db_entry = self.model.from_orm(entry)
        return await self._save(db_entry, refresh)

    async def read_many(self, entry: todo_models.TodoFilters) -> list[todo_models.Todo]:
        statement = self.build_where_statement(sqlmodel.select(self.model), entry)
        return (await self.session.execute(statement)).scalars().all()

    async def read_one(self, entry: todo_models.TodoFilters) -> todo_models.Todo:
        statement = self.build_where_statement(sqlmodel.select(self.model), entry)
        return (await self.session.execute(statement)).scalar_one()

    async def update(
        self,
        db_entry: todo_models.Todo,
        entry: todo_models.TodoUpdate,
        refresh: bool = False,
    ) -> todo_models.Todo:
        data = entry.dict(exclude_unset=True)
        for key, value in data.items():
            setattr(db_entry, key, value)
        return await self._save(db_entry, refresh)

    async def delete(self, entry: todo_models.Todo) -> None:
        await self.session.delete(entry)
        await self.session.commit()

    async def _save(
        self, entry: todo_models.Todo, refresh: bool = False
    ) -> todo_models.Todo:
        self.session.add(entry)
        await self.session.commit()
        self.session.expire(entry)
        if refresh:
            await self.session.refresh(entry)
        return entry

    def build_where_statement(
        self,
        statement: expression.SelectOfScalar[todo_models.Todo],
        filters: todo_models.TodoFilters,
    ) -> expression.SelectOfScalar[todo_models.Todo]:
        filters_data = filters.dict(exclude_unset=True)
        for attr, value in filters_data.items():
            statement = statement.where(getattr(self.model, attr) == value)
        return statement
