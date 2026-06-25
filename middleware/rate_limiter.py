import os
from time import time

import dotenv
from redis import Redis
from werkzeug.exceptions import TooManyRequests

allowed_units = ["hour", "minute", "second"]


class ClientProperties:
    ip: str

    def __init__(self, ip: str) -> None:
        self.ip = ip


class RateLimiterProperties:
    """Define rate limit rule for specific endpoint \n
    When define unit, unit_value and window value must also folow the unit \n
    Ex: 1req/1min, subwindow = every 1 minute => unit = 'minute', unit_value = 1, window = 1 \n
    If wish to subwindow to be in second, you may have to define the unit ='second' and unit_value ='60'"""

    service_name: str = ""
    endpoint_name: str = ""
    unit_value: int = 0
    max_requests: int = 0
    global allowed_units
    window: int = 0

    def __init__(
        self,
        service_name: str,
        endpoint_name: str,
        unit: str,
        unit_value: int,
        max_requests: int,
    ):
        if (
            not service_name
            or not endpoint_name
            or not unit_value
            or not max_requests
            or not unit
        ):
            raise ValueError("one or more param is null")
        if unit not in allowed_units:
            raise ValueError(f"Unit not allowed, Must be one of {allowed_units}")
        self.service_name = service_name
        self.endpoint_name = endpoint_name
        self.unit = unit
        self.unit_value = unit_value
        self.max_requests = max_requests
        self._convert()

    def _convert(self):
        match self.unit:
            case "hour":
                self.unit_value = self.unit_value * 3600
                self.window = self.window * 3600
            case "minute":
                self.unit_value = self.unit_value * 60
                self.window = self.window * 60
            case "second":
                pass
            case _:
                raise ValueError("Unexpected unit")
        self.window = self.unit_value // 2

    def __repr__(self) -> str:
        return f"""Rate Limiter Config: (service name: {self.service_name},
        endpoint name: {self.endpoint_name},
        unit: {self.unit},
        unit value: {self.unit_value},
        max requests: {self.max_requests},
        window: {self.window}"""


class RateLimiter:
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._init:
            return
        dotenv.load_dotenv()
        host = os.getenv("REDIS_HOST")
        port = os.getenv("REDIS_PORT")
        self.redis_client = Redis(host=host, port=int(port), decode_responses=True)

        self._init = True

    def is_allowed(self, property: RateLimiterProperties, client: ClientProperties):
        if property is None or client is None:
            raise ValueError("missing client or rate limit properties")
        # get current subwindow
        # get pass subwindow
        # if current subwindow count >= limit: return
        # estimate = (1-X%)pass subwindow + current subwindow
        # estimate < limit
        #
        pipe = self.redis_client.pipeline()
        current_time = int(time())
        current_window = current_time // property.window
        # current sub window key
        current_subw_key = (
            f"rate_limiter:{property.endpoint_name}:{current_window}:{client.ip}"
        )
        # previous sub window key
        previous_subw_key = (
            f"rate_limiter:{property.endpoint_name}:{current_window - 1}:{client.ip}"
        )
        # increase the current sub window
        pipe.incr(current_subw_key)
        # get the previous
        pipe.get(previous_subw_key)
        # reset ttl, ensure that avalible until a new subwindow create
        pipe.expire(current_subw_key, property.window * 2)

        current_raw_count, previous_raw_count, _ = pipe.execute()

        # cast
        current_count = int(current_raw_count or 0)
        previous_count = int(previous_raw_count or 0)

        # second that left in the subwindow
        s_pass_window = current_time % property.window
        # the percentage position of the current in the subwindow
        request_in_percentage = s_pass_window / property.window
        # estimate
        estimate = (1 - request_in_percentage) * previous_count + current_count

        if estimate > property.max_requests:
            # roll back if reject
            pipe.decr(current_subw_key)
            pipe.execute()
            raise TooManyRequests(
                retry_after=current_time + (property.window - s_pass_window)
            )
        return current_count, current_time + (property.window - s_pass_window)
