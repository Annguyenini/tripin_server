import psycopg2
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from psycopg2.extras import DictCursor
import configparser ,os
import subprocess


    
def get_cursor(hostname:str, dbname:str, user:str, password:str, port:int):
    con = psycopg2.connect(
        host = hostname,
        dbname = dbname,
        user = user,
        password = password,
        port = port
    )
    cur = con.cursor()
    return con, cur

def init_database_scheme():
    print("PLEASE MAKE SURE TO HAVE A DATABASE READY NAME tripin")
    print("Create database by 'CREATE BASE tripin'")
    
    host = str(input("Enter host usually ('localhost)"))
    db_name = str(input("Enter database name"))
    user = str(input("Enter username"))
    password = str(input("Enter password"))
    port = int(input("Enter port"))
    con, cur = get_cursor(hostname=host,dbname=db_name,user=user,password=password,port=port)
    cur.execute('CREATE SCHEMA IF NOT EXISTS tripin_auth;')
    con.commit()
    cur.execute('CREATE TABLE IF NOT EXISTS tripin_auth.userdata (id SERIAL PRIMARY KEY, email TEXT,display_name TEXT, user_name TEXT, password TEXT,created_time TIMESTAMP NOT NULL)')
    con.commit()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tripin_auth.tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES tripin_auth.userdata(id) ON DELETE CASCADE,
    user_name TEXT NOT NULL,
    token TEXT NOT NULL,
    issued_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expired_at TIMESTAMP NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE
    );

    ''')
    con.commit() 
    cur.execute(''' CREATE TABLE IF NOT EXISTS tripin_auth.session (id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES tripin_auth.userdata(id) ON DELETE CASCADE, login_time TIMESTAMP NOT NULL, last_activity TIMESTAMP NOT NULL);''')
    con.commit()
    con.close()
    set_up_config_env(hostname=host,dbname=db_name,user=user,password=password,port=port)
    

def set_up_config_files():
    parent_path = 'src/assets/configs'
    os.makedirs(parent_path,exist_ok=True)
    with open('src/assets/configs/Confignure.ini','w')as config_file:
        content = """[paths]
private_key = src/assets/keys/private.pem
public_key = src/assets/keys/public.pem
access_salt = src/assets/keys/access_salt.pem
access_key = src/assets/keys/access_key.pem
encrypt_salt = src/assets/keys/encrypt_salt.pem
database_salt = src/assets/keys/database_salt.pem
env_path = src/assets/configs/.env

[status]
db_encrypted = 0
"""
        config_file.write(content)
        
def set_up_config_env(hostname:str, dbname:str, user:str, password:str, port:int):
    config = configparser.ConfigParser()
    parent_path = 'src/assets/configs'
    os.makedirs(parent_path,exist_ok=True)
    config["DEFAULT"]={
        "DB_HOST":f"{hostname}",
        "DB_PORT":f"{port}",
        "DB_USER":f"{user}",
        "DB_PASS":f"{password}",
        "DB_NAME":f"{dbname}"
    }
    config["email setting"]={
        "EMAIL_USERNAME" : "trip.in.11234207@gmail.com",
        "EMAIL_PASSWORD" :"wpgm bhtr klbc bqnf",
        "MAIL_DEFAULT_SENDER":"trip.in.11234207@gmail.com"
    }
    with open('src/assets/configs/.env','w') as env:
        config.write(env)   
    
    
def set_up_keys():
        config = configparser.ConfigParser()
        config.read('src/assets/configs/Confignure.ini')
        _private_key_path = config.get('paths','private_key',fallback=None)
        _public_key_path = config.get('paths','public_key',fallback=None)
        
        parent_path ="src/assets/keys"
        os.makedirs(parent_path,exist_ok=True)
        
        if not os.path.exists(_private_key_path):
            private_key =rsa.generate_private_key( public_exponent=65537,
            key_size=2048)
            
            with open(_private_key_path,'wb') as private:
                private.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
        if not os.path.exists(_public_key_path):
                    
            public_key = private_key.public_key()

            # save public key
            with open(_public_key_path, "wb") as f:
                f.write(
                    public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                )

if __name__ == "__main__":
            
    init_database_scheme()
    set_up_config_files()
    set_up_keys()

