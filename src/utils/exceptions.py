class TripException(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class TripNotFound(TripException):
    def __init__(self) -> None:
        super().__init__("trip_not_found", "Trip NOT Found!")


class TripPermissionError(TripException):
    def __init__(self) -> None:
        super().__init__(
            "no_permission", "You dont have permission to complete this action!"
        )
