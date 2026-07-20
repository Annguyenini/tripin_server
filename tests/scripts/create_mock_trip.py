import os
import sys
import dotenv
import psycopg2

dotenv.load_dotenv()
conn = psycopg2.connect(
    host=os.environ.get("DB_HOST"),
    dbname=os.environ.get("DB_NAME"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASS"),
    port=os.environ.get("DB_PORT"),
)
cur = conn.cursor()

TEST_USER_ID = 1

# Each entry: (trip_name, privacy, active, ended)
# active=False + ended=True -> a finished trip with ended_time set
# active=True  + ended=False -> an ongoing trip (ended_time = NULL)
mock_trips = [
    ("Solo Japan Trip",         "private", False, True),
    ("Weekend in Big Sur",      "private", True,  False),
    ("College Friends Reunion", "friend",  False, True),
    ("Camping w/ Roommates",    "friend",  True,  False),
    ("Backpacking SE Asia",     "public",  False, True),
    ("Currently in Iceland",    "public",  True,  False),
]

# ended_time needs NOW() vs NULL depending on whether the trip is finished,
# and psycopg2 can't conditionally inline that as a plain param — hence two branches.
def insert_trip(trip_name, privacy, active, ended):
    if ended:
        cur.execute(
            """
            INSERT INTO tripin_trips.trip_table
                (user_id, created_time, active, ended_time, trip_name,
                 image, modified_time, content_modified_time, event, privacy)
            VALUES
                (%s, NOW(), %s, NOW(), %s, %s, NOW(), NOW(), %s, %s)
            RETURNING id
            """,
            (TEST_USER_ID, active, trip_name, None, None, privacy),
        )
    else:
        cur.execute(
            """
            INSERT INTO tripin_trips.trip_table
                (user_id, created_time, active, ended_time, trip_name,
                 image, modified_time, content_modified_time, event, privacy)
            VALUES
                (%s, NOW(), %s, NULL, %s, %s, NOW(), NOW(), %s, %s)
            RETURNING id
            """,
            (TEST_USER_ID, active, trip_name, None, None, privacy),
        )
    return cur.fetchone()[0]

created_ids = []
for trip_name, privacy, active, ended in mock_trips:
    trip_id = insert_trip(trip_name, privacy, active, ended)
    created_ids.append((trip_id, trip_name, privacy))

conn.commit()
cur.close()
conn.close()

print(f"Seeded trips for user_id={TEST_USER_ID}:")
for trip_id, trip_name, privacy in created_ids:
    print(f"  id={trip_id:<4} privacy={privacy:<8} name={trip_name}")
