# -*- coding: utf-8 -*-
from leancloud import Query, LeanCloudError
from leancloud import user
from ..models import _User

__author__ = 'pan'


class UserModel(object):
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.query = Query(_User)

    @classmethod
    def register(cls, email, username, password):
        u = user.User(username=username, password=password, email=email)
        u.sign_up()
        return Query(_User).equal_to('username', username).first()

    @classmethod
    def login_with_email(cls, email, password):
        try:
            username = Query(_User).equal_to('email', email).first().get('username')
            u = user.User(username=username, password=password)
            u.login()
        except LeanCloudError as e:
            print e.message
            return None
        else:
            return Query(_User).equal_to('username', username).first()

    @classmethod
    def check_email_exist(cls, email):
        if Query(_User).equal_to('email', email).find():
            return True
        return False

    @classmethod
    def check_username_exist(cls, username):
        if Query(_User).equal_to('username', username).find():
            return True
        return False

    @classmethod
    def get_all_count(cls):
        return Query(_User).count()
