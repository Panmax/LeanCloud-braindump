# -*- coding: utf-8 -*-
import os
__author__ = 'pan'


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


config = {
    'development': DevelopmentConfig,

    'default': DevelopmentConfig
}

GITHUB_SETTINGS = {
    'consumer_key': '052931ef384d23238629',
    'consumer_secret': 'cdfb2181b736abb56a26565ce16e09c676d3d535',
    'request_token_params': {'scope': 'user:email'},
    'base_url': 'https://api.github.com/',
    'request_token_url': None,
    'access_token_method': 'POST',
    'access_token_url': 'https://github.com/login/oauth/access_token',
    'authorize_url': 'https://github.com/login/oauth/authorize'
}
