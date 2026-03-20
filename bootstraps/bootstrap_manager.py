from bootstraps.aws import bootstrap_aws
from bootstraps.credentials import bootstrapping_credentials
from bootstraps.postgress_check import bootstrap_postgres
from bootstraps.redis_check import bootstrap_redis
import os

def bootstrap_manager():
    if os.getenv('FLASK_ENV') == 'testing':
        return  # skip bootstrap in CI
    credential = bootstrapping_credentials()
    postgres = bootstrap_postgres()
    redis = bootstrap_redis()
    aws = bootstrap_aws()
    print('Bootstrap Pass!')