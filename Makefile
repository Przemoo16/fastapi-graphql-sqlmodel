
COMPOSE_DEV=docker compose -f config/compose/docker-compose.yml

build:
	$(COMPOSE_DEV) build

confirm-email:
	$(COMPOSE_DEV) exec -T postgres psql --username=postgres postgres -c "UPDATE public.user SET confirmed_email = TRUE WHERE email = '$(EMAIL)';"

create-migration:
	$(COMPOSE_DEV) run --rm backend alembic revision --autogenerate --message '$(MESSAGE)'

lint: lint-backend

lint-backend:
	$(COMPOSE_DEV) run --rm --no-deps backend bash -c " \
		find . -name '*.py' -not -path '*migrations*' -type f | xargs pyupgrade --py310-plus && \
		isort . --check-only && \
		black . --check --exclude=migrations && \
		flake8 . && \
		mypy . && \
		pylint app && \
		bandit . --exclude migrations,tests --recursive \
	"

migrate:
	$(COMPOSE_DEV) run --rm backend alembic upgrade head

remove:
	$(COMPOSE_DEV) down --remove-orphans

run:
	$(COMPOSE_DEV) up

setup:
	git config blame.ignoreRevsFile .git-blame-ignore-revs
	pre-commit install --hook-type pre-commit --hook-type pre-push

stop:
	$(COMPOSE_DEV) stop

test: test-backend

test-backend:
	$(COMPOSE_DEV) run --rm backend pytest .
