import time
from queue import Queue

from src.database.s3.s3_client import ClientError, s3Client, s3Resource
from src.error_handler.error_handler import ErrorHandler
from src.server_config.config import Config
from src.utils.cache.cache import Cache

MAX_CLOUD_UPLOAD_RETRY = 3
WEB_PREFIX = "web_images/"


class S3Sevice:
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        self.config = Config()
        self._queue = Queue()
        self.cache_service = Cache()
        self.ErrorHandler = ErrorHandler().logger("S3 service")
        self._init = True

    def _s3_client_error(self, traceback: dict):
        self.ErrorHandler.error("S3 Client error", {traceback})

    def _s3_error(self, body: str, traceback: dict):
        self.ErrorHandler.error(body, {traceback})

    def generate_temp_uri(self, key: str, expiration: int = 3600):
        # print(s3Client)
        """generate presigned uri for media

        Args:
            key (str): _description_
            expiration (int, optional): _description_. Defaults to 3600.

        Returns:
            _type_: _description_
        """
        try:
            cache_key = f"presigned:{key}"
            # cache using redis can replace it with simple dictionary
            cache = self.cache_service.get(cache_key)
            if cache:
                return cache

            respond = s3Client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.config.aws_bucket,
                    "Key": key,
                    "ResponseContentType": "image/jpeg",
                },
                ExpiresIn=expiration,
            )

            # print(respond)
        except ClientError as e:
            self._s3_client_error({e})
            return None
        self.cache_service.set(cache_key, expiration, respond)
        return respond

    def generate_upload_url(
        self, key: str, content_type: str, expiration: int = 300, max_size: int = None
    ):
        # print(s3Client)
        """generate presigned uri for media

        Args:
            key (str): _description_
            expiration (int, optional): _description_. Defaults to 3600.

        Returns:
            _type_: _description_
        """
        try:
            param = {
                "Bucket": self.config.aws_bucket,
                "Key": key,
                "ContentType": content_type,
            }
            # if max_size:
            #     param["ContentLength"] = max_size
            respond = s3Client.generate_presigned_url(
                "put_object",
                Params=param,
                ExpiresIn=expiration,
            )
            # print(respond)
        except ClientError as e:
            self._s3_client_error({e})
            return None
        return respond

    def upload_media(self, path: str, data):
        """upload to s3

        Args:
            image_path (string): _description_
            image (data): _description_
        Return:
            status(boolean)
        """

        for i in range(MAX_CLOUD_UPLOAD_RETRY):
            try:
                respond_obj = s3Resource.Bucket(self.config.aws_bucket).put_object(
                    Key=path, Body=data
                )
                response = respond_obj.get()  # returns a dict
                if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    return True
            except ClientError as e:
                # Handles AWS service errors, e.g., AccessDenied, NoSuchBucket
                print("AWS ClientError:", e)
                self._s3_client_error({e})

            except Exception as e:
                # Handles all other exceptions
                print("Other error:", e)
                self._s3_error(body="S3 failed", traceback={e})
            time.sleep(1)
        return False

    def check_s3_object_exists(self, key: str) -> bool:
        try:
            s3Client.head_object(Bucket=self.config.aws_bucket, Key=key)
            return True
        except ClientError as e:
            self._s3_error(body="failed to get head_object", traceback={e})
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def delete_media(self, path: str) -> bool:
        try:
            response = s3Resource.Object(
                self.config.aws_bucket, path
            ).delete()  # returns a dict
            if response["ResponseMetadata"]["HTTPStatusCode"] == 204:
                return True
        except ClientError as e:
            # Handles AWS service errors, e.g., AccessDenied, NoSuchBucket
            self._s3_client_error({e})
            print("AWS ClientError:", e)
        except Exception as e:
            # Handles all other exceptions
            self._s3_error(body="failed to delete object", traceback={e})

            print("Other error:", e)
        return False

    def upload_file(self, file_path: str, base_name: str):
        try:
            respond_obj = s3Client.upload_file(
                file_path, self.config.aws_logs_bucket, base_name
            )
        except ClientError as e:
            self._s3_client_error({e})
            print(e)

    def get_all_web_presigned_urls(self, expiry=3600):

        response = s3Client.list_objects_v2(
            Bucket=self.config.aws_bucket, Prefix=WEB_PREFIX
        )
        if "Contents" not in response:
            return []

        urls = []
        for obj in response["Contents"]:
            if obj["Key"] == "web_images/":
                continue
            cache_key = f"presigned:{obj['Key']}"
            # cache using redis can replace it with simple dictionary
            cache = self.cache_service.get(cache_key)
            if cache:
                urls.append({"key": obj["Key"], "url": cache})
                continue

            url = s3Client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.config.aws_bucket,
                    "Key": obj["Key"],
                },
                ExpiresIn=expiry,
            )

            urls.append({"key": obj["Key"], "url": url})
            cache = self.cache_service.set(key=cache_key, data=url, time=3300)

        return urls
