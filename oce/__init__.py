from secrets import token_urlsafe

from argon2 import PasswordHasher
from flask import Flask
from flask_dance.contrib.github import make_github_blueprint, github
from flask_login import LoginManager
from flask_session import Session
import os

# for forum
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

login_manager = LoginManager()
password_hasher = PasswordHasher()

# for forum
db = SQLAlchemy() 
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['DB_NAME'] = 'oce.db'  # TODO: extract into config file
    app.secret_key = token_urlsafe(32)  # TODO: extract into config file
    login_manager.init_app(app)
    app.config['SESSION_TYPE'] = 'filesystem'  # Store session data in files
    app.config['SESSION_PERMANENT'] = False  # Ensure session resets properly

    Session(app)
    
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    #Github OAuth config
    github_blueprint = make_github_blueprint()
    app.register_blueprint(github_blueprint, url_prefix="/github_login")

    from oce.accounts.routes import accounts
    from oce.content.routes import content
    from oce.errors.handlers import errors
    from oce.forum.routes import forum

    
    app.register_blueprint(accounts)
    app.register_blueprint(content)
    app.register_blueprint(errors)
    app.register_blueprint(forum)

    return app
