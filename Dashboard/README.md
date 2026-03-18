# Dashboard

This stack deploys a `pgAdmin` web UI that connects to the PostgreSQL server shown in the screenshot.

## Files

- `docker-compose.yml`: pgAdmin service definition
- `.env.example`: local environment values to copy to `.env`
- `servers.json`: pre-registered PostgreSQL server entry

## Start

1. Copy `.env.example` to `.env` and adjust the values.
2. Run `docker compose up -d`.
3. Open pgAdmin on `http://localhost:5050`.

## Preconfigured server

- Name: `DOCKERDB`
- Host: `10.20.30.2`
- Port: `5432`
- Maintenance DB: `postgres`
- Username: `pg`

You will still need the PostgreSQL password for the connection unless you add it manually in pgAdmin.
