import os
from datetime import datetime, timezone

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, render_template


app = Flask(__name__)


def db_config():
    return {
        "host": os.getenv("DB_HOST", "10.20.30.2"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "CRITIQDB"),
        "user": os.getenv("DB_USER", "pg"),
        "password": os.getenv("DB_PASSWORD", ""),
    }


def refresh_seconds():
    return int(os.getenv("DASHBOARD_REFRESH_SECONDS", "5"))


def connect():
    return psycopg2.connect(**db_config())


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

                quoted_table = sql.SQL("{}.{}").format(
                    sql.Identifier(schema),
                    sql.Identifier(name),
                )

                cur.execute(
                    sql.SQL("SELECT * FROM {} LIMIT 50").format(quoted_table)
                )
                rows = cur.fetchall()

                result.append(
                    {
                        "schema": schema,
                        "name": name,
                        "columns": columns,
                        "rows": rows,
                    }
                )

            return result


@app.route("/")
def index():
    return render_template(
        "index.html",
        refresh_seconds=refresh_seconds(),
        db_host=db_config()["host"],
        db_port=db_config()["port"],
        db_name=db_config()["dbname"],
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
