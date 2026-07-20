import json
import datetime
import os
import traceback
from logging.handlers import RotatingFileHandler

import dotenv
from flask import (
    Blueprint,
    Flask,
    abort,
    jsonify,
    render_template,
    request,
    send_file,
    send_from_directory,
)
from flask_cors import CORS
from flask_mail import Mail, Message
from flask_socketio import SocketIO
from werkzeug.exceptions import HTTPException

from bootstraps.bootstrap_manager import bootstrap_manager

# from flask_admin import Admin
from src.credential.credential_route import AuthServer
from src.error_handler.error_handler import ErrorHandler, ErrorSSE
from src.friendships.friendships_routes import FriendShipRoutes
from src.mail.mail_config import MailConfig
from src.server_config.discord_error_logs import (
    discord_error_logs,
    discord_request_logs,
    start_server_status_thread,
)
from src.trip_contents.trip_contents_routes import TripContentRoutes
from src.trip_service.trip_route import TripRoute
from src.user.user_route import UserRoute
from src.user_setting.user_setting_route import UserSettingsRoutes
from src.users.trips.trip_routes import UsersTripDataRoutes
from src.users.users_routes import UsersRoutes
from src.web.trip_view.trip_view_route import TripViewRoute
from src.web.web_service import WebService
from src.websocket.connection import Notification, Socket
import redis
bootstrap_manager()
mail = Mail()
dotenv.load_dotenv(".env")


class Server:
    def __init__(self):
        self.app = Flask(__name__)
        # self.admin = Admin()
        # self.admin.init_app(self.app)
        CORS(
            self.app,
            resources={
                r"/internal/*": {
                    "origins": "http://127.0.0.1:5000",
                    "supports_credentials": True,
                }
            },
        )
        print(self.app.extensions)
        self._register_blueprints()
        self.app.config.from_object(MailConfig)
        self.WebSetting = WebService()
        mail.init_app(self.app)

    def _register_blueprints(self):
        auth_route = AuthServer()
        trip_route = TripRoute()
        user_route = UserRoute()
        user_settings_route = UserSettingsRoutes()
        trip_view_route = TripViewRoute()
        trip_content_routes = TripContentRoutes()
        internal_error_route = ErrorSSE()
        friendships_route = FriendShipRoutes()
        profile_routes = UsersRoutes()
        users_trip = UsersTripDataRoutes()
        self.app.register_blueprint(auth_route.bp, url_prefix="/auth")
        self.app.register_blueprint(trip_route.bp, url_prefix="/trip")

        self.app.register_blueprint(trip_content_routes.bp, url_prefix="/trip-contents")

        self.app.register_blueprint(user_route.bp, url_prefix="/user")
        self.app.register_blueprint(trip_view_route.bp, url_prefix="/trip-view")
        self.app.register_blueprint(internal_error_route.bp, url_prefix="/internal")
        self.app.register_blueprint(user_settings_route.bp, url_prefix="/user-settings")
        self.app.register_blueprint(friendships_route.bp, url_prefix="/friend")
        self.app.register_blueprint(profile_routes.bp, url_prefix="/users")
        self.app.register_blueprint(users_trip.bp, url_prefix="/users")

        self.app.route("/", methods=["GET"])(self.landing)
        self.app.route("/app-version", methods=["GET"])(self.app_version)
        self.app.route("/privacy", methods=["GET"])(self.privacy)
        self.app.route("/policy-text", methods=["GET"])(self.policy_text)
        self.app.route("/health", methods=["GET"])(self.health)
        self.app.route("/testsocket", methods=["GET"])(self.test_socket)

        # self.app.route("/testmap",methods =['GET'])(self.testmap)

        # self.app.route("/trip-view",methods =['GET'])(self.trip_view)
        self.app.errorhandler(404)(self.error_404_site)
        # self.app.errorhandler(500)(self.error_500_site)
        self.app.errorhandler(HTTPException)(self.error_exception_log)
        self.app.errorhandler(Exception)(self.error_exception_log)
        self.app.after_request(self.log_request)
        self.redis = redis.Redis(
            host=os.environ.get("REDIS_HOST"),
            port=os.environ.get("REDIS_PORT"),
            decode_responses=True,
        )

    def health(self):
        return {"ok": "okeluon okela"}, 200

    def testmap(self):
        return render_template("testmap.html")

    def app_version(self):
        return jsonify({"version": f"{os.getenv('APP_VERSION')}"}), 200

    def policy_text(self):
        return send_from_directory("static", "policy.txt", mimetype="text/plain")

    def privacy(self):
        return render_template("policy.html"), 200

    def landing(self):
        settings = self.WebSetting.get_index_setting()
        return render_template("index.html", settings=settings)

    def trip_view(self):
        return render_template("trip_view.html")

    def error_404_site(self, e):
        return render_template("404.html"), 404

    def error_500_site(self, e):
        print("dsdsd")
        return render_template("500.html"), 500

    def error_exception_log(self, e):

        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M")
        trace = traceback.format_exc()
        route = request.path
        method = request.method
        ip = request.remote_addr
        ErrorHandler().logger("Exception").error(
            f"Error at {route} | {method}", body=str(trace)
        )
        # build embed message
        description = f"**Route:** {route}\n**Method:** {method}\n**IP:** {ip}\n**Time:** {timestamp}\n```{trace}```"
        discord_error_logs(description)

        # return JSON to client
        return jsonify({"error": f"internal server error: {e}"}), 500

    def log_request(self, response):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M")
        discord_request_logs(
            f"[{timestamp}] \nMethod:{request.method} \nURI:{request.url} \nIP:{request.remote_addr} \nCode:{response.status_code}",
            response.status_code,
        )
        return response

    def test_socket(self):


        self.redis.publish('notifications', json.dumps({'room_id':'user:1','data':'data','event_type':'friend_removed'}))
        return {'code':'code'},200


server = Server()

start_server_status_thread()
app = server.app
# socket = Socket(app=app)
# redisnotification = Notification(socketIO=socket)
# redisnotification.start_listener_thread()
DEBUG = os.getenv("DEBUG") or False


def create_app():
    return server.app


# socket = SocketIO

if __name__ == "__main__":
    print("initialize s3")
    print(app.url_map)
    print("ver 5")

    # socket
    # socket.init_app(app=app)
    # run_tasks()
    app.run(host="0.0.0.0", port=8000,debug=DEBUG)


    # socket.socketIO.run(app,host="0.0.0.0",port=8000)
    # app.run( host ="0.0.0.0", port =8000,ssl_context=("src/assets/https/cert.pem", "src/assets/https/key.pem"))
