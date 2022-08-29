import sqlmodel
from sqlmodel.sql import expression

from app.config import db
from app.models import todo as todo_models


async def create_todo(todo: todo_models.TodoInput) -> todo_models.TodoSchema:
    async with db.get_session() as session:
        todo_db = todo.to_pydantic()
        created_todo = await TodoCRUD(session).create(todo_db, refresh=True)
        return todo_models.TodoSchema.from_pydantic(  # pylint: disable=no-member
            created_todo
        )


async def get_todos() -> list[todo_models.TodoSchema]:
    async with db.get_session() as session:
        filters = todo_models.TodoFilters()
        todos = await TodoCRUD(session).read_many(filters)
    return [  # pylint: disable=no-member
        todo_models.TodoSchema.from_pydantic(todo) for todo in todos
    ]


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
