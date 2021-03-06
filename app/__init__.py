# -*- coding: utf-8 -*-

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask_oauthlib.client import OAuth

from config import config, GITHUB_SETTINGS

__author__ = 'pan'

bootstrap = Bootstrap()
login_manager = LoginManager()
moment = Moment()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
oauth = OAuth()
github = oauth.remote_app('github', **GITHUB_SETTINGS)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
