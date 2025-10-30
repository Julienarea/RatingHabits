from flask import Flask

from flask_login import LoginManager
import os

application = Flask(__name__)
application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'


# Настройка Flask-Login

login_manager = LoginManager()

login_manager.init_app(application)

login_manager.login_view = 'login'

login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'


from app.views import routes

