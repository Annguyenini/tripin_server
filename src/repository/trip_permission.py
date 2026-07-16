# purpose is for all service accept Trip Service to verify the owner/ permission of the trip
#
#
from src.repository.friendships_repository import FriendShipsRepository
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
        self.FriendShipsRepository = FriendShipsRepository()
        self._init = True

    def trip_permission_policy(self, request_id: int, trip_id: int):
        trip_data = self.TripRepository.get_trip_data(trip_id=trip_id)
        if trip_data is None:
            raise TripNotFound
        privacy = trip_data.get('privacy')
        print(privacy)

        match privacy:
            case 'public':
                return
            case 'friend':
                target_id = trip_data.get('user_id')
                if not request_id or not target_id:
                    raise TripPermissionError
                user_id1,user_id2 = sorted([request_id,target_id])
                relationship = self.FriendShipsRepository.get_relationship(user_id1=user_id1,user_id2=user_id2)
                if not relationship or relationship.get('status') != 'FRIEND':
                    raise TripPermissionError
                return
            case 'private':
                if int(trip_data.get("user_id")) != int(request_id):
                    raise TripPermissionError
                return
            case _:
                raise TripPermissionError
