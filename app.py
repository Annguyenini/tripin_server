from flask import Flask, render_template, jsonify, request, send_file, abort,Blueprint
from flask_cors import CORS
from flask_mail import Mail, Message
from src.credential.credential_route import AuthServer
from src.server_auth.server_auth import ServerAuth
from src.mail.mail_config import MailConfig
from src.trip_service.trip_route import TripRoute
from src.user.user_route import UserRoute
import getpass
import json
import io
import sys

mail =Mail()
class Server:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self._register_blueprints()
        self.app.config.from_object(MailConfig)
        mail.init_app(self.app)
        
    def _register_blueprints(self):
        auth_server = AuthServer()
        trip_server = TripRoute()
        user_server = UserRoute()
        self.app.register_blueprint(auth_server.bp,url_prefix="/auth")
        self.app.register_blueprint(trip_server.bp,url_prefix="/trip")
        self.app.register_blueprint(user_server.bp,url_prefix="/user")
        
        


server_auth_service = ServerAuth()
if not server_auth_service.verify_indentity():
    print("Wrong password!❌")
    sys.exit(1)
print("Successfully authenticated!✅")
server = Server()
app = server.app
# app.debug = True
if __name__ =="__main__":
    print("initialize s3")
    print(app.url_map)
    app.run( host ="0.0.0.0", port =8000)

    # app.run( host ="0.0.0.0", port =8000,ssl_context=("src/assets/https/cert.pem", "src/assets/https/key.pem"))
    