import os
import signal

from redis import Redis


def bootstrap_redis():
    try:
        host = os.environ.get("REDIS_HOST")
        port = os.environ.get("REDIS_PORT")
        redis_client = Redis(host=host, port=port, decode_responses=True)
        redis_client.ping()
        return True
    except Exception as e:
        print("")
        os.kill(os.getppid(), signal.SIGTERM)  # kill the gunicorn master

        os._exit(1)
