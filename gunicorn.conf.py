from gevent import monkey

monkey.patch_all()

import os
import time

from redis import Redis

host = os.getenv("REDIS_HOST")
port = os.getenv("REDIS_PORT")
LOGDIR = os.environ.get("LOGDIR", "logs")
bind = "0.0.0.0:8000"
workers = 4
worker_class = "gevent"
timeout = 120
keepalive = 5
preload_app = True
spew = False

errorlog = f"{LOGDIR}/gunicorn.log"
accesslog = f"{LOGDIR}/gunicorn.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

proc_name = "Tripping Server"


def when_ready(server):
    redis = Redis(host=host, port=port, decode_responses=True)
    redis.set("server:status", "up")
    redis.set("server:uptime", f"{time.time()}")
    redis.publish("admin:status", "up")
    server.log.info("Server is ready. Spawning workers")


def on_exit(server):
    redis = Redis(host=host, port=port, decode_responses=True)
    redis.set("server:status", "down")
    redis.delete("server:uptime")
    redis.publish("admin:status", "down")
    server.log.info("Server down")
