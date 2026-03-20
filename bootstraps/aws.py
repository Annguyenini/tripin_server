import boto3
from botocore.exceptions import ClientError
import os
def bootstrap_aws():
    try:
        s3 = boto3.client('s3', region_name='us-east-2')
        s3.list_buckets()
        return True
    except Exception as e:
        os._exit(1)
