import logging
import json
import traceback
import os
from types import SimpleNamespace
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "time": self.formatTime(record),
            "type": record.levelname,
            "message": record.getMessage(),
            "body": getattr(record, 'body', None) or (''.join(traceback.format_exception(*record.exc_info)) if record.exc_info else None)
        }
        return json.dumps(log)

LOGDIR = './logs/errorlogs'
class ErrorHandler:
    def __init__(self):
        self._logger = None
        if not os.path.exists(LOGDIR):
            os.makedirs(LOGDIR)        
        
    def _make_logger(self,name,file):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(file)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        return logger
    
    def logger (self,category):
        ALLOWCATEGORY = ['auth','database','trip']
        if category not in ALLOWCATEGORY: raise ValueError('category not allow')
        self._logger = self._make_logger(category,f'{LOGDIR}/{category}.log')
        
    def info (self,msg,body=None):
        self._logger.info(msg=msg, extra={'body':body})
    def warn (self,msg,body=None):
        self._logger.warning(msg=msg, extra={'body':body})
    def error (self,msg,body=None):
        self._logger.error(msg=msg, extra={'body':body})
    def exception (self,msg,body=None):
        self._logger.exception(msg=msg, extra={'body':body})
