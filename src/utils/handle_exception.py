from functools import wraps

from werkzeug.exceptions import Conflict

from src.error_handler.error_handler import ErrorHandler


def _get_ErrorHandler():
    return ErrorHandler()


def handle_exception(name: str, service: str):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs) -> tuple[dict, int]:
            try:
                return function(*args, **kwargs)
            except PermissionError as e:
                return {"code": "no_permission", "message": str(e)}, 403
            except AssertionError as e:
                return {"code": "missing_input", "message": str(e)}, 400
            except ValueError as e:
                return {"code": "invalid_input", "message": str(e)}, 400
            except Conflict as e:
                return {
                    "code": e.description["code"],
                    "message": e.description["message"],
                }, 409
            except Exception as e:
                _get_ErrorHandler().logger(name).error(f"failed at {service}", str(e))
                return {"code": "server_fail", "message": str(e)}, 500

        return wrapper

    return decorator
