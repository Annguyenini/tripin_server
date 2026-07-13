# this is wrapper layer, it purpose is only be a caller for database. Best is to not compute any business logic in this layer


from src.database.database import Database
from src.database.database_keys import DATABASEKEYS
from src.error_handler.error_handler import ErrorHandler


class FriendShipsDatabaseService(Database):
    _instance = None
    _init = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._init:
            return
        super().__init__()
        self.ErrorHandler = ErrorHandler().logger("Friendship Database Service")
        self._init = True

    def get_user_relationships(self, user_id: int):
        con, cur = self.connect_db(cur_options='realDict')
        try:
            cur.execute(
                f"""
                SELECT * FROM {DATABASEKEYS.TABLES.FRIENDSHIPS}
                WHERE (
                {DATABASEKEYS.FRIENDSHIPS.USER_ID1} =%s
                OR
                {DATABASEKEYS.FRIENDSHIPS.USER_ID2} =%s)
                """,
                (
                    user_id,
                    user_id,
                ),
            )
            result = cur.fetchall()
            return result
        except Exception as e:
            print(e)
            self.ErrorHandler.error("Fail to get user friendships", str(e))
            return None
        finally:
            self.close_db(conn=con)

    def get_relationship(self, user_id1: int, user_id2: int):
        """Require user_id1 < user_id2"""
        con, cur = self.connect_db(cur_options='realDict')
        try:
            cur.execute(
                f"""
                SELECT * FROM {DATABASEKEYS.TABLES.FRIENDSHIPS}
                WHERE
                {DATABASEKEYS.FRIENDSHIPS.USER_ID1} =%s
                AND
                {DATABASEKEYS.FRIENDSHIPS.USER_ID2} =%s
                """,
                (
                    user_id1,
                    user_id2,
                ),
            )
            result = cur.fetchone()
            return result
        except Exception as e:
            print(e)
            self.ErrorHandler.error("Fail to get user friendships", str(e))
            return None
        finally:
            self.close_db(conn=con)

    def insert_new_relationships(self, user_id1: int, user_id2: int, status: str):
        con, cur = self.connect_db()
        try:
            cur.execute(
                f"""
                INSERT INTO {DATABASEKEYS.TABLES.FRIENDSHIPS}
                ({DATABASEKEYS.FRIENDSHIPS.USER_ID1},
                {DATABASEKEYS.FRIENDSHIPS.USER_ID2},
                {DATABASEKEYS.FRIENDSHIPS.STATUS}) VALUES(%s,%s,%s)
                """,
                (user_id1, user_id2, status),
            )
            con.commit()
            if cur.rowcount <= 0:
                return False
            return True
        except Exception as e:
            print(e)
            self.ErrorHandler.error("Fail to get insert friendships", str(e))
            return False
        finally:
            self.close_db(conn=con)
        pass

    def update_relationships(
        self, user_id1: int, user_id2: int, status: str, last_update
    ):
        con, cur = self.connect_db()
        try:
            cur.execute(
                f"""
                UPDATE {DATABASEKEYS.TABLES.FRIENDSHIPS}
                SET {DATABASEKEYS.FRIENDSHIPS.STATUS} = %s,
                {DATABASEKEYS.FRIENDSHIPS.LAST_UPDATE} = %s
                WHERE
                {DATABASEKEYS.FRIENDSHIPS.USER_ID1} = %s
                AND
                {DATABASEKEYS.FRIENDSHIPS.USER_ID2} = %s
                """,
                (
                    status,
                    last_update,
                    user_id1,
                    user_id2,
                ),
            )
            con.commit()
            if cur.rowcount <= 0:
                return False
            return True
        except Exception as e:
            print(e)
            self.ErrorHandler.error("Fail to get user friendships", str(e))
            return False
        finally:
            self.close_db(conn=con)
        pass


    def delete_relationship(self,user_id1:int,user_id2:int):
        is_delete = self.delete_from_table(
            table=DATABASEKEYS.TABLES.FRIENDSHIPS,
            item=DATABASEKEYS.FRIENDSHIPS.USER_ID1,
            value=user_id1,second_condition=True,
            second_item=DATABASEKEYS.FRIENDSHIPS.USER_ID2,
            second_value=user_id2)
        return is_delete
