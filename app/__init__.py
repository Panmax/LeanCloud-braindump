# -*- coding: utf-8 -*-

from flask import Flask

__author__ = 'pan'


def create_app(config_name):
    app = Flask(__name__)

    return app
