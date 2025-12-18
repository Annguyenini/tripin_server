from src.server_config.encryption.encryption import Encryption 
from src.server_config.config import Config
# from src.database.database import Database
from src.server_config.database_config import DatabaseConfig
from dotenv import set_key, load_dotenv
import getpass
import sys
import os
class ServerAuth:
    def __init__(self):
        self.encryption_Service = Encryption()
        self.config = Config()
        # self.database_Service = Database()
        self.database_Config = DatabaseConfig()
        self.config_parser = self.config.get_config_parser() 
        self.database_config_parser = self.config.get_config_parser(path='src/assets/configs/.env')
        self.env_path = self.config.env_path
        load_dotenv(self.env_path)
        self.access_salt_path = self.config.access_salt_path
        self.access_key_path =self.config.access_key_path
        self.encrypt_salt_path = self.config.encrypt_salt_path
        self.database_salt_path =self.config.database_salt_path
        self.encrypt_salt = self.__init__salt(self.encrypt_salt_path)
        self.access_salt = self.__init__salt(self.access_salt_path)
        self.database_salt = self.__init__salt(self.database_salt_path)
        self.master_key = None
        self.access_key =None
        self.database_key =None
        self.database_derived_key =None
        self.__init__access_key()
        
        
    def __init__salt(self,path):
        """
        Docstring for pass in the path and it will return salt
        
        :param path: path of salt
        """
        if not os.path.exists(path):
            try:
                salt = self.encryption_Service.generate_salt()
                with open(path,'w') as w:
                    w.write(salt.hex())
            except: 
                return False
        
        try:
            with open (path ,'r') as r:
                
                ##return salt as byte convert from hex
                item = bytes.fromhex(r.read())
                return item
        except (FileNotFoundError, PermissionError, IOError) as e:
            print(f"File open failed as {e}")
            return None
        

    def __init__access_key(self):
        
        """init access key, using master paswords if access key not exists

        Returns:
            _type_: _description_
        """
        if not os.path.exists(self.access_key_path):
            password = input("INIT Master Password:")
            kdf,status = self.encryption_Service.generate_kdf(self.access_salt)
            key,keysatus = self.encryption_Service.generate_key(kdf,password)  
            with open (self.access_key_path,'w') as w:
                w.write(key.hex())
        try:
            with open (self.access_key_path,'r') as r:
                self.access_key = bytes.fromhex(r.read())
        except (FileNotFoundError, PermissionError, IOError,):
            print(f"ERROR: Failed to open int_key file:")
            return False
        return True
    
    def __init__master_key(self,password):
        if self.encrypt_salt is None : return None
        kdf,status = self.encryption_Service.generate_kdf(self.encrypt_salt)
        self.master_key,keysatus = self.encryption_Service.generate_key(kdf,password)
    

    def verify_indentity(self):
        """verify credential

        Returns:
            _type_: _description_
        """
        password = getpass.getpass("MASTER PASSWORD: ")
        kdf,status  = self.encryption_Service.generate_kdf(self.access_salt)
        key,keystatus = self.encryption_Service.generate_key(kdf,password)
        try: 
            if key == self.access_key:
                print("Successfully authenticated!✅")
                self.__init__master_key(password)
                self.init_database_encrytion()
                return True 
        except Exception as e :
            if "Invalid padding" in str(e):
                print("Wrong password❌")
                sys.exit(1) 
            else:
                import logging
                logging.exception("Unexpected error ❌")
                print("Something went wrong during auth.")
                sys.exit(1)
    
    

    def init_database_encrytion(self):
        ##get a config parser
        config = self.config.get_config_parser()
        encrypted = int (config.get ('status','db_encrypted'))
        print ("[NOTE]: PASSWORD ARE NOT STORE AND REQUIRE EVERYTIME THE SERVER RESTART!")

        if encrypted == 0:
            password = getpass.getpass("INIT DATABASE PASSWORD FOR ENCRYPTION: ")
            ## generate kdf for database key
            kdf,status  = self.encryption_Service.generate_kdf(self.database_salt)
            ## generate database key
            self.database_key, keystatus= self.encryption_Service.generate_key(kdf,password)
            ## generate service key for database (note that info of service key must be unique and convert to bytes)
            self.database_service_key = self.encryption_Service.generate_service_key(self.master_key,b"database_service_key")
            ## derive final key for database encryption (using combination of database key and service key)
            self.database_encryption_key = self.encryption_Service.derive_combination_key(self.database_service_key,self.database_key,b"database")
            
            ## encrypt and store in .env file (if not encrypted)

            ### get database credentials from .env file
            # host= os.getenv("DB_HOST").replace(","," "),
            # dbname= os.getenv("DB_NAME"),
            # user= os.getenv("DB_USER"),
            # password= os.getenv("DB_PASS"),
            # port= os.getenv("DB_PORT")
            host = self.database_config_parser.get('DEFAULT','DB_HOST')
            dbname = self.database_config_parser.get('DEFAULT','DB_NAME')
            user = self.database_config_parser.get('DEFAULT','DB_USER')
            password = self.database_config_parser.get('DEFAULT','DB_PASS')
            port = self.database_config_parser.get('DEFAULT','DB_PORT')
            
            ### encrypt database credentials
            encrypted_host,host_iv = self.encryption_Service.encrypt(host,self.database_encryption_key)
            encrypted_dbname, dbname_iv = self.encryption_Service.encrypt(dbname,self.database_encryption_key)
            encrypted_user,user_iv = self.encryption_Service.encrypt(user,self.database_encryption_key)
            encrypted_password,password_iv = self.encryption_Service.encrypt(password,self.database_encryption_key)
            encrypted_port,port_iv = self.encryption_Service.encrypt(port,self.database_encryption_key)
            ### store encrypted database credentials and iv in .env file
            set_key(self.env_path,"DB_HOST",encrypted_host)
            set_key(self.env_path,"DB_NAME",encrypted_dbname)
            set_key(self.env_path,"DB_USER",encrypted_user)
            set_key(self.env_path,"DB_PASS",encrypted_password)
            set_key(self.env_path,"DB_PORT",encrypted_port)
            set_key(self.env_path,"DB_HOST_IV",host_iv.hex())
            set_key(self.env_path,"DB_NAME_IV",dbname_iv.hex())
            set_key(self.env_path,"DB_USER_IV",user_iv.hex())
            set_key(self.env_path,"DB_PASS_IV",password_iv.hex())
            set_key(self.env_path,"DB_PORT_IV",port_iv.hex())
            self.config_parser.set('status','db_encrypted','1')
            with open('src/assets/configs/Confignure.ini', 'w') as configfile:
                self.config_parser.write(configfile)
            print("[NOTE]: DATABASE CREDENTIALS ENCRYPTED AND STORE IN .env FILE")
        self.init_database_decrytion()





    def init_database_decrytion(self):

        password = getpass.getpass("DATABASE PASSWORD FOR DECRYPTION: ")
        kdf,status  = self.encryption_Service.generate_kdf(self.database_salt)
        ## generate database key
        self.database_key, keystatus= self.encryption_Service.generate_key(kdf,password)
        ## generate service key for database (note that info of service key must be unique and convert to bytes)
        self.database_service_key = self.encryption_Service.generate_service_key(self.access_key,b"database_service_key")
        ## derive final key for database encryption (using combination of database key and service key)
        info = b'database'
        self.database_encryption_key = self.encryption_Service.derive_combination_key(self.database_service_key,self.database_key,info)
        ## decrypt database credentials and store in .env file (if encrypted)

        ##get encrypted database credentials from .env file
        host =bytes.fromhex(self.database_config_parser.get('DEFAULT','DB_HOST').strip("'"))
        dbname = bytes.fromhex(self.database_config_parser.get('DEFAULT','DB_NAME').strip("'"))
        user = bytes.fromhex(self.database_config_parser.get('DEFAULT','DB_USER').strip("'"))
        password = bytes.fromhex(self.database_config_parser.get('DEFAULT','DB_PASS').strip("'"))
        port = bytes.fromhex(self.database_config_parser.get('DEFAULT','DB_PORT').strip("'"))

        ##get iv from .env file (read as hex and convert to bytes) and when write to file convert to hex
        host_iv = bytes.fromhex(self.database_config_parser.get('DEFAULT','DB_HOST_IV').strip("'"))
        dbname_iv = bytes.fromhex(self.database_config_parser.get('DEFAULT','DB_NAME_IV').strip("'"))
        user_iv = bytes.fromhex(self.database_config_parser.get('DEFAULT','DB_USER_IV').strip("'"))
        password_iv = bytes.fromhex(self.database_config_parser.get('DEFAULT','DB_PASS_IV').strip("'"))
        port_iv = bytes.fromhex(self.database_config_parser.get('DEFAULT','DB_PORT_IV').strip("'"))
        ##return None if salt is None
        if self.database_salt is None : return None
        ## decrypt database credentials

        ##store as variable to use when connect to database (NOT IN FILE AS PLAIN TEXT)

        decrypted_host = self.encryption_Service.decrypt(host_iv,host,self.database_encryption_key).strip().strip("'").strip('"')
        decrypted_user = self.encryption_Service.decrypt(user_iv,user,self.database_encryption_key).strip().strip("'").strip('"')
        decrypted_dbname = self.encryption_Service.decrypt(dbname_iv,dbname,self.database_encryption_key).strip().strip("'").strip('"')
        decrypted_password = self.encryption_Service.decrypt(password_iv,password,self.database_encryption_key).strip().strip("'").strip('"')
        decrypted_port = self.encryption_Service.decrypt(port_iv,port,self.database_encryption_key).strip().strip("'").strip('"')
        
        ##set credentials to datbase config
        self.database_Config._init_database_properties(decrypted_host,decrypted_dbname,decrypted_user,decrypted_password,int(decrypted_port))
        return True             