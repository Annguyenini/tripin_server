import re
class InputValidation:
    _instance =None
    _init = False
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._init:
            return
        self._init = True


    def username_validation(self,username:str)->bool:
        if not username:
            return False
        if len(username)<5 or len(username) >10 :
            return False
        # must contain upper case letter, no special char  and start with word 
        check = re.match(r'^(?=.*[A-Z])[a-zA-Z]\w+$',username)
        return True if check else False

    
    def password_validation(self,password:str)->bool:
        if not password:
            return False
        if len(password)<8 or len(password) >15 :
            return False
        # must contain at least 1upper case,1 sepecial char, 1 degit, and start with word 
        check = re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[a-zA-Z]',password)
        return True if check else False
    
    def displayname_validation(self,display_name:str)->bool:
        if not display_name:
            return False
        if len(display_name)<5 or len(display_name) >10 :
            return False
        # must contain upper case letter, no special char
        check = re.match(r'^(?=.*[A-Z])[a-zA-Z]\w+$',display_name)
        return True if check else False
    
    def email_validation(self,email:str)->bool:
        if not email:return False
        # if doesnt have the @ dont bother care
        check = re.match(r'^(?=.*[@])',email)
        return True if check else False
    
    def trip_name_validation(self,trip_name:str)->bool:
        if not trip_name:
            return False
        if len(trip_name)<5 or len(trip_name) >10 :
            return False
        # no special char  and start with word 
        check = re.match(r'^[a-zA-Z]\w+$',trip_name)
        return True if check else False
