# -*- coding: utf-8 -*-
from leancloud import Query
from leancloud import Object as LObject

from flask.ext.login import UserMixin, current_user, AnonymousUserMixin

from . import login_manager


@login_manager.user_loader
def load_user(user_id):
    return Query(_User).get(user_id)


class _User(UserMixin, LObject):
    @property
    def username(self):
        return self.get('username')

    @property
    def email(self):
        return self.get('email')


class AnonymousUser(AnonymousUserMixin):

    def can(self):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Note(LObject):
    @property
    def title(self):
        return self.get('title')

    @property
    def notebook_id(self):
        return self.get('notebook').id

    @property
    def updated_date(self):
        return self.get('updatedAt')

    def get_notebook(self, id):
        notebook = Query(Notebook).get(id)
        return notebook


class Notebook(LObject):
    @property
    def title(self):
        return self.get('title')


class Tag(LObject):
    pass
