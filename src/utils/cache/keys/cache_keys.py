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


def GetBasicUserDataDomainCacheKey(user_id: int):
    return f"user_domain:{user_id}"

##profile
def GetProfileCacheKey(user_id: int):
    return f"user_data:{user_id}"

##friendship
def GetUserRelationshipsDomainCacheKey(user_id: int):
    return f"user_relationships_domain:{user_id}"


def GetUserRelationshipsCacheKey(user_id: int):
    return f"user_relationships:{user_id}"


def GetFriendshipCacheKey(user_id1: int, user_id2: int):
    return f"relationship:{user_id1}:{user_id2}"



## search keywords
def GetUserSearchCacheKey(keywords:str):
    return f"search::user:{keywords}"

def GetUserSearchCacheWithRelationshipKey(keywords:str):
    return f"search::user:{keywords}"


def GetUserSearchDomainCacheKey(keywords:str):
    return f"search::domain:user:{keywords}"


## users trip data cache key
#
def GetUsersTripDataCacheKey(user_id:int):
    return f"user:{user_id}::public_trips"
