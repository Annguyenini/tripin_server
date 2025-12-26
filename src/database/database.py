## use to control the database
## contain functions to modify database directly
## helpo avoid other class, function to touch database directly
## act as a layer between server to database
## all functions that contain querry must use parameter (EX: UPDATE table SET user =%s, (value))




import psycopg2
from dotenv import set_key, load_dotenv
import os
from src.server_config.config import Config
from src.server_config.encryption.encryption import Encryption
from src.server_config.database_config import DatabaseConfig
import inspect
from datetime import datetime
from psycopg2.extras import DictCursor


class Database:
    _instance = None
    def __new__(cls,*args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        if getattr(self, "_initialized_credentials", False):
            return
        self._initialized = True
        self._initialized_credentials = False
        self.config = Config()
        self.encryption_Service = Encryption() 
        self.database_config = DatabaseConfig()
        self._initialized =False
        # database credentials
        self.database_host =None
        self.database_dbname =None
        self.database_username  =None
        self.database_password =None
        self.database_port = None        
            
    # set database credentials(onlyfor server Auth class)
    def _init_database_credentials(self):
        self.database_host = self.database_config.database_host
        self.database_dbname = self.database_config.database_dbname
        self.database_username = self.database_config.database_user
        self.database_password = self.database_config.database_password
        self.database_port = self.database_config.database_port
        self._initialized_credentials = True
        
    ## setup table if not exists (assuming exist)
    def __init__authsetup(self):
        if not self._initialized_credentials:
            return
        con,cur = self.connect_db()
        cur.execute('CREATE TABLE IF NOT EXISTS tripin_auth.userdata (id SERIAL PRIMARY KEY, email TEXT,display_name TEXT, user_name TEXT, password TEXT,created_time TIMESTAMP NOT NULL)')
        con.commit()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS tripin_auth.tokens (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES tripin_auth.auth(id) ON DELETE CASCADE,
        user_name TEXT NOT NULL,
        token TEXT NOT NULL,
        issued_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        revoked BOOLEAN NOT NULL DEFAULT FALSE
        );

        ''')
        con.commit() 
        cur.execute(''' CREATE TABLE IF NOT EXISTS tripin_auth.session (id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES tripin_auth.auth(id) ON DELETE CASCADE, login_time TIMESTAMP NOT NULL, last_activity TIMESTAMP NOT NULL);''')
        con.commit()
        con.close()
    def __init__tripsetup(self):
        if not self._initialized_credentials:
            return
        con,cur = self.connect_db()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS tripin_trips.trip_table (
        id SERIAL PRIMARY KEY,
        trip_name INTEGER NOT NULL,
        user_id INTEGER NOT NULL REFERENCES tripin_auth.userdata(id) ON DELETE CASCADE,
        start_time TIMESTAMP NOT NULL,
        end_time TIMESTAMP,
        active BOOLEAN NOT NULL DEFAULT FALSE
        );

        ''')
        con.commit() 
        cur.execute('''
        CREATE TABLE IF NOT EXISTS tripin_trips.trip_points (
        id SERIAL PRIMARY KEY,
        trip_id INTEGER NOT NULL REFERENCES tripin_trips.trip_table(id) ON DELETE CASCADE,
        altitude REAL NOT NULL,
        latitude REAL NOT NULL,
        longtitude REAL NOT NULL,
        speed REAL NOT NULL,
        heading REAL NOT NULL,
        time_stamp TIMESTAMP NOT NULL
        );
        ''')
        con.commit() 
        con.close() 
    def connect_db(self):
        """connect to postgres

        Returns:
            _cursor_: con, cur  
        """
        if not self._initialized:
            self._init_database_credentials()
        conn = psycopg2.connect(
        host= self.database_host,
        dbname= self.database_dbname,
        user= self.database_username,
        password= self.database_password,
        port= self.database_port
        )

        # con = sqlite3.connect(path,check_same_thread=False,isolation_level=None)
        cur= conn.cursor(cursor_factory=DictCursor)
        return conn, cur


    def check_allowance(self,table:str|None =None, item:str|None = None):
        """check for allowance base on table and value

        Args:
            table (str): table_name 
            item (str): column_name
        """
        db_allow_table=['tripin_auth.userdata','tripin_auth.tokens','tripin_trips.trip_coordinates','tripin_trips.trips_table']
        db_allow_items_auth=['email','user_name','password','display_name','token','user_id','issued_at','exprires_at','revoked','id']
        db_allow_items_trip=['trip_name','id','created_time','ended_time','active','image']
        db_allow_items_user =['avatar']
        if table and table not in db_allow_table:
            raise "Table not allowed"
        
        if item and item not in db_allow_items_auth and item not in db_allow_items_trip and item not in db_allow_items_user:
            raise "Item not allowed"
                
                
    def find_item_in_sql(self, table:str, item:str, value:str, second_condition:bool | None=None, second_item:str |None = None, second_value: str| None=None, return_option:str |None="fetchone",):
        """return value base on table and item in postgress

        Args:
            table (str): table name including scheme.
            item (str): column name.
            value (str): value that looking for in column.
            second_condition (bool | None, optional): _True/ False_ find base on 2 columns and 2 values. Defaults to None.
            second_item (str | None, optional): _second column name_. Defaults to None.
            second_value (str | None, optional): _second value name_. Defaults to None.
            return_option (str | None, optional): _fetchone/fetchall_. Defaults to None.

        Returns:
            _list_: list of tuple or tuple
        """
        con,cur = self.connect_db()
        
        self.check_allowance(table,item)
        
        if not second_condition:
            cur.execute (f'SELECT * FROM {table} WHERE {item}=%s',(value,))
        else :
            cur.execute(f'SELECT * FROM {table} WHERE {item}=%s AND {second_item} =%s',(value,second_value,))
        
        if return_option =="fetchall":
            item = cur.fetchall()
        else:
            item = cur.fetchone()
        return item
    
    def update_db(self,table:str, item:str, value:str, item_to_update:str, value_to_update:str ):
        
        """update a specific value where  condition exist 
        Args:
            table: table name
            item: column name of codition
            value: some condition
            item_to_update: column that want to update
            value_to_update: value that want to update
        Returns:
            bool: status
        """
        con,cur = self.connect_db()
        self.check_allowance(table,item)
        self.check_allowance(item = item_to_update)

        cur.execute(f'UPDATE {table} SET {item_to_update} =%s WHERE {item} = %s',(value_to_update,value,))
        con.commit()
        con.close()
        if cur.rowcount <0:
            return False
        return True

    def insert_to_database_trip(self,user_id:int,trip_name:str,imageUri:str):
        """insert new row in to database trip table / return 2 value

        Args:
            user_id (int): _userid_
            trip_name (str): _tripname_

        Returns:
            _bool, int_: _status, trip_id_
        """
        con,cur = self.connect_db()
        created_time = datetime.now()
        cur.execute(f'INSERT INTO tripin_trips.trips_table (user_id,trip_name,created_time, active,image) VALUES (%s,%s,%s,%s,%s) RETURNING id',(user_id,trip_name,created_time,True,imageUri))
        trip_id = cur.fetchone()['id']
        con.commit()
        con.close()
        if cur.rowcount >=1:
            print("insert successfully")
            return True, trip_id
        return False,0 
        
    def insert_to_database_singup(self, email:str, display_name:str, username:str, password:str):
        """insert to database, credential table

        Args:
            email (str): _email_
            display_name (str): _display name_
            username (str): _username_
            password (str): _dpassword (hashed)_

        Returns:
            _bool_: _status_
        """
        con,cur= self.connect_db()
        current_time = datetime.now()
        cur.execute(f'INSERT INTO tripin_auth.userdata (email,display_name,user_name,password,created_time) VALUES(%s,%s,%s,%s,%s)',(email,display_name,username,password,current_time))
        con.commit()
        con.close()
        if cur.rowcount >=1:
            return True
        return False


    def insert_token_into_db(self, user_id :int, username:str, token:str, issued_at, expired_at): 
        """insert into database, token table 

        Args:
            user_id (int): _username_
            username (str): _userid_
            token (str): _token_
            issued_at (timestamp): _timestamp_
            expired_at (timestamp): _timestamp_

        Returns:
            _bool_: _status_
        """

        con,cur = self.connect_db()
        cur.execute(f'INSERT INTO tripin_auth.tokens (user_id,user_name,token,issued_at,expired_at) VALUES (%s, %s, %s, %s, %s)',(user_id,username,token,issued_at,expired_at,))
        con.commit()
        if(cur.rowcount>=1):
            return True
        return False