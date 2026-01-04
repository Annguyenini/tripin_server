from database_keys import DATABASEKEYS

# Assume your DATABASEKEYS from above

# Access table names
print(DATABASEKEYS.TABLES.USERDATA)
# output: 'tripin_auth.userdata'

print(DATABASEKEYS.TABLES.TRIPS)
# output: 'tripin_trips.trips_table'

# Access columns in USERDATA table
print(DATABASEKEYS.USERDATA.USER_ID)
# output: 'id'

print(DATABASEKEYS.USERDATA.EMAIL)
# output: 'email'

# Access columns in TRIPS table
print(DATABASEKEYS.TRIPS.TRIP_NAME)
# output: 'trip_name'

# Access media keys
print(DATABASEKEYS.TRIP_MEDIAS.KEY)
# output: 'key'

# Access trip coordinates columns
print(DATABASEKEYS.TRIP_COORDINATES.LONGITUDE)
# output: 'longitude'
print(DATABASEKEYS.TRIP_COORDINATES.ALTITUDE)
# output: 'altitude'
