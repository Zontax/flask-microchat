from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap  # Фреймворк CSS
from flask_moment import Moment  # Час UTF
from flask_babel import Babel  # Зміна LANG

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)  # Представляє БД
migrate = Migrate(app, db)  # Представляє механізм міграції
login = LoginManager(app)
login.login_view = 'login'
login.login_message = "Увійдіть щоб побачити цю сторінку"

mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
babel = Babel(app)

from app import routes, models  # import після БД
