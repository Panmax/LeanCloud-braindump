# -*- coding: utf-8 -*-
from flask import abort
from flask.ext.login import UserMixin, current_user, AnonymousUserMixin

from leancloud import Query
from leancloud import Object as LObject, user
from leancloud import Relation
from leancloud import LeanCloudError

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


    @classmethod
    def check_email_exist(cls, email):
        if Query(cls).equal_to('email', email).find():
            return True
        return False

    @classmethod
    def check_username_exist(cls, username):
        if Query(cls).equal_to('username', username).find():
            return True
        return False

    @classmethod
    def register(cls, email, username, password):
        u = user.User(username=username, password=password, email=email)
        u.sign_up()
        return Query(cls).equal_to('username', username).first()

    @classmethod
    def login_with_email(cls, email, password):
        try:
            username = Query(cls).equal_to('email', email).first().get('username')
            u = user.User(username=username, password=password)
            u.login()
        except LeanCloudError as e:
            print e.message
            return None
        else:
            return Query(cls).equal_to('username', username).first()

    @classmethod
    def get_all_count(cls):
        return Query(cls).count()


class AnonymousUser(AnonymousUserMixin):

    def can(self):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Note(LObject):
    @property
    def notebook_id(self):
        return self.get('notebook').id

    @property
    def title(self):
        return self.get('title')

    @property
    def author(self):
        a = self.get('author')
        a.fetch()
        return a

    @property
    def body(self):
        return self.get('body')

    @property
    def body_html(self):
        return self.get('body_html')

    @property
    def is_favorite(self):
        return self.get('is_favorite')

    @property
    def is_deleted(self):
        return self.get('is_deleted')

    @property
    def created_date(self):
        return self.get('createdAt')

    @property
    def updated_date(self):
        return self.get('updatedAt')

    def get_notebook(self, id):
        notebook = Query(Notebook).get(id)
        return notebook

    def update(self, title, body, body_html, notebook_id):
        self.set('title', title)
        self.set('body', body)
        self.set('body_html', body_html)
        self.set('notebook_id', notebook_id)
        self.save()

    def delete(self):
        self.set('is_deleted', True)
        self.save()

    def set_favorite(self, favorite):
        self.set('is_favorite', favorite)
        self.save()

    def _find_or_create_tag(self, tag):
        t = Query(Tag).equal_to('tag', tag).limit(1).find()
        if not t:
            t = Tag()
            t.set('tag', tag.strip())
            t.save()
            return t
        return t[0]

    def _get_tags(self):
        tags = self.relation('tags').query().find()
        return [x.tag for x in tags]

    def _set_tags(self, value):
        tags = self.relation('tags').query().find()
        relation = self.relation('tags')
        while tags:
            relation.remove(tags[0])
        for tag in value:
            relation.add(self._find_or_create_tag(tag))
        self.save()

    # simple wrapper for tags relationship
    str_tags = property(_get_tags,
                        _set_tags)

    @classmethod
    def get_or_404(cls, note_id):
        try:
            note = Query(cls).get(note_id)
        except LeanCloudError as e:
            print e.message
            abort(404)
        else:
            return note

    @classmethod
    def get_user_notes(cls, user_id, is_deleted=False):
        notes = Query(cls).equal_to('author', user.User.create_without_data(user_id)).\
            equal_to('is_deleted', is_deleted).descending('is_favorite').descending('updatedAt').find()
        return notes

    @classmethod
    def get_user_favorite_notes(cls, user_id):
        notes = Query(cls).equal_to('author', user.User.create_without_data(user_id)).equal_to('is_deleted', False)\
            .equal_to('is_favorite', True).descending('updatedAt').find()
        return notes

    @classmethod
    def new(cls, title, body, body_html, notebook_id, author):
        note = cls()
        note.set('title', title)
        note.set('body', body)
        note.set('body_html', body_html)
        note.set('notebook', Notebook.create_without_data(notebook_id))
        note.set('author', author)
        note.save()
        return note

    @classmethod
    def get_all_count(cls):
        return Query(cls).count()


class Notebook(LObject):
    @property
    def title(self):
        return self.get('title')

    @property
    def author(self):
        a = self.get('author')
        a.fetch()
        return a

    @property
    def notes(self):
        return Query(Note).equal_to('notebook', self).find()

    def _show_notes(self):
        notes = []
        for note in self.notes:
            if not note.is_deleted:
                notes.append(note)
        return notes

    @classmethod
    def get_or_404(cls, notebook_id):
        try:
            notebook = Query(cls).get(notebook_id)
        except LeanCloudError, e:
            print e.message
            abort(404)
        else:
            return notebook

    @classmethod
    def get_user_notebooks(cls, user_id):
        notebooks = Query(Notebook).equal_to('author', user.User.create_without_data(user_id)).find()
        return notebooks

    @classmethod
    def add(cls, title, user_id):
        if Query(Notebook).equal_to('author', user.User.create_without_data(user_id)).equal_to('title', title).find():
            return False
        notebook = Notebook()
        notebook.set('title', title)
        notebook.set('author', user.User.create_without_data(user_id))
        notebook.save()
        return True

    @classmethod
    def create_default_notebook(cls, user_id):
        notebook = Notebook()
        notebook.set('title', 'Default')
        notebook.set('author', user.User.create_without_data(user_id))
        notebook.save()


class Tag(LObject):
    @property
    def tag(self):
        return self.get('tag')

    def _get_notes(self):
        notes = []
        all_notes = Relation.reverse_query('Note', 'tags', self).find()
        for note in all_notes:
            author = note.get('author')
            author.fetch()
            if author == current_user:
                notes.append(note)
        return notes

    @classmethod
    def get_by_name(cls, name):
        tag = Query(Tag).equal_to('tag', name).first()
        return tag
