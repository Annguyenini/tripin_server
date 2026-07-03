# purpose is to read/write trip domain
# trip domain

import json
from datetime import datetime, timezone

from numpy.ma.core import sort

from database.friendships_db_service import FriendShipsDatabaseService
from src.database.database_keys import DATABASEKEYS
from src.database.s3.s3_service import S3Sevice
from src.error_handler.error_handler import ErrorHandler
from src.repository.friendships_repository import FriendShipsRepository
from src.repository.user_data_repository import UserDataRepository
from src.utils.cache.cache import Cache
from src.utils.cache.keys.cache_keys import GetUserRelationshipsCacheKey
from src.utils.handle_exception import handle_exception
from src.utils.time_convert import timestamptz_to_ms


class FriendShipsService:
    _instance = None
    _init = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        self.CacheService = Cache()
        self.FriendShipsRepository = FriendShipsRepository()
        self.UserRepository = UserDataRepository()
        self.S3Service = S3Sevice()
        self.ErrorHandler = ErrorHandler().logger("Friendships service")
        self.FriendShipsDatabaseService = FriendShipsDatabaseService
        self._init = True

    def _get_user_data_with_avatar(self, user_id: int):
        target = self.UserRepository.get_user_data(user_id)
        if target["avatar"]:
            target["avatar"] = S3Sevice.generate_temp_uri(key=target["avatar"])
        result = {
            "avatar": target["avatar"],
            "display_name": target["display_name"],
            "user_name": target["user_name"],
            "user_id": target["id"],
        }
        return result

    def _get_user_relationships(self, user_id: int) -> dict[str, []] | None:
        # this function help build 3 types of relationship
        # 1 - friend
        # 2 - incomming friend request
        # 3 - outcomming friend request
        USER1 = DATABASEKEYS.FRIENDSHIPS.USER_ID1
        USER2 = DATABASEKEYS.FRIENDSHIPS.USER_ID2
        STATUS = DATABASEKEYS.FRIENDSHIPS.STATUS
        try:
            ## look in cache
            cache_key = GetUserRelationshipsCacheKey(user_id=user_id)
            raw_data_from_cache = self.CacheService.get(key=cache_key)
            if raw_data_from_cache:
                data_from_cache = json.loads(raw_data_from_cache)
                return data_from_cache
            ## cache miss
            # get all user relationship
            relationships_list = self.FriendShipsRepository.get_user_relationships(
                user_id=user_id
            )
            # if null, there are error
            # relationships_list is [] if empty
            if relationships_list is None:
                return None

            friends_list = []
            incoming_friend_requests = []
            outgoing_friend_requests = []
            ## loop through all the relationship and separate it into 3 types
            for relationship in relationships_list:
                user1 = relationship.get(USER1)
                user2 = relationship.get(USER2)
                status = relationship.get(STATUS)
                ## if user is the user1
                if user_id == user1:
                    target_id = user2
                    target = self._get_user_data_with_avatar(user_id=target_id)
                    if status == "FRIEND":
                        friends_list.append(target)
                    elif status == "REQ_1":
                        outgoing_friend_requests.append(target)
                    elif status == "REQ_2":
                        incoming_friend_requests.append(target)
                ## if user is user 2
                elif user_id == user2:
                    target_id = user1
                    target = self._get_user_data_with_avatar(user_id=target_id)
                    if status == "FRIEND":
                        friends_list.append(target)
                    elif status == "REQ_2":
                        outgoing_friend_requests.append(target)
                    elif status == "REQ_1":
                        incoming_friend_requests.append(target)
            result = {
                "friends_list": friends_list,
                "incoming_friend_requests": incoming_friend_requests,
                "outgoing_friend_requests": outgoing_friend_requests,
            }
            ## put to cache
            self.CacheService.set(key=result, data=json.dumps(result), time=3600)
            return result
        except Exception as e:
            print(e)
            self.ErrorHandler.error("fail to get user relationships", str(e))
            return None

    @handle_exception("Friendships service", "get-friends-list")
    def get_friends_list(self, user_id: int):
        relationships = self._get_user_relationships(user_id=user_id)
        friends_list = relationships.get("friends_list")
        if friends_list is None:
            return {"code": "failed", "message": "Fail to get friends list"}, 500
        return {
            "code": "successfully",
            "message": "successfully",
            "friends_list": friends_list,
        }, 200

    @handle_exception("Friendships service", "get-incoming-frient-list")
    def get_incoming_friend_requests(self, user_id: int):
        relationships = self._get_user_relationships(user_id=user_id)
        incoming_friend_requests = relationships.get("incoming_friend_requests")
        if incoming_friend_requests is None:
            return {"code": "failed", "message": "Fail to get friends list"}, 500
        return {
            "code": "successfully",
            "message": "successfully",
            "incoming_friend_requests": incoming_friend_requests,
        }, 200

    @handle_exception("Friendships service", "get-outcoming-request-list")
    def get_outcoming_requests(self, user_id: int):
        relationships = self._get_user_relationships(user_id=user_id)
        outcoming_requests = relationships.get("outcoming_requests")
        if outcoming_requests is None:
            return {"code": "failed", "message": "Fail to get friends list"}, 500
        return {
            "code": "successfully",
            "message": "successfully",
            "outcoming_requests": outcoming_requests,
        }, 200

    @handle_exception("friendship service", "accept friend request")
    def accept_friend_request(self, user_id: int, target_user_id: int):
        user_id1, user_id2 = sort(user_id, target_user_id)
        relationship = self.FriendShipsRepository.get_relationship(
            user_id1=user_id1, user_id2=user_id2
        )
        if relationship is None:
            return {"code": "failed", "message": "couldn't find the relationship"}, 400
        status = relationship.get("status")

        ## prevent mixed
        # if status = REQ_1 user_id1 have to be the target
        # if status = REQ_2 user_id2 have to be the target
        if (status == "REQ_1" and target_user_id != user_id1) or (
            status == "REQ_2" and target_user_id != user_id2
        ):
            return {"code": "failed", "message": "couldn't find the relationship"}, 400
        last_update = datetime.now(timezone.utc)
        # update the database
        self.FriendShipsDatabaseService.update_relationships(
            user_id1=user_id1,
            user_id2=user_id2,
            status="FRIEND",
            last_update=last_update,
        )
        ## invalidate cache for both user
        # invalidate the domain data
        self.FriendShipsRepository.invalidate_cache(user_id=user_id)
        self.FriendShipsRepository.invalidate_cache(user_id=target_user_id)
        # invalidate user relationship list
        self.invalid_user_relationship_list_cache(user_id=user_id)
        self.invalid_user_relationship_list_cache(user_id=target_user_id)
        return {"code": "successfully", "message": "successfully"}, 200
        pass

    @handle_exception("friendship service", "request friend")
    def request_friend(self, user_id: int, target_user_id: int):

        if user_id < target_user_id:
            user_id1 = user_id
            user_id2 = target_user_id
            status = "REQ_1"
        elif user_id > target_user_id:
            user_id2 = user_id
            user_id1 = target_user_id
            status = "REQ_2"

        insert = self.FriendShipsDatabaseService.insert_new_relationships(
            user_id1=user_id1, user_id2=user_id2, status=status
        )
        if not insert:
            return {"code": "failed", "message": "failed to request friend"}, 500
        ## invalidate cache for both user
        # invalidate the domain data
        self.FriendShipsRepository.invalidate_cache(user_id=user_id)
        self.FriendShipsRepository.invalidate_cache(user_id=target_user_id)
        # invalidate user relationship list
        self.invalid_user_relationship_list_cache(user_id=user_id)
        self.invalid_user_relationship_list_cache(user_id=target_user_id)
        return {"code": "successfully", "message": "successfully"}, 200
        pass

    def invalid_user_relationship_list_cache(self, user_id):
        try:
            cache_key = GetUserRelationshipsCacheKey(user_id=user_id)
            self.CacheService.delete(key=cache_key)
        except Exception as e:
            print(e)
