from fastapi import FastAPI
from strawberry import asgi

from app.api.v1 import api

graphql_app = asgi.GraphQL(api.schema)

app = FastAPI()
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)
