import os

import dotenv
import psycopg2
from werkzeug.security import generate_password_hash

dotenv.load_dotenv(".env")
conn = psycopg2.connect(
    host=os.environ.get("DB_HOST"),
    dbname=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASS"),
    port=os.environ.get("DB_PORT"),
)
hashed = generate_password_hash("Testpass11234@")
cur = conn.cursor()
cur.execute(
    "INSERT INTO tripin_auth.userdata (email, display_name, user_name, password, created_time, role) VALUES (%s, %s, %s, %s, NOW(), 'user')",
    ("test@tripping.com", "TestUser", "TestUser", hashed),
)
conn.commit()
cur.execute("SELECT * FROM tripin_auth.userdata WHERE user_name = 'TestUser'")
row = cur.fetchone()
cur.close()
conn.close()
print("row", row)
print("Test user created", hashed)
