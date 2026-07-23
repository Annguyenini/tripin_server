from functools import wraps

from werkzeug.exceptions import Conflict

from src.error_handler.error_handler import ErrorHandler
from src.utils.exceptions import TripException


def _get_ErrorHandler():
    return ErrorHandler()


def handle_exception(name: str, service: str):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs) -> tuple[dict, int]:
            try:
                return function(*args, **kwargs)

            except TripException as e:
                return {"code": e.code, "message": e.message},403
            except PermissionError as e:
                return {"code": "no_permission", "message": 'No Permission'}, 403

            except AssertionError as e:
                print(e)
                return {"code": "missing_input", "message": 'Invalid inputs'}, 400
            except TypeError as e:
                print(e)
                return {'code':'bad_request','message':'Bad Request'},400
            except ValueError as e:
                return {"code": "invalid_input", "message": f'Invalid inputs: {e}'}, 400
            except Conflict as e:
                return {
                    "code": e.description["code"],
                    "message": e.description["message"],
                }, 409
            except Exception as e:
                print(e)
                _get_ErrorHandler().logger(name).error(f"failed at {service}", str(e))
                return {"code": "server_fail", "message": 'Something wrong in out end, please try again later'}, 500

        return wrapper

    return decorator
