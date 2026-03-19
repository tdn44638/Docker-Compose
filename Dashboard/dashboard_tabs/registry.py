from .windows10 import build_windows10_views


VIEW_BUILDERS = [
    build_windows10_views,
]


def build_table_views(schema, table_name, columns, rows, pick_default_columns):
    for builder in VIEW_BUILDERS:
        views = builder(schema, table_name, columns, rows, pick_default_columns)
        if views:
            return views

    return None
