import os

from bootstraps.aws import bootstrap_aws
from bootstraps.credentials import bootstrapping_credentials
from bootstraps.postgress_check import bootstrap_postgres
from bootstraps.redis_check import bootstrap_redis


def bootstrap_manager():
    if os.getenv("ENV") != "production":
        return  # skip bootstrap in CI
    credential = bootstrapping_credentials()
    print("Credential Bootstrap Pass!")
    postgres = bootstrap_postgres()
    print("Progres Bootstrap Pass!")
    redis = bootstrap_redis()
    print("Redis Bootstrap Pass!")

    aws = bootstrap_aws()
    print("AWS Bootstrap Pass!")

    print("Bootstrap Pass!")
