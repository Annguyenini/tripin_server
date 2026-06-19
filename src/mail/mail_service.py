from operator import sub, truediv

from flask_mail import Mail, Message

from src.error_handler.error_handler import ErrorHandler
from src.utils.cache.cache import Cache

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

    def _send_email(self, recipients: list, subject: str, html, sender):
        try:
            msg = Message(
                subject=subject,
                recipients=recipients,
                html=html,
                sender=sender,
            )
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
        try:
            subject = "Email Confirmation Code"
            html_body = f"""
            <div style="font-family: sans-serif; max-width: 480px; margin: auto; padding: 24px;">
              <h2 style="color: #2a201a;">Email Confirmation</h2>
              <p style="color: #555;">Use the code below to confirm your email:</p>

              <div style="
                font-size: 32px;
                font-weight: bold;
                letter-spacing: 8px;
                text-align: center;
                padding: 20px;
                background: #fdf6ee;
                border-radius: 8px;
                color: #2a201a;
                margin: 20px 0;
              ">{code}</div>

              <p style="color: #888; font-size: 12px;">
                This code expires in 5 minutes. If you didn't request this, ignore this email.
              </p>

              <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0"/>
              <p style="margin:0; font-size: 13px; color: #333;"><strong>Tripping</strong></p>
              <p style="margin:4px 0 0; font-size: 12px; color: #888;">
                <a href="https://tripping.live" style="color: #c8a96e; text-decoration: none;">tripping.live</a>
              </p>
              <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0"/>
              <p style="margin:0; font-size: 13px; color: #333;"><strong>Policies</strong></p>
              <p style="margin:4px 0 0; font-size: 12px; color: #888;">
                <a href="https://tripping.live/privacy" style="color: #c8a96e; text-decoration: none;">Privacy Policy</a>
              </p>
            </div>
            """

            subject = "Your Tripping Confirmation Code"
            sender = ("Tripping", "tripper@tripping.live")
            recipients = [recipient]
            self._send_email(
                recipients=recipients,
                subject=subject,
                html=html_body,
                sender=sender,
            )
            return True
        except Exception as e:
            self.ErrorHandler.error("failed to send confirmation code", {e})
            return False
