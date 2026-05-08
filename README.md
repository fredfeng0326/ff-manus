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
