# Database Setup with Docker

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
