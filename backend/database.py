import psycopg2

DATABASE_CONFIG = {
    "dbname": "wildlens",
    "user": "prajwal",
    "host": "localhost",
    "port": "5432"
}


def get_connection():
    return psycopg2.connect(**DATABASE_CONFIG)