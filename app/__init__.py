from flask import Flask
from config import Config
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app)

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

photos = UploadSet('photos', IMAGES)
uploads = configure_uploads(app, photos)
patches = patch_request_class(app)  # set maximum file size, default is 16MB

# Notice how socketio.run takes care of app instantiation as well.
from app import routes, models
if __name__ == '__main__':
	socketio.run(app, debug=True)


