import strawberry


@strawberry.type
class Query:
    user: str


schema = strawberry.Schema(query=Query)
