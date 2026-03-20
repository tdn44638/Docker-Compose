import os


DEFAULT_PRIMARY_TABLE = ("public", "atera_devices")


def parse_table_reference(value, default_schema="public", default_table="atera_devices"):
    raw = (value or "").strip()
    if not raw:
        return default_schema, default_table

    if "." in raw:
        schema, table_name = raw.split(".", 1)
        schema = schema.strip() or default_schema
        table_name = table_name.strip() or default_table
        return schema, table_name

    return default_schema, raw


PRIMARY_TABLE_SCHEMA, PRIMARY_TABLE_NAME = parse_table_reference(
    os.getenv("DASHBOARD_PRIMARY_TABLE", ".".join(DEFAULT_PRIMARY_TABLE)),
    default_schema=DEFAULT_PRIMARY_TABLE[0],
    default_table=DEFAULT_PRIMARY_TABLE[1],
)

PRIMARY_TABLE_KEY = f"{PRIMARY_TABLE_SCHEMA}.{PRIMARY_TABLE_NAME}"


def is_primary_table(schema, table_name):
    return (schema, table_name) == (PRIMARY_TABLE_SCHEMA, PRIMARY_TABLE_NAME)
