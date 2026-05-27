import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect(user="postgres", password="postgres", host="localhost", port="5432", database="postgres")
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
try:
    cur.execute("ALTER DATABASE template1 REFRESH COLLATION VERSION;")
except Exception as e:
    print(f"Error refreshing template1: {e}")
try:
    cur.execute("ALTER DATABASE postgres REFRESH COLLATION VERSION;")
except Exception as e:
    print(f"Error refreshing postgres: {e}")
try:
    cur.execute("CREATE DATABASE tnfd_dashboard;")
    print("Database created successfully")
except psycopg2.errors.DuplicateDatabase:
    print("Database already exists")
except Exception as e:
    print(f"Error creating DB: {e}")
cur.close()
conn.close()
