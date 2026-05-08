from src.server_config.service.Etag.etag_abs import EtagService


class UserdataEtag(EtagService):
    def generate_etag_key(self, user_id: int) -> str:
        return f"user:{user_id}::userdata"

    def generate_etag(self, user_id: int, modified_time: str) -> str:
        return f"user:{user_id}::userdata::modi_time:{modified_time}"


class AllTripsDataEtag(EtagService):
    def generate_etag_key(self, user_id: str) -> str:
        return f"user:{user_id}::alltrips"

    def generate_etag(self, user_id: int, modified_time: str, bucket_hour: int) -> str:
        return (
            f"user:{user_id}::alltrips::modi_time:{modified_time}::bucket:{bucket_hour}"
        )


class TripDataEtag(EtagService):
    def generate_etag_key(self, trip_id: str) -> str:
        return f"trip:{trip_id}::tripdata"

    def generate_etag(self, trip_id: str, modified_time: str, bucket_hour: int) -> str:
        return f"trip:{trip_id}::tripdata::modi_time:{modified_time}::bucket_hour:{bucket_hour}"


class TripContentEtag(EtagService):
    def generate_etag_key(self, trip_id: int) -> str:
        return f"trip:{trip_id}::tripcontent"

    def generate_etag(self, trip_id: int, modified_time: str) -> str:
        return f"trip:{trip_id}::tripcontent::modi_time:{modified_time}"
