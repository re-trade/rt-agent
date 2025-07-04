import os

def get_pg_url_from_env():
    host = os.getenv('PG_HOST')
    port = os.getenv('PG_PORT', '5432')
    database = os.getenv('PG_DATABASE')
    user = os.getenv('PG_USER')
    password = os.getenv('PG_PASSWORD')
    if not all([host, port, database, user, password]):
        raise ValueError("Missing PostgreSQL environment variables")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"