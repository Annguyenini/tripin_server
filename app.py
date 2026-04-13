from flask import Flask, render_template, jsonify, request, send_file, abort,Blueprint
from werkzeug.exceptions import HTTPException

from flask_cors import CORS
from flask_mail import Mail, Message
# from flask_admin import Admin
from src.credential.credential_route import AuthServer
from src.server_auth.server_auth import ServerAuth
from src.mail.mail_config import MailConfig
from src.trip_service.trip_route import TripRoute
from src.trip_service.trip_contents.trip_contents_route import TripContentsRoute
from src.user.user_route import UserRoute
from src.trip_view.trip_view_route import TripViewRoute

from src.contents_sync.contents_sync_route import ContentsSyncRoute
from logging.handlers import RotatingFileHandler
import dotenv
import os 
from src.server_config.discord_error_logs import discord_error_logs,discord_request_logs,start_server_status_thread
import traceback
import datetime
from bootstraps.bootstrap_manager import bootstrap_manager
from src.error_handler.error_handler import ErrorSSE,ErrorHandler
bootstrap_manager()
mail =Mail()
dotenv.load_dotenv('.env')

class Server:
    def __init__(self):
        self.app = Flask(__name__)
        # self.admin = Admin()
        # self.admin.init_app(self.app)
        CORS(self.app,
             resources={
                 r"/internal/*":{'origins':'http://127.0.0.1:5000','supports_credentials':True}
             })
        print(self.app.extensions)
        self._register_blueprints()
        self.app.config.from_object(MailConfig)
        mail.init_app(self.app)
        
    def _register_blueprints(self):
        auth_route = AuthServer()
        trip_route = TripRoute()
        trip_contents_route = TripContentsRoute()
        user_route = UserRoute()
        sync_route = ContentsSyncRoute()
        trip_view_route = TripViewRoute()
        internal_error_route = ErrorSSE()
        self.app.register_blueprint(auth_route.bp,url_prefix="/auth")
        self.app.register_blueprint(trip_route.bp,url_prefix="/trip")
        self.app.register_blueprint(trip_contents_route.bp,url_prefix ="/trip-contents")
        self.app.register_blueprint(user_route.bp,url_prefix="/user")
        self.app.register_blueprint(sync_route.bp,url_prefix="/sync")
        self.app.register_blueprint(trip_view_route.bp,url_prefix ="/trip-view")
        self.app.register_blueprint(internal_error_route.bp,url_prefix="/internal")
        self.app.route('/test-error',methods=['GET'])(self.test_error)
        self.app.route("/health",methods=['GET'])(self.health)    
        self.app.route("/",methods =['GET'])(self.landing)
        # self.app.route("/testmap",methods =['GET'])(self.testmap)

        # self.app.route("/trip-view",methods =['GET'])(self.trip_view)
        self.app.errorhandler(404)(self.error_404_site)
        # self.app.errorhandler(500)(self.error_500_site)
        self.app.errorhandler(HTTPException)(self.error_exception_log)
        self.app.errorhandler(Exception)(self.error_exception_log)
        self.app.after_request(self.log_request)

        
    def testmap(self):
        return render_template('testmap.html')

    def test_error(self):
        
        1/0
    def health(self):
        return jsonify({'code':'success'}),200
    def landing(self):
        return render_template('index.html')
    def trip_view(self):
        return render_template('trip_view.html')
    def error_404_site(self,e):
        return render_template('404.html'),404
    def error_500_site(self,e):
        print('dsdsd')
        return render_template('500.html'),500
    def error_exception_log(self,e):

        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M")
        trace = traceback.format_exc()
        route = request.path
        method = request.method
        ip = request.remote_addr
        ErrorHandler().logger('Exception').error(f"Error at {route} | {method}",body= trace)
        # build embed message
        description = f"**Route:** {route}\n**Method:** {method}\n**IP:** {ip}\n**Time:** {timestamp}\n```{trace}```"
        discord_error_logs( description )

        # return JSON to client
        return jsonify({"error": f"internal server error: {e}"}), 500
    
        
    def log_request(self,response):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M")
        discord_request_logs(f"[{timestamp}] \nMethod:{request.method} \nURI:{request.url} \nIP:{request.remote_addr} \nCode:{response.status_code}",response.status_code)
        return response





server_auth_service = ServerAuth()
server_auth_service.skip_indentity()
server = Server()


start_server_status_thread()


app = server.app

DEBUG = os.getenv('DEBUG') or False
def create_app():
    return server.app
if __name__ =="__main__":
    print("initialize s3")
    print(app.url_map)
    print('ver 5')
   
    # run_tasks()
    app.run( host ="0.0.0.0", port =8000,debug=True if DEBUG else False)
    # app.run( host ="0.0.0.0", port =8000,ssl_context=("src/assets/https/cert.pem", "src/assets/https/key.pem"))
    
    
    