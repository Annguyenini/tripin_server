from types import SimpleNamespace
DATABASEKEYS= SimpleNamespace(
    TABLES= SimpleNamespace(
        USERDATA='tripin_auth.userdata',       
        TOKENS = 'tripin_auth.tokens',
        TRIP_COORDINATES='tripin_trips.trip_coordinates',
        TRIP_MEDIAS='tripin_trips.trip_medias',
        TRIPS = 'tripin_trips.trips_table',
    ),
    USERDATA = SimpleNamespace(
        USER_ID='id',
        EMAIL ='email',
        DISPLAY_NAME ='display_name',
        USER_NAME = 'user_name',
        PASSWORD='password',
        CREATED_TIME='created_time',
        ROLE = 'role',
        AVARTAR= 'avatar',
        ETAG='etag',
        TRIPS_DATA_VERSION='trips_data_version',
        TRIPS_DATA_ETAG ='trips_data_etag',
        USER_DATA_VERSION ='userdata_version'
    ),
    TOKENS= SimpleNamespace(
        TOKEN_ID='id',
        USER_ID='user_id',
        USER_NAME='user_name',
        TOKEN='token',
        ISSUE_TIME='issue_at',
        EXPIRED_TIME='expired_at',
        REVOKED = 'revoked',
    ),
    TRIPS= SimpleNamespace(
        TRIP_ID='id',
        USER_ID='user_id',
        CREATED_TIME ='created_time',
        ACTIVE ='active',
        ENDED_time='ended_time',
        TRIP_NAME='trip_name',
        IMAGE_KEY='image',
        TRIP_ETAG='etag',
        TRIP_INFO_VERSION='trip_informations_version',
        TRIP_COORDINATES_VERSION='trip_coordinates_version',
        TRIPS_MEDIAS_VERSION='trip_medias_version'
    ),
    TRIP_MEDIAS = SimpleNamespace(
        MEDIA_ID ='id',
        TRIP_ID='trip_id',
        MEDIA_TYPE='media_type',
        KEY='key',
        LONGITUDE='longitude',
        LATITUDE='latitude',
        TIME_STAMP='time_stamp'
    ),
    TRIP_COORDINATES =SimpleNamespace(
        COORDINATES_ID = 'id',
        TRIP_ID ='trip_id',
        BATCH_VERSION ='batch_version',
        LONGITUDE = 'longitude',
        LATITUDE ='latitude',
        ALTITUDE='altitude',
        SPEED='speed',
        HEADING='heading',
        TIME_STAMP='time_stamp',
    )
    
)