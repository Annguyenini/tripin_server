## trip data
def GetTripDataCacheKey(trip_id: int):
    return f"trip:{trip_id}"


def GetTripDomainCacheKey(trip_id: int) -> str:
    return f"trip_domain:{trip_id}"


## all trips
def GetUserTripsDataCacheKey(user_id: int):
    return f"trips::user:{user_id}"


def GetUserTripsDomainCacheKey(user_id: int):
    return f"trips_domain::user:{user_id}"


## trip contents
def GetTripContentsCacheKey(trip_id: int) -> str:
    return f"trip_contents:{trip_id}"


def GetTripContentsDomainCacheKey(trip_id: int) -> str:
    return f"trip_contents_domain:{trip_id}"


##userdata
def GetUserDataCacheKey(user_id: int):
    return f"user_data:{user_id}"


def GetUserDomainCacheKey(user_id: int):
    return f"user_domain:{user_id}"
