import psycopg2
conn = psycopg2.connect(host='localhost', dbname='tripin', user='testuser', password='testpass', port=5432)
cur = conn.cursor()
cur.execute('SELECT id, user_name, password FROM tripin_auth.userdata')
rows = cur.fetchall()
print('Users in DB:', rows)
cur.close()
conn.close()