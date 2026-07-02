import re

from src.database.s3.s3_client import ClientError, s3Client, s3Resource
from src.database.s3.s3_service import S3Sevice
from src.error_handler.error_handler import ErrorHandler


class TripContentS3Service(S3Sevice):
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        super()
        self.ErrorHandler = ErrorHandler().logger("S3 service")
        self._init = True

    def delete_all_contents_in_trip(self, trip_id: int, retry=2):
        try:
            if retry:
                bucket = s3Resource.Bucket(self.config.aws_bucket)
                prefix = f"trips/{trip_id}/"

                # Delete all objects and versions with the specified prefix
                bucket.objects.filter(Prefix=prefix).delete()
                bucket.object_versions.filter(Prefix=prefix).delete()
            return
        except Exception as e:
            self.ErrorHandler.error("trip content s3", str(e))
            retry = retry - 1
            return self.delete_all_contents_in_trip(trip_id=trip_id, retry=retry)
