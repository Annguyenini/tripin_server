import os 
import dotenv
from redis import Redis 
import signal
dotenv.load_dotenv()
def bootstrap_redis():
    try:
        host = os.getenv('REDIS_HOST')
        port =os.getenv('REDIS_PORT')
        redis_client = Redis (host =host, port =port, decode_responses =True )
        redis_client.ping()
        return True
    except Exception as e:
        os.kill(os.getppid(), signal.SIGTERM)  # kill the gunicorn master

        os._exit(1)
