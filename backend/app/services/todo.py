import sqlmodel
from sqlmodel.sql import expression

from app.config import db
from app.models import todo as todo_models


async def create_todo(  # type: ignore
    title: todo_models.TodoTitle,
    description: todo_models.TodoDescription | None = None,
    remind_at: todo_models.TodoRemindAt | None = None,
):
    async with db.get_session() as session:
        todo = todo_models.Todo(
            title=title, description=description, remind_at=remind_at
        )
        return await TodoCRUD(session).create(todo, refresh=True)


async def get_todos():  # type: ignore
    async with db.get_session() as session:
        filters = todo_models.TodoFilters()
        return await TodoCRUD(session).read_many(filters)


class TodoCRUD:
    def __init__(self, session: "db.AsyncSession"):
        self.session = session
        self.model = todo_models.Todo

    async def create(
        self, entry: todo_models.Todo, refresh: bool = False
    ) -> todo_models.Todo:
        db_entry = self.model.from_orm(entry)
        return await self._save(db_entry, refresh)

    async def read_many(self, entry: todo_models.TodoFilters) -> list[todo_models.Todo]:
        statement = self.build_where_statement(sqlmodel.select(self.model), entry)
        return (await self.session.execute(statement)).scalars().all()

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
