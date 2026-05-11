# FF Manus

FF Manus is a multi-agent project built with OpenAI JDK, with FastAPI as the backend framework.
This repository contains the API service and infrastructure setup for storage, migrations, and testing.

## Database Setup with Docker

This project uses PostgreSQL and Redis. You can create both services with Docker using the commands below.

## 1) Create PostgreSQL Container

```bash
docker run -d \
  --name manus-postgres \
  -p 5435:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=manus \
  -v manus_postgres_data:/var/lib/postgresql \
  postgres:latest
```

## 2) Create Redis Container

```bash
docker run -d \
  --name manus-redis \
  -p 6380:6379 \
  -v manus_redis_data:/data \
  redis
```

## Redis message queue & tasks (overview)

The **domain** only describes abstract roles: something that behaves like a **message queue**, and something that behaves like a **task** with a **runner**. The **infrastructure** implements that with **Redis Streams** for durable in/out queues, and **asyncio** to run the runner in the background.

In short: **Redis** holds the queued messages; **your process** runs the task logic and reads/writes those queues. A **task** is wired with two streams (input and output) so producers and consumers can stay decoupled. Related code lives under `app/domain/external/` and `app/infrastructure/external/` (queue and task implementations).

## 3) Database Migrations with Alembic

Use Alembic to create and apply database schema migrations.

```bash
# Create a new migration file from model changes
alembic revision --autogenerate -m "describe_your_change"

# Apply all pending migrations
alembic upgrade head

# Roll back the latest migration (optional)
alembic downgrade -1
```

## 4) Run Tests with Pytest

Use pytest to run the test suite.

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run a specific test file
pytest test/app/interfaces/endpoints/test_status_routes.py
```
