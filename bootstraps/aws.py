import os
import signal

import boto3
import dotenv
from botocore.exceptions import ClientError

dotenv.load_dotenv()


def bootstrap_aws():
    try:
        s3 = boto3.client(
            "s3",
            region_name=os.environ.get("AWS_DEFAULT_REGION"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        )
        s3.list_buckets()
        return True
    except Exception as e:
        print("fail to connect to AWS")
        os.kill(os.getppid(), signal.SIGTERM)  # kill the gunicorn master
        os._exit(1)
