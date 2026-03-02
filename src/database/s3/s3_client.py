import boto3
from botocore.exceptions import ClientError
s3Resource = boto3.resource('s3', region_name='us-east-2')

def check_cre():

# Default session
    session = boto3.Session()

    # Get credentials currently in use
    creds = session.get_credentials()
    current_creds = creds.get_frozen_credentials()

    print("Access Key:", current_creds.access_key)
    print("Secret Key:", current_creds.secret_key)
    print("Token (if any):", current_creds.token)


s3Client = boto3.client('s3', region_name='us-east-2')