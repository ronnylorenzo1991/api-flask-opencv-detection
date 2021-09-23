from flask import Flask, render_template
from flask_cors import CORS
from config import DevelopmentConfig
from flask_migrate import Migrate
from models import db
from routes.camera_bp import camera_bp
from routes.event_bp import event_bp
from routes.weight_bp import weight_bp
from routes.task_bp import task_bp
from routes.default_bp import default_bp
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
from sockets.camera_ws import *

db.init_app(app)
socketio.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(camera_bp, url_prefix='/camera')
app.register_blueprint(event_bp, url_prefix='/event')
app.register_blueprint(weight_bp, url_prefix='/weight')
app.register_blueprint(default_bp, url_prefix='/default')
app.register_blueprint(task_bp, url_prefix='/task')

def index():
    return render_template('index.html')

if __name__ == '__main__':
    db = SQLAlchemy(app)
    ma = Marshmallow(app)
    socketio.run(app)