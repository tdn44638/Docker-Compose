import os
import re
from datetime import datetime, timezone

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, render_template
from dashboard_tabs import TABLE_COLUMN_OVERRIDES, build_table_views
from dashboard_tabs.config import PRIMARY_TABLE_KEY, PRIMARY_TABLE_NAME, PRIMARY_TABLE_SCHEMA


app = Flask(__name__)

FILTER_NAME_BONUS = (
    "name",
    "customer",
    "agent",
    "system",
    "machine",
    "host",
    "domain",
    "folder",
    "status",
    "type",
    "email",
    "ip",
    "serial",
    "model",
    "manufacturer",
    "version",
    "os",
    "date",
    "created",
    "modified",
)

FILTER_NAME_PENALTY = (
    "guid",
    "uuid",
    "id",
    "password",
    "token",
    "hash",
    "binary",
    "blob",
)

def db_config():
    return {
        "host": os.getenv("DB_HOST", "10.20.30.2"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "CRITIQDB"),
        "user": os.getenv("DB_USER", "pg"),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def refresh_seconds():
    return int(os.getenv("DASHBOARD_REFRESH_SECONDS", "15"))


def column_score(column):
    name = (column["column_name"] or "").lower()
    data_type = (column["data_type"] or "").lower()
    score = 0

    if data_type in {"character varying", "character", "text", "uuid", "date", "timestamp without time zone", "timestamp with time zone", "boolean", "integer", "bigint", "smallint", "numeric", "real", "double precision"}:
        score += 4

    for token in FILTER_NAME_BONUS:
        if token in name:
            score += 3

    for token in FILTER_NAME_PENALTY:
        if token in name:
            score -= 5

    if re.search(r"(created|modified|date|time|status|name|type|host|domain|ip|serial|model|manufacturer|version|os)$", name):
        score += 2

    return score


def pick_useful_columns(columns, limit=10):
    ranked = sorted(columns, key=lambda column: (column_score(column), column["column_name"]))
    picked = []
    for column in reversed(ranked):
        if column_score(column) < 0:
            continue
        picked.append(
            {
                "column_name": column["column_name"],
                "data_type": column["data_type"],
                "is_nullable": column["is_nullable"],
            }
        )
        if len(picked) >= limit:
            break
    return picked


def pick_default_columns(schema, table_name, columns, limit=10):
    overrides = TABLE_COLUMN_OVERRIDES.get((schema, table_name), [])
    by_name = {column["column_name"]: column for column in columns}
    picked = []

    for column_name in overrides:
        column = by_name.get(column_name)
        if column and column_name not in picked:
            picked.append(column_name)
        if len(picked) >= limit:
            return picked

    fallback = pick_useful_columns(columns, limit=limit)
    for column in fallback:
        name = column["column_name"]
        if name not in picked:
            picked.append(name)
        if len(picked) >= limit:
            break

    if not picked:
        picked = [column["column_name"] for column in columns[:limit]]

    return picked


def connect():
    return psycopg2.connect(**db_config())


def fetch_table_rows(cur, schema, name):
    # Intentionally fetch every row for the table.
    # No LIMIT or pagination here, because filters must see the full dataset.
    quoted_table = sql.SQL("{}.{}").format(
        sql.Identifier(schema),
        sql.Identifier(name),
    )
    cur.execute(sql.SQL("SELECT * FROM {}").format(quoted_table))
    return cur.fetchall()


def fetch_tables():
    with connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                  AND table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY table_schema, table_name
                """
            )
            tables = cur.fetchall()

            result = []
            for table in tables:
                schema = table["table_schema"]
                name = table["table_name"]

                cur.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                    """,
                    (schema, name),
                )
                columns = cur.fetchall()
                suggested_columns = pick_default_columns(schema, name, columns)

                rows = fetch_table_rows(cur, schema, name)
                views = build_table_views(schema, name, columns, rows, pick_default_columns)

                result.append(
                    {
                        "schema": schema,
                        "name": name,
                        "columns": columns,
                        "suggested_columns": suggested_columns,
                        "rows": rows,
                        "views": views,
                    }
                )

            return result


@app.route("/")
def index():
    return render_template(
        "index.html",
        page="dashboard",
        refresh_seconds=refresh_seconds(),
        db_host=db_config()["host"],
        db_port=db_config()["port"],
        db_name=db_config()["dbname"],
        primary_table_schema=PRIMARY_TABLE_SCHEMA,
        primary_table_name=PRIMARY_TABLE_NAME,
        primary_table_key=PRIMARY_TABLE_KEY,
    )


@app.route("/settings")
def settings():
    return render_template(
        "index.html",
        page="settings",
        refresh_seconds=refresh_seconds(),
        db_host=db_config()["host"],
        db_port=db_config()["port"],
        db_name=db_config()["dbname"],
        primary_table_schema=PRIMARY_TABLE_SCHEMA,
        primary_table_name=PRIMARY_TABLE_NAME,
        primary_table_key=PRIMARY_TABLE_KEY,
    )


@app.route("/api/snapshot")
def snapshot():
    tables = fetch_tables()
    return jsonify(
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "refresh_seconds": refresh_seconds(),
            "tables": tables,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
