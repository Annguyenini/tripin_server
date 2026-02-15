from flask import Blueprint,request,jsonify ,render_template
class AdminRoute:
    _instance = None
    _init = False
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        if self._init: return
        self.bp = Blueprint('admin',__name__)
        self._init = True

    def _register_route(self):
        self.bp.route('/portal',methods =['GET'])(self.portal)
    
    def portal(self):
        return render_template('admin.html')