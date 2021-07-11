# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

# DATABASES = {
#     "default": {
#         #"ENGINE": "sql_server.pyodbc",
#         "ENGINE": "mssql",
#         "NAME": "master",
#         #"HOST": "localhost",
#         "HOST": "sqlserver",
#         "PORT": "1433",
#         "USER": "sa",
#         "PASSWORD": "iaengine32K",
#         "OPTIONS":{
#             "driver": "ODBC Driver 17 for SQL Server",
#         }
#     }
# }

ENGINE_MSSQL = env.str("IA_ENGINE_DATABASE_MSQL", default="")

if ENGINE_MSSQL:
    from dj_database_url import SCHEMES
    SCHEMES["mssql"] = ENGINE_MSSQL

DATABASES = {
    "default": env.dj_db_url(
        "IA_ENGINE_DATABASE_URL", default="mssql://sa:iaengine32K@sqlserver:1433/master"
    ),
}