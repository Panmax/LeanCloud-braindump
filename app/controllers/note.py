# -*- coding: utf-8 -*-
from leancloud import Query, LeanCloudError
from leancloud import user
from ..models import Note, Notebook

__author__ = 'pan'


class NoteModel(object):
    def __init__(self, note_id):
        self.note_id = note_id
        self.query = Query(Note)

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
    def get_user_notes(cls, user_id):
        notes = Query(Note).equal_to('author', user.User.create_without_data(user_id)).\
            equal_to('is_deleted', False).descending('is_favorite').descending('updatedAt').find()
        return notes


class NotebookModel(object):
    def __init__(self, notebook_id):
        self.notebook_id = notebook_id
        self.query = Query(Notebook)

    @classmethod
    def get_user_notebooks(cls, user_id):
        notebooks = Query(Notebook).equal_to('author', user.User.create_without_data(user_id)).find()
        return notebooks

    @classmethod
    def create_default_notebook(cls, user_id):
        notebook = Notebook()
        notebook.set('title', 'Default')
        notebook.set('author', user.User.create_without_data(user_id))
        notebook.save()
