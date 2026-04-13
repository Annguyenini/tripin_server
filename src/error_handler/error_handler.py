import logging
import json
import traceback
import os
from flask import Blueprint,request,Response,jsonify
from types import SimpleNamespace
from src.database.database import Database,DATABASEKEYS
from src.error_code.error_code import ERROR_KEYS 
import redis 
import uuid
from datetime import datetime,timezone
from src.token.tokenservice import TokenService
class JSONFormatter(logging.Formatter):
    """custom formater for log
        contain id, category,time ,message, body
        using json format
    Args:
        logging (_type_): _description_
    """
    def format(self, record):
        log = {
            'id': record.id,
            'category':record.name,
            "time": self.formatTime(record),
            "type": record.levelname,
            "message": record.getMessage(),
            "traceback": ''.join(traceback.format_exception(*record.exc_info)) if record.exc_info else getattr(record, 'body', None)        }
        redis.Redis().publish('admin:error_log',json.dumps(log))

        return json.dumps(log)

class Filter(logging.Filter):
    """custom filter 
    also use to send data via sse 

    Args:
        logging (_type_): _description_
    """
    def filter(self, record):
        id = str(uuid.uuid4())
        record.id = id
       
        # redis.Redis().publish('admin:error_log',json.dumps({'id':id,'category':category,'time':str(time),'level':level,"message":message,'traceback':traceback}))
        return True
    
LOGDIR = os.environ.get('ERRORLOGDIR','logs/errorlogs')
LOGPATH = f'{LOGDIR}/error.log'
ALLOWCATEGORY = ['auth','database','trip']

class ErrorSSE:
    _instance = None
    _init =False
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        if self._init: return
        self.bp = Blueprint('ErrorSSE',__name__)
        self.databaseService = Database()
        self.redis = redis.Redis()
        self.tokenService = TokenService()
        self._registerRoute()
        self._init = True
    
    def _registerRoute(self):
        @self.bp.before_request
        def _credentialCheck():
            raw_token = request.cookies.get('token')
            token = self.databaseService.find_item_in_sql(
                table=DATABASEKEYS.TABLES.TOKENS,
                item=DATABASEKEYS.TOKENS.TOKEN,
                value= raw_token,)
            if datetime.utcnow() > token['expired_at']:
                print('exp')
                return jsonify({'code':ERROR_KEYS.NOPERMISSION}),401
            if token['role']!= 'admin' or token['revoked']:return jsonify({'code':ERROR_KEYS.NOPERMISSION}),401
           

        # self.bp.route('/error-sse')(self.errorSSEConnect)
        self.bp.route('/request-logs', methods =['GET'])(self.getAllErrorLog)
    
    def getAllErrorLog(self):
        if not os.path.exists(LOGPATH):return jsonify({'logs':[]}),200
        with open (LOGPATH,'r')as log:
            raw_logs = log.readlines()
        logs =[]
        for l in raw_logs:
            logs.append(json.loads(l))
        return jsonify({'logs':logs}) 
    def errorSSEConnect(self):

        return Response(self._liveErrorLogSource(),mimetype='text/event-stream',headers={
            'Access-Control-Allow-Origin': 'http://127.0.0.1:5000',
            'Access-Control-Allow-Credentials':'true',
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        })
    
    
    def _liveErrorLogSource(self):
        pubsub = self.redis.pubsub()
        pubsub.subscribe('admin:error_log')
        for message in pubsub.listen():
            if message['type']=='message':
                yield f'data:{message['data'].decode()}\n\n'
class ErrorHandler:
    # _instance = None
    # _init =False
    # def __new__(cls):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #     return cls._instance

    def __init__(self):
        # if self._init: return
        self._logger = None
        if not os.path.exists(LOGDIR):
            os.makedirs(LOGDIR)        
        # self._init = True

    def _make_logger(self,name,file):
        logger = logging.getLogger(name)
        if logger.handlers:
            print(logger)
            return logger
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(file)
        handler.setFormatter(JSONFormatter())
        handler.addFilter(Filter())
        logger.addHandler(handler)
        return logger
    
    def logger (self,category):
        """set name category for log

        Args:
            category (_type_): _description_

        Returns:
            _type_: _description_
        """
        # if category not in ALLOWCATEGORY: raise ValueError('category not allow')
            
        self._logger = self._make_logger(category,f'{LOGPATH}')
        return self
        
    def info (self,msg,body=None):
        """append log info type 

        Args:
            msg (_type_): _description_
            body (_type_, optional): _description_. Defaults to None.
        """
        self._logger.info(msg=msg, extra={'body':body})
    
    def warn (self,msg,body=None):
        self._logger.warning(msg=msg, extra={'body':body})
    def error (self,msg,body=None):
        self._logger.error(msg=msg, extra={'body':body})
    def exception (self,msg,body=None):
        self._logger.exception(msg=msg, extra={'body':body})

