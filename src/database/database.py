## use to control the database
## contain functions to modify database directly
## helpo avoid other class, function to touch database directly
## act as a layer between server to database
## all functions that contain query must use parameter (EX: UPDATE table SET user =%s, (value))



import psycopg2
from psycopg2 import pool
from dotenv import set_key, load_dotenv
import os
import inspect
from datetime import datetime
from psycopg2.extras import DictCursor,RealDictCursor
from src.database.database_keys import DATABASEKEYS
import os 
import dotenv
dotenv.load_dotenv()
class Database:
    _instance = None
    _initialized_credentials = False
    def __new__(cls,*args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True        
        self._initialized =False
        # database credentials
        self.database_host =None
        self.database_dbname =None
        self.database_username  =None
        self.database_password =None
        self.database_port = None 
        
        self._pool =None       
    
    def _init_connection_pool(self):
        """create connection pool
        """
        if not self._initialized_credentials:
            self._init_database_credentials()
            
            
        self._initialized_credentials = True
        try:
            self._pool = pool.ThreadedConnectionPool(
                5, 20,  # min, max connections
                host=self.database_host,
                dbname=self.database_dbname,
                user=self.database_username,
                password=self.database_password,
                port=self.database_port
            )
        except Exception as e:
            print (f'Failed to init postgres pool: {e}')
        
    # set database credentials(onlyfor server Auth class)
    def _init_database_credentials(self):
        self.database_host =  os.getenv("DB_HOST")
        self.database_dbname = os.getenv("DB_NAME")
        self.database_username = os.getenv("DB_USER")
        self.database_password = os.getenv("DB_PASS")
        self.database_port = os.getenv("DB_PORT")

    def connect_db(self,cur_options:str = 'rowDict'):
        """connect to postgres

        Returns:
            _cursor_: con, cur  
        """
        if self._pool is None:
            self._init_connection_pool()
        
        conn = self._pool.getconn() 

        # con = sqlite3.connect(path,check_same_thread=False,isolation_level=None)
        if cur_options =='realDict':
            cur= conn.cursor(cursor_factory=RealDictCursor)
        else:
            cur= conn.cursor(cursor_factory=DictCursor)

        return conn, cur

    def close_db (self,conn):
        """return conection to pool

        Args:
            conn (_type_): _description_
        """
        self._pool.putconn(conn=conn)
    
                
    def find_item_in_sql(self, table:str, 
                         item:str, value, 
                         second_condition:bool | None=None, 
                         second_item:str |None = None, second_value: str| None=None, 
                         order_by:str | None=None, 
                         order_type:str |None = None,
                         return_option:str |None="fetchone",):
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
        con,cur = None,None
        try:
            con,cur = self.connect_db()

        
            if not second_condition:
                query = f'SELECT * FROM {table} WHERE {item}=%s'
                if order_by :                  
                    if not order_type:
                        raise('need to specify the order_type')
                    query =f'SELECT * FROM {table} WHERE {item}=%s ORDER BY {order_by} {order_type}'
                cur.execute (query=query,vars=(value,))
            else :
                query =f'SELECT * FROM {table} WHERE {item}=%s AND {second_item} =%s'
                if order_by :                  
                    if not order_type:
                        raise('need to specify the order_type')
                    query =f'SELECT * FROM {table} WHERE {item}=%s AND {second_item} =%s ORDER BY {order_by} {order_type}'
                cur.execute(query,(value,second_value,))
            
            con.commit()
            item = None
            if return_option =="fetchall":
                item = cur.fetchall()
            else:
                item = cur.fetchone()
                
            return item  
        except Exception as e:
            print('Error at find item ',e)
            return None
        finally:
            if con: self.close_db(conn=con)

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
        try:
            con,cur = self.connect_db()

            
            cur.execute(f'UPDATE {table} SET {item_to_update} =%s WHERE {item} = %s',(value_to_update,value,))
            con.commit()
            self.close_db(conn=con)
            if cur.rowcount <0:
                return False
            
            return True
        except Exception as e:
            print ('failed to update to database',e)
            return False
    def delete_from_table(self,table:str, item:str,value:str, second_condition:bool | None=None, second_item:str | None=None , second_value:str | None=None):
        con,cur = self.connect_db()

        if second_condition:
            cur.execute(f'DELETE FROM {table} WHERE {item} = %s AND {second_item} = %s',(value,second_value))
        else:
            cur.execute(f'DELETE FROM {table} WHERE {item} = %s',(value))            
        con.commit()
        self.close_db(conn=con)
        if cur.rowcount <= 0:
            return False
        else :return True
        
   
        
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
        cur.execute(f'INSERT INTO {DATABASEKEYS.TABLES.USERDATA} (email,display_name,user_name,password,created_time) VALUES(%s,%s,%s,%s,%s)',(email,display_name,username,password,current_time))
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
        cur.execute(f'INSERT INTO {DATABASEKEYS.TABLES.TOKENS} (user_id,user_name,token,issued_at,expired_at) VALUES (%s, %s, %s, %s, %s)',(user_id,username,token,issued_at,expired_at,))
        con.commit()
        self.close_db(conn=con)
        if(cur.rowcount>=1):
            return True
        return False
    
