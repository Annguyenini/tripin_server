import boto3
from botocore.exceptions import ClientError
import os
import signal

def bootstrap_aws():
    try:
        s3 = boto3.client('s3', region_name='us-east-2')
        s3.list_buckets()
        return True
    except Exception as e:
        os.kill(os.getppid(), signal.SIGTERM)  # kill the gunicorn master
        os._exit(1)
