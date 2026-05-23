import json

from flask import jsonify

from src.database.s3.s3_service import S3Sevice
from src.error_handler.error_handler import ErrorHandler
from src.server_config.service.cache import Cache


class WebService:
    _instance = None
    _init = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._init:
            return
        super().__init__()
        self.S3Service = S3Sevice()
        self.ErrorHandler = ErrorHandler().logger("web service")
        self._init = True

    def _get_index_image(self):
        return self.S3Service.get_all_web_presigned_urls()

    def get_index_setting(self) -> tuple[dict, int]:
        try:
            with open("static/website_setting.json", "r") as setting:
                settings = json.load(setting)
            settings["images"] = self._get_index_image()
        except Exception as e:
            self.ErrorHandler.error("failed to get web setting", str(e))
            return {}
        return settings
