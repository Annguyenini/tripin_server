import os
import signal

import dotenv
import psycopg2

dotenv.load_dotenv()


def bootstrap_postgres():
    try:
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_USER = os.getenv("DB_USER")
        DB_PASS = os.getenv("DB_PASS")
        DB_NAME = os.getenv("DB_NAME")
        conn = psycopg2.connect(
            host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
        )
        conn.cursor().execute("SELECT 1")
        return True
    except Exception as e:
        print("fail to connect to postgress")

        os.kill(os.getppid(), signal.SIGTERM)  # kill the gunicorn master
        os._exit(1)
