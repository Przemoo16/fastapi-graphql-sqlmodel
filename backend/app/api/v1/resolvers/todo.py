from app.config import db
from app.models import todo as todo_models
from app.services import todo as todo_services


async def create_todo_resolver(
    todo: todo_models.TodoCreateSchema,
) -> todo_models.TodoReadSchema:
    todo_create = todo.to_pydantic()
    async with db.get_session() as session:
        created_todo = await todo_services.create_todo(todo_create, session=session)
    return todo_models.TodoReadSchema.from_pydantic(  # pylint: disable=no-member
        created_todo
    )


async def get_todos_resolver() -> list[todo_models.TodoReadSchema]:
    async with db.get_session() as session:
        todos = await todo_services.get_todos(
            todo_models.TodoFilters(), session=session
        )
    return [  # pylint: disable=no-member
        todo_models.TodoReadSchema.from_pydantic(todo) for todo in todos
    ]


async def get_todo_resolver(
    id: todo_models.TodoID,  # pylint: disable=redefined-builtin
) -> todo_models.TodoReadSchema:
    async with db.get_session() as session:
        todo = await todo_services.get_todo(
            todo_models.TodoFilters(id=id), session=session
        )
    return todo_models.TodoReadSchema.from_pydantic(todo)  # pylint: disable=no-member


async def update_todo_resolver(
    id: todo_models.TodoID,  # pylint: disable=redefined-builtin
    todo: todo_models.TodoUpdateSchema,
) -> todo_models.TodoReadSchema:
    todo_update = todo_models.TodoUpdate.marshal(todo)
    async with db.get_session() as session:
        retrieved_todo = await todo_services.get_todo(
            todo_models.TodoFilters(id=id), session=session
        )
        updated_todo = await todo_services.update_todo(
            retrieved_todo, todo_update, session=session
        )
    return todo_models.TodoReadSchema.from_pydantic(  # pylint: disable=no-member
        updated_todo
    )


# TODO: Cannot return None because of the `assert self.type_annotation is not None`
async def delete_todo_resolver(
    id: todo_models.TodoID,  # pylint: disable=redefined-builtin
) -> todo_models.TodoReadSchema:
    async with db.get_session() as session:
        retrieved_todo = await todo_services.get_todo(
            todo_models.TodoFilters(id=id), session=session
        )
        await todo_services.delete_todo(retrieved_todo, session=session)
    return todo_models.TodoReadSchema.from_pydantic(  # pylint: disable=no-member
        retrieved_todo
    )
