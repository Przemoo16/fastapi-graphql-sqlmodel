import strawberry

from app.api.v1.resolvers import todo as todo_resolvers
from app.models import todo as todo_models


@strawberry.type
class Query:
    todos: list[todo_models.TodoReadSchema] = strawberry.field(
        resolver=todo_resolvers.get_todos_resolver
    )
    todo: todo_models.TodoReadSchema = strawberry.field(
        resolver=todo_resolvers.get_todo_resolver
    )


@strawberry.type
class Mutation:
    create_todo: todo_models.TodoReadSchema = strawberry.field(
        resolver=todo_resolvers.create_todo_resolver
    )
    update_todo: todo_models.TodoReadSchema = strawberry.field(
        resolver=todo_resolvers.update_todo_resolver
    )
    delete_todo: todo_models.TodoReadSchema = strawberry.field(
        resolver=todo_resolvers.delete_todo_resolver
    )


schema = strawberry.Schema(query=Query, mutation=Mutation)
