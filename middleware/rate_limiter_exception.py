from functools import wraps

from flask import request

from middleware.rate_limiter import ClientProperties, RateLimiter, RateLimiterProperties


def rate_limiter_handler(
    service: str, endpoint: str, unit: str, unit_value: int, max_requests: int
):
    if (
        service is None
        or endpoint is None
        or unit is None
        or unit_value is None
        or max_requests is None
    ):
        raise ValueError("Missing params")
    ip = request.remote_add()
    client = ClientProperties(ip=ip)
    rate_limiter_properties = RateLimiterProperties(
        service_name=service,
        endpoint_name=endpoint,
        unit=unit,
        unit_value=unit_value,
        max_requests=max_requests,
    )
    request = RateLimiter(rate_limiter_properties, client)
