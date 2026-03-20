import psycopg2
import os
import dotenv
import signal
dotenv.load_dotenv
def bootstrap_postgres():
    try:
        DB_HOST= os.getenv('DB_HOST')
        DB_PORT= os.getenv('DB_PORT')
        DB_USER= os.getenv('DB_USER')
        DB_PASS= os.getenv('DB_PASS')
        DB_NAME= os.getenv('DB_NAME')
        conn = psycopg2.connect(
            host= DB_HOST,
            dbname= DB_NAME,
            user= DB_USER,
            password= DB_PASS,
            port= DB_PORT
        )
        conn.cursor().execute("SELECT 1")
        return True
    except Exception as e:
        os.kill(os.getppid(), signal.SIGTERM)  # kill the gunicorn master
        os._exit(1)
