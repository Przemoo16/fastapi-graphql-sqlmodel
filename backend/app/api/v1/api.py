import strawberry

from app.models import todo as todo_models
from app.services import todo as todo_services


@strawberry.type
class Query:
    todos: list[todo_models.TodoSchema] = strawberry.field(
        resolver=todo_services.get_todos
    )


@strawberry.type
class Mutation:
    create_todo: todo_models.TodoSchema = strawberry.field(
        resolver=todo_services.create_todo
    )


schema = strawberry.Schema(query=Query, mutation=Mutation)
