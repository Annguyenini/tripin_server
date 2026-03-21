import time
import psycopg2 
from psycopg2 import pool
import os
import dotenv
import threading
dotenv.load_dotenv()
DB_HOST= os.getenv('DB_HOST')
DB_PORT= os.getenv('DB_PORT')
DB_USER= os.getenv('DB_USER')
DB_PASS= os.getenv('DB_PASS')
DB_NAME= os.getenv('DB_NAME')
# Test without pool
def test_no_pool(n=1000):
    start = time.time()
    for _ in range(n):
        conn = psycopg2.connect(host= DB_HOST,
            dbname= DB_NAME,
            user= DB_USER,
            password= DB_PASS,
            port= DB_PORT)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        conn.close()
    print(f"No pool: {time.time() - start:.3f}s")

# Test with pool
def test_with_pool(n=1000):
    p = pool.ThreadedConnectionPool(5, 20, host= DB_HOST,
            dbname= DB_NAME,
            user= DB_USER,
            password= DB_PASS,
            port= DB_PORT)
    start = time.time()
    for _ in range(n):
        conn = p.getconn()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        p.putconn(conn)
    print(f"With pool: {time.time() - start:.3f}s")

threading.Thread(target=test_no_pool).start()
threading.Thread(target=test_with_pool).start()