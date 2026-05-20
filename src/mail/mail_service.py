from operator import sub

from flask_mail import Mail, Message

from src.error_handler.error_handler import ErrorHandler
from src.server_config.service.cache import Cache

mail = Mail()


class MailService:
    _instance = None
    _initialize = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialize:
            self.ErrorHandler = ErrorHandler().logger("Email Service")
            self._initialize = True
        return

    def _send_email(self, recipients: list, subject: str, body: str):
        try:
            msg = Message(subject=subject, recipients=[recipients], body=body)
            mail.send(msg)
        except Exception as e:
            self.ErrorHandler.error("failed at send code", {e})
            return False


class CredentialEmailService(MailService):
    # Assuming all the input pass in is ALREADY validate
    _instance = None
    _initialize = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialize:
            return
        self.ErrorHandler = ErrorHandler().logger("Credential Email Service")
        self.CacheService = Cache()
        self._initialize = True

    def send_email_confirmation_code(self, code: str, recipient: str):
        # send email code to user and set code in cache
        subject = "Email Confirmation Code"
        message = f"Your Email Confirmation Code: {code} \n nananana =))"
        self._send_email(recipients=recipient, subject=subject, body=message)
        return
