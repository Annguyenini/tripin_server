import os
from functools import wraps

from flask import make_response, request
from flask.json import jsonify
from werkzeug.exceptions import Conflict, TooManyRequests

from middleware.rate_limiter import ClientProperties, RateLimiter, RateLimiterProperties
from src.error_handler.error_handler import ErrorHandler
from src.utils.exceptions import TripException


def _get_ErrorHandler():
    return ErrorHandler()


def route_exception(
    service: str, endpoint: str, unit: str, unit_value: int, max_requests: int
):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs) -> tuple[dict, int]:
            try:
                if os.environ.get("ENV") == "production":
                    ip = request.remote_addr
                    client = ClientProperties(ip=ip)
                    rate_limiter_pro = RateLimiterProperties(
                        service_name=service,
                        endpoint_name=endpoint,
                        unit=unit,
                        unit_value=unit_value,
                        max_requests=max_requests,
                    )
                    rate_limiter = RateLimiter()
                    current_request, retry_after_s = rate_limiter.is_allowed(
                        rate_limiter_pro, client
                    )
                    response = make_response(function(*args, **kwargs))
                    response.headers["X-RateLimit-Limit"] = str(max_requests)
                    response.headers["X-RateLimit-Remaining"] = str(
                        max_requests - current_request
                    )
                    response.headers["X-RateLimit-Reset"] = str(retry_after_s)
                    return response
                else:
                    response = make_response(function(*args, **kwargs))
                    return response
            except TripException as e:
                return {"code": e.code, "message": e.message}
            except PermissionError as e:
                return {"code": "no_permission", "message": str(e)}, 403

            except AssertionError as e:
                print(e)
                return {"code": "missing_input", "message": str(e)}, 400
            except ValueError as e:
                return {"code": "invalid_input", "message": str(e)}, 400
            except Conflict as e:
                return {
                    "code": e.description["code"],
                    "message": e.description["message"],
                }, 409
            except TooManyRequests as e:
                response = make_response(
                    {"code": "too_many_request", "message": "Too many request"},
                    429,
                )

                response.headers["X-RateLimit-Limit"] = str(max_requests)
                response.headers["X-RateLimit-Remaining"] = 0
                response.headers["X-RateLimit-Reset"] = str(e.retry_after)

                return response
            except Exception as e:
                print(e)
                _get_ErrorHandler().logger(service).error(
                    f"failed at {endpoint}", str(e)
                )
                return {"code": "server_fail", "message": str(e)}, 500

        return wrapper

    return decorator
