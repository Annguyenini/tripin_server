from flask import Flask, render_template, jsonify, request, send_file, abort,Blueprint
from flask_cors import CORS
from flask_mail import Mail, Message
from src.credential.credential_route import AuthServer
from src.server_auth.server_auth import ServerAuth
from src.mail.mail_config import MailConfig
from src.trip_service.trip_route import TripRoute
from src.trip_service.trip_contents.trip_contents_route import TripContentsRoute
from src.user.user_route import UserRoute
import getpass
import json
import io
import sys
import threading
from src.contents_sync.contents_sync_route import ContentsSyncRoute
import logging
from logging.handlers import RotatingFileHandler
import sentry_sdk
import dotenv
import os 
mail =Mail()
dotenv.load_dotenv('.env')

class Server:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self._register_blueprints()
        self.app.config.from_object(MailConfig)
        mail.init_app(self.app)
        
    def _register_blueprints(self):
        auth_route = AuthServer()
        trip_route = TripRoute()
        trip_contents_route = TripContentsRoute()
        user_route = UserRoute()
        sync_route = ContentsSyncRoute()
        self.app.register_blueprint(auth_route.bp,url_prefix="/auth")
        self.app.register_blueprint(trip_route.bp,url_prefix="/trip")
        self.app.register_blueprint(trip_contents_route.bp,url_prefix ="/trip-contents")
        self.app.register_blueprint(user_route.bp,url_prefix="/user")
        self.app.register_blueprint(sync_route.bp,url_prefix="/sync")
        
        self.app.route("/health",methods=['GET'])(self.health)    
        self.app.route("/",methods =['GET'])(self.landing)
        
    def health(self):
        return jsonify({'code':'success'}),200
    def landing(self):
        return render_template('index.html')
        
def run_sentry_log():
    sentry_dns = os.getenv('SENTRY_DNS')
    print(sentry_dns)
    sentry_sdk.init(
        dsn=sentry_dns,
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
        enable_logs=True,
    )
    sentry_sdk.logger.info('This is an info log message')


server_auth_service = ServerAuth()
server_auth_service.skip_indentity()
# if not server_auth_service.verify_indentity():
#     print("Wrong password!❌")
#     sys.exit(1)
# print("Successfully authenticated!✅")
server = Server()

run_sentry_log()
app = server.app
if __name__ =="__main__":
    print("initialize s3")
    print(app.url_map)
    print('ver 3')
   
    # run_tasks()
    app.run( host ="0.0.0.0", port =8000,debug= True)
    # app.run( host ="0.0.0.0", port =8000,ssl_context=("src/assets/https/cert.pem", "src/assets/https/key.pem"))
    