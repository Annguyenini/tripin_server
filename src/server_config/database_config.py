class DatabaseConfig:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self,"_initialized",False):
            return
        self._decrypted_host = None 
        self._decrypted_dbname = None 
        self._decrypted_user = None 
        self._decrypted_password = None
        self._decrypted_port =None
        self._initialized = True

        
    def _init_database_properties(self,host:str, dbname:str, user:str, password:str, port:int):
        self._decrypted_host = host
        self._decrypted_dbname =dbname
        self._decrypted_user = user
        self._decrypted_password =password
        self._decrypted_port = port
        self._initialized = True

    @property
    def database_host(self):
        return self._decrypted_host
    
    @property
    def database_dbname(self):
        return self._decrypted_dbname
    
    @property 
    def database_user(self):
        return self._decrypted_user
    
    @property
    def database_password(self):
        return self._decrypted_password
    @property
    def database_port(self):
        return self._decrypted_port