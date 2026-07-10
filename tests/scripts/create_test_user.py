import os
import sys

import dotenv
import psycopg2
from werkzeug.security import generate_password_hash

conn = psycopg2.connect(
    host=os.environ.get("DB_HOST"),
    dbname=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASS"),
    port=os.environ.get("DB_PORT"),
)
username = os.getenv("TEST_USER")
password = os.getenv("TEST_PASS")
hashed = generate_password_hash(password)
cur = conn.cursor()
for i in range(10):
    cur.execute(
        "INSERT INTO tripin_auth.userdata (email, display_name, user_name, password, created_time, role) VALUES (%s, %s, %s, %s, NOW(), 'user')",
        (f"test@tripping{i}.com", username, username+f'{i}', hashed),
    )

conn.commit()
cur.execute("SELECT * FROM tripin_auth.userdata WHERE user_name = 'TestUser'")
row = cur.fetchone()
cur.close()
conn.close()
print("row", row)
print("Test user created", hashed)
print(f'test user created in database :{os.environ.get("DB_HOST")} {os.environ.get("DB_HOST")} {os.environ.get("DB_USER")} {os.environ.get("DB_PASS")} {os.environ.get("DB_PORT")}')
sys.exit(0)
