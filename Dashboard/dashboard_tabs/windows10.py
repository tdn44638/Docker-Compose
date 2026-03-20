from .config import is_primary_table


WINDOWS10_VIEW_COLUMNS = [
    "customername",
    "systemname",
    "domainname",
    "online",
    "lastseen",
    "currentloggedusers",
    "lastloginuser",
    "reportedfromip",
]


def is_windows10_row(row):
    for key in ("os", "ostype"):
        value = str(row.get(key, "")).lower()
        if "windows 10" in value or "win10" in value or "windows10" in value:
            return True
    return False


def build_windows10_views(schema, table_name, columns, rows, pick_default_columns):
    if not is_primary_table(schema, table_name):
        return None

    windows10_rows = [row for row in rows if is_windows10_row(row)]
    return {
        "all": {
            "label": "Alle toestellen",
            "rows": rows,
            "suggested_columns": pick_default_columns(schema, table_name, columns),
        },
        "windows10": {
            "label": "Windows 10",
            "rows": windows10_rows,
            "suggested_columns": [
                column["column_name"]
                for column in columns
                if column["column_name"] in WINDOWS10_VIEW_COLUMNS
            ][:12],
        },
    }
