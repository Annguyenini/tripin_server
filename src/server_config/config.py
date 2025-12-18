import configparser, os

class Config:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True


        self.config = configparser.ConfigParser()
        self.config.read('src/assets/configs/Confignure.ini')

        # paths
        self._private_key_path = self.config.get('paths','private_key',fallback=None)
        self._public_key_path = self.config.get('paths','public_key',fallback=None)
        self._access_key_path = self.config.get('paths','access_key', fallback=None)
        self._access_salt_path = self.config.get('paths','access_salt', fallback=None)
        self._encrypt_salt_path = self.config.get('paths','encrypt_salt', fallback=None)
        self._database_salt_path = self.config.get('paths','database_salt', fallback=None)
        self._env_path = self.config.get('paths','env_path', fallback=None)
        # read keys
        with open(self._private_key_path,'r') as f:
            self._PRIVATE_KEY = f.read()
        with open(self._public_key_path,'r') as f:
            self._PUBLIC_KEY = f.read()
    
        
    
    @property
    def private_key(self):
        return self._PRIVATE_KEY
    @property
    def env_path(self):
        return self._env_path
    @property
    def public_key(self):
        return self._PUBLIC_KEY

    @property
    def access_salt_path(self):
        return self._access_salt_path

    @property
    def access_key_path(self):
        return self._access_key_path
    @property
    def database_salt_path(self):
        return self._database_salt_path
    @property 
    def encrypt_salt_path(self):
        return self._encrypt_salt_path

 

    def get_config_parser(self,**kwargs):
        if kwargs.get("path") is not None:
            config = configparser.ConfigParser()
            config.read(kwargs.get("path"))
            return config
        return self.config

   