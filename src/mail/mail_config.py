from flask import Flask
from flask_mail import Mail, Message
import os 
from src.server_config.config import Config
from dotenv import set_key, load_dotenv
config = Config()
load_dotenv(config.env_path)

class MailConfig:
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

