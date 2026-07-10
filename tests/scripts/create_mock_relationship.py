import os
import sys
import dotenv
import psycopg2
from werkzeug.security import generate_password_hash

# dotenv.load_dotenv()

conn = psycopg2.connect(
    host=os.environ.get("DB_HOST"),
    dbname=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASS"),
    port=os.environ.get("DB_PORT"),
)
cur = conn.cursor()

username = os.getenv("TEST_USER")
password = os.getenv("TEST_PASS")
hashed = generate_password_hash(password)

# Assumes your TEST_USER account has id = 1. Change if it doesn't.
TEST_USER_ID = 1

# Each entry: (other_user_id, relation)
# relation is either "FRIEND", or a tuple ("PENDING", initiator_id)
# initiator_id tells you who sent the request (used to derive REQ_1/REQ_2)
mock_relations = [
    (2, "FRIEND"),                      # already friends
    (3, "FRIEND"),                      # already friends
    (4, ("PENDING", 4)),                # user 4 requested TEST_USER -> incoming
    (5, ("PENDING", 5)),                # user 5 requested TEST_USER -> incoming
    (6, ("PENDING", TEST_USER_ID)),     # TEST_USER requested user 6 -> outgoing
    (7, ("PENDING", TEST_USER_ID)),     # TEST_USER requested user 7 -> outgoing
]

# Unrelated pair, doesn't involve TEST_USER at all — sanity check that
# TEST_USER's incoming/outgoing/friends queries don't pick this up.
unrelated_relations = [
    (8, 9, ("PENDING", 9)),
    (9, 10, "FRIEND"),
]


def insert_relation(id_a, id_b, relation):
    user_id1, user_id2 = sorted([id_a, id_b])

    if relation == "FRIEND":
        status = "FRIEND"
    else:
        _, initiator = relation
        status = "REQ_1" if initiator == user_id1 else "REQ_2"

    cur.execute(
        """
        INSERT INTO tripin_friendships.friendships_table
            (user_id1, user_id2, status, last_update)
        VALUES (%s, %s, %s, NOW())
        """,
        (user_id1, user_id2, status),
    )


for other_id, relation in mock_relations:
    insert_relation(TEST_USER_ID, other_id, relation)

for id_a, id_b, relation in unrelated_relations:
    insert_relation(id_a, id_b, relation)

conn.commit()
cur.close()
conn.close()

print(f"Seeded friendships around user_id={TEST_USER_ID}:")
print("  friends: 2, 3")
print("  incoming (waiting for TEST_USER to accept): 4, 5")
print("  outgoing (waiting for other user to accept): 6, 7")
print("  unrelated pair (8,9 pending / 9,10 friends) for isolation testing")
print(f'test relation created in database :{os.environ.get("DB_HOST")} {os.environ.get("DB_HOST")} {os.environ.get("DB_USER")} {os.environ.get("DB_PASS")} {os.environ.get("DB_PORT")}')
