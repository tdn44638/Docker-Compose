# Dashboard

This stack deploys a small live HTML dashboard that reads tables from PostgreSQL and refreshes automatically.

## Files

- `docker-compose.yml`: the dashboard service
- `Dockerfile`: container image for the app
- `app.py`: Flask application and PostgreSQL queries
- `templates/index.html`: dashboard UI
- `.env.example`: environment values to copy to `.env`

## Start

1. Copy `.env.example` to `.env` and adjust the database password if needed.
2. Run `docker compose up -d --build`.
3. Open `http://localhost:5051`.

## Behavior

- Lists all non-system tables in the configured database
- Renders each table as HTML
- Refreshes automatically every `DASHBOARD_REFRESH_SECONDS`
- Shows up to 50 rows per table

## Notes

- `DB_HOST` is set to `10.20.30.2` by default because that is the host shown in your screenshot.
- `DB_NAME` defaults to `CRITIQDB`, which appears to be the database selected in pgAdmin.
- If your PostgreSQL server is inside the same Docker network, change `DB_HOST` to the service name or container IP that is reachable from this stack.
