import shutil
import threading
import time
import socket
from datetime import datetime 
import os
import boto3
from src.database.s3.s3_service import S3Sevice
import dotenv

from  src.server_config.config import Config       
import schedule
class Logs:
    _instance = None
    _init = False
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._init :return
        self._init =True
        self.server_config = Config()
        self.s3Service = S3Sevice()
        dotenv.load_dotenv(self.server_config.env_path)
        self.running =True
    
    def get_file_name(self):
        timestamp = datetime.now().strftime("%Y-%m-%d")
        file_path = f'{timestamp}.log'
        return file_path
    
    def setup_socket(self):
        HOST = os.getenv('SOCKET_HOST')
        PORT = int(os.getenv('SOCKET_PORT'))
        os.makedirs('logs',exist_ok=True)
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.bind((HOST,PORT))
        self.server.listen(100)
        
    def handle(self,socket,address):
        print('running')
        file_name = self.get_file_name()
        with open(f'logs/{file_name}', 'ab') as log:
            while True:
                data = socket.recv(4096)
                print('data',data.decode())

                if not data:
                    break
                log.write(data + b'\n')
        print('close')
        socket.close() 
        
    def backup_to_s3(self):
        file_name = self.get_file_name()
        file_path =f'logs/{file_name}'
        tmp_path = f'logs/tmp/{file_name}'
        if not os.path.exists(file_path) :return
        os.makedirs('logs/tmp',exist_ok= True)
        shutil.copyfile(file_path,tmp_path)
        self.s3Service.upload_file(file_path,os.path.basename(tmp_path))
        os.remove(tmp_path)

    def run(self):
        print('run')
        self.running =True
        self.setup_socket()
        threading.Thread(target= self.run_s3BackUp,daemon= True).start()
        threading.Thread(target= self.run_recv,daemon= True).start()

    
    def run_recv (self):
        while True:
            soc, address = self.server.accept()
            print(1)
            threading.Thread(target= self.handle, args=(soc,address),daemon= True).start()
            time.sleep(0.5)
            
    def run_s3BackUp(self):
        while self.running:
            self.backup_to_s3()
            time.sleep(60)
    
    def stop (self):
        self.running = False