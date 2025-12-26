import boto3
from botocore.exceptions import ClientError
s3Resource = boto3.resource('s3', region_name='us-east-2')
s3Client = boto3.client('s3', region_name='us-east-2')