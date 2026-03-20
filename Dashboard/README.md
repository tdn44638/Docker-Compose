# Dashboard

This stack deploys a small live HTML dashboard that reads tables from PostgreSQL and refreshes automatically.

## Files

- `docker-compose.yml`: the dashboard service
- `Dockerfile`: container image for the app
- `app.py`: Flask application and PostgreSQL queries
- `templates/index.html`: dashboard UI
- `dashboard_tabs/`: isolated tab logic, including the Windows 10 view
- `.env.example`: environment values to copy to `.env`

## Start

1. Copy `.env.example` to `.env` and adjust the database password if needed.
2. Run `docker compose up -d --build`.
3. Open `http://localhost:5051`.

## Behavior

- Loads all non-system tables from the configured database
- Renders the primary table from `DASHBOARD_PRIMARY_TABLE` as the main dashboard view
- Keeps other tables available as optional secondary tabs that can be enabled in settings
- Refreshes automatically every `DASHBOARD_REFRESH_SECONDS`
- Shows all rows for the visible tables
- `DASHBOARD_PRIMARY_TABLE` points to the main table for the dashboard tabs, defaulting to `public.atera_devices`
- that primary table has two views: `Alle toestellen` and `Windows 10`
- Each view keeps its own visible columns and column order in the browser
- Windows-specific filtering and tab defaults live in `dashboard_tabs/windows10.py`
- Make sure `DASHBOARD_PRIMARY_TABLE` is passed into the container, for example through `docker-compose.yml` or your deployment environment
- The app does not apply any row limit when loading table data; it fetches every row with `SELECT *` and `fetchall()`

## Windows 10 View

- Focuses on identifying the device owner, machine identity, and current activity
- Uses a compact default column set for support-life visibility
- You can still add or reorder more columns from the selector

## Notes

- `DB_HOST` is set to `10.20.30.2` by default because that is the host shown in your screenshot.
- `DB_NAME` defaults to `CRITIQDB`, which appears to be the database selected in pgAdmin.
- If your PostgreSQL server is inside the same Docker network, change `DB_HOST` to the service name or container IP that is reachable from this stack.
