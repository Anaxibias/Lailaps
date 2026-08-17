from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from config import Config

app = Flask(__name__)

app.config.from_object(Config)
app.jinja_env.auto_reload = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
bootstrap = Bootstrap5(app)

from app.services import service_bp
from app.api import api_bp
from app.utils import utils_bp

app.register_blueprint(service_bp)
app.register_blueprint(api_bp)
app.register_blueprint(utils_bp)

from app import routes, models
