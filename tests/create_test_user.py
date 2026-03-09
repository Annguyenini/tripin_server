import psycopg2, os
from werkzeug.security import generate_password_hash
conn = psycopg2.connect(host='localhost', dbname='tripin', user='testuser', password='testpass', port=5432)
hashed = generate_password_hash(os.getenv('TEST_PASS'))
cur = conn.cursor()
cur.execute("INSERT INTO tripin_auth.userdata (email, display_name, user_name, password, created_time, role) VALUES (%s, %s, %s, %s, NOW(), 'user')", ('test@tripping.com', 'TestUser', os.getenv('TEST_USER'), hashed))
conn.commit()
cur.close()
conn.close()
print('Test user created')