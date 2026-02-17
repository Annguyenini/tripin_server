from src.database.s3.s3_client import s3Resource,s3Client, ClientError

from src.server_config.config import Config
from queue import Queue
import time
class S3Sevice:
    _instance = None
    _init =False
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls) 
        return cls._instance
    def __init__(self):
        if self._init:
            return
        self.config = Config()   
        self._queue = Queue()
        self._init = True
        
     
    def generate_temp_uri (self,key:str,expiration:int = 3600):
        # print(s3Client)
        try:
            respond = s3Client.generate_presigned_url('get_object',
            Params={'Bucket': self.config.aws_bucket, 'Key': key},
            ExpiresIn=expiration,)
            # print(respond)
        except ClientError as e:
            print(e)
            return None
        return respond
    
    def upload_media(self,path:str,data):
        """upload to s3

        Args:
            image_path (string): _description_
            image (data): _description_
        Return:
            status(boolean)
        """
        self._queue.put((path,data))
        while not self._queue.empty():
            item_path,item_data = self._queue.get()
            try:
                respond_obj =s3Resource.Bucket(self.config.aws_bucket).put_object(Key=item_path,Body =item_data)
                response = respond_obj.get()           # returns a dict
                if(response['ResponseMetadata']['HTTPStatusCode']==200):
                    return True
            except ClientError as e:
                # Handles AWS service errors, e.g., AccessDenied, NoSuchBucket
                print("AWS ClientError:", e)
            except Exception as e:
                # Handles all other exceptions
                print("Other error:", e)
            self._queue.put((item_data,item_data))
            time.sleep(1)
            return False
    def upload_file(self,file_path:str,base_name:str):
        try:
            respond_obj = s3Client.upload_file(file_path,self.config.aws_logs_bucket,base_name)
        except ClientError as e:
            print(e)
            