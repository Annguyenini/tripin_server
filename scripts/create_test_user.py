import psycopg2, os
from werkzeug.security import generate_password_hash
import dotenv
dotenv.load_dotenv('.env.test')
conn = psycopg2.connect(host=os.getenv('DB_HOST'), 
                        dbname=os.getenv('DB_NAME'), 
                        user=os.getenv('DB_USER'), 
                        password=os.getenv('DB_PASS'), 
                        port=os.getenv('DB_PORT'))
hashed = generate_password_hash(os.getenv('TEST_PASS'))
cur = conn.cursor()
cur.execute("INSERT INTO tripin_auth.userdata (email, display_name, user_name, password, created_time, role) VALUES (%s, %s, %s, %s, NOW(), 'user')", ('test@tripping.com', 'TestUser', os.getenv('TEST_USER'), hashed))
conn.commit()
cur.close()
conn.close()
print('Test user created',hashed)