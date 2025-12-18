from flask_mail import Mail, Message
import random
mail = Mail()
class MailService:
    _instance = None
    _initialize = False
    def __new__(cls,*args,**kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance         
    def __init__(self):
        if not self._initialize:
            self.confirmation_list = {}
            self._initialize = True
        return
    def send_confirmation_code(self, recipients:str):
        """ process sending verify code through email

        Args:
            recipients (str): _user email_

        Returns:
            bool: status
        """
        assert recipients is not None, "recipient Null" 
        
        ##random 6digits 
        code = random.randint(100000, 999999) 
        
        ##message
        subject ="Code for Tripin Auth"
        body = f"This is your code for Tripin {code}"
        
        ##send email
        try:
            msg =Message (subject = subject, recipients=[recipients],body=body)
            mail.send(msg)
        except Exception as e:
            print("Error at send mail",e)
            return False
        
        ##append to cache
        email = recipients.strip()
        self.confirmation_list[email]=code
        
        return True
    def verify_code(self,recipients:str, code:int):
        """Call to verify code

        Args:
            recipients (str): email
            code (int): userinput code 

        Returns:
            bool: status
        """
        email = recipients.strip()
                        
        ##correct code
        realcode = self.confirmation_list.get(email)

        if code != realcode:
            return False
        del self.confirmation_list[email]
        
        return True