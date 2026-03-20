from .config import PRIMARY_TABLE_NAME, PRIMARY_TABLE_SCHEMA


TABLE_COLUMN_OVERRIDES = {
    (PRIMARY_TABLE_SCHEMA, PRIMARY_TABLE_NAME): [
        "customername",
        "systemname",
        "domainname",
        "online",
        "lastseen",
        "monitored",
        "currentloggedusers",
        "reportedfromip",
        "agentversion",
        "os",
        "ostype",
        "osversion",
        "osbuild",
        "ipaddresses",
        "macaddresses",
        "created",
        "modified",
        "foldername",
    ],
}
