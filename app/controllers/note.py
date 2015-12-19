# -*- coding: utf-8 -*-
from flask import abort

from leancloud import Query, LeanCloudError
from leancloud import user
from ..models import Note, Notebook, Tag

__author__ = 'pan'


class NoteModel(object):
    def __init__(self, note_id=None):
        self.note_id = note_id
        self.query = Query(Note)

    def get_or_404(self):
        try:
            note = self.query.get(self.note_id)
        except LeanCloudError as e:
            print e.message
            abort(404)
        else:
            return note

    def update(self, title, body, body_html, notebook_id):
        note = self.get_or_404()
        note.set('title', title)
        note.set('body', body)
        note.set('body_html', body_html)
        note.set('notebook_id', notebook_id)
        note.save()

    def delete(self):
        note = self.get_or_404()
        note.set('is_deleted', True)
        note.save()

    @classmethod
    def set_favorite(cls, note, favorite):
        note.set('is_favorite', favorite)
        note.save()

    @classmethod
    def add(cls, title, body, body_html, notebook_id, author):
        note = Note()
        note.set('title', title)
        note.set('body', body)
        note.set('body_html', body_html)
        note.set('notebook', Notebook.create_without_data(notebook_id))
        note.set('author', author)
        note.save()
        return note

    @classmethod
    def get_all_count(cls):
        return Query(Note).count()

    @classmethod
    def get_user_notes(cls, user_id, is_deleted=False):
        notes = Query(Note).equal_to('author', user.User.create_without_data(user_id)).\
            equal_to('is_deleted', is_deleted).descending('is_favorite').descending('updatedAt').find()
        return notes

    @classmethod
    def get_user_favorite_notes(cls, user_id):
        notes = Query(Note).equal_to('author', user.User.create_without_data(user_id)).equal_to('is_deleted', False)\
            .equal_to('is_favorite', True).descending('updatedAt').find()
        return notes


class NotebookModel(object):
    def __init__(self, notebook_id):
        self.notebook_id = notebook_id
        self.query = Query(Notebook)

    def get_or_404(self):
        try:
            notebook = self.query.get(self.notebook_id)
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


class TagModel(object):
    @classmethod
    def get_by_name(cls, name):
        tag = Query(Tag).equal_to('tag', name).first()
        return tag
