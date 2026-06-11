import os

from dotenv import load_dotenv, set_key
from flask import Flask
from flask_mail import Mail, Message

from src.server_config.config import Config

config = Config()
load_dotenv(config.env_path)


class MailConfig:
    MAIL_SERVER = os.getenv("EMAIL_SERVER")
    MAIL_PORT = os.getenv("EMAIL_PORT")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv("EMAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("EMAIL_DEFAULT_SENDER")
