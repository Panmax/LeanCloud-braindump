# -*- coding: utf-8 -*-
from leancloud import Query
from leancloud import Object as LObject
from leancloud import Relation

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
    def is_favorite(self):
        return self.get('is_favorite')

    @property
    def updated_date(self):
        return self.get('updatedAt')

    def get_notebook(self, id):
        notebook = Query(Notebook).get(id)
        return notebook

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


class Notebook(LObject):
    @property
    def title(self):
        return self.get('title')


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
