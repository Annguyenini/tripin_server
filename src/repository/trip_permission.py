# purpose is for all service accept Trip Service to verify the owner/ permission of the trip
#
#
from src.repository.trip_repository import TripRepository
from src.trip_service.trip_service import TripService
from src.utils.exceptions import TripNotFound, TripPermissionError


class TripPolicy:
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._init:
            return
        self.TripService = TripService()
        self.TripRepository = TripRepository()
        self._init = True

    def trip_permission_policy(self, user_id: int, trip_id: int):
        trip_data = self.TripRepository.get_trip_data(trip_id=trip_id)
        if trip_data is None:
            raise TripNotFound
        if int(trip_data["user_id"]) != int(user_id):
            raise TripPermissionError
