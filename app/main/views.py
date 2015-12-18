# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, abort, current_app, request
from flask.ext.login import current_user, login_required

from . import main
from .forms import NoteForm
from ..controllers.user import UserModel
from ..controllers.note import NoteModel, NotebookModel
__author__ = 'pan'


@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated():
        notes = NoteModel.get_user_notes(current_user.id)
        return render_template('app/app.html', notes=notes)
    else:
        stats = []
        users = UserModel.get_all_count()
        stats.append(users)
        notes = NoteModel.get_all_count()
        stats.append(notes)
        return render_template('index.html', stats=stats)


@main.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = NoteForm()
    form.notebook.choices = [(n.id, n.title) for n in NotebookModel.get_user_notebooks(current_user.id)]
    if form.validate_on_submit():
        note = NoteModel.add(title=form.title.data, body=form.body.data,
                             body_html=form.body_html.data, notebook_id=form.notebook.data,
                             author=current_user._get_current_object())
        tags = []
        if not len(form.tags.data) == 0:
            for tag in form.tags.data.split(','):
                tags.append(tag.replace(' ', ''))
            note.str_tags = (tags)
        return redirect(url_for('.index'))
    return render_template('app/add.html', form=form)


@main.route('/note/<id>')
@login_required
def note(id):
    note = None
    if current_user != note.author:
        abort(403)
    return render_template('app/note.html', notes=[note])


@main.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    pass


@main.route('/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    pass


@main.route('/notebooks', methods=['GET', 'POST'])
@login_required
def notebooks():
    pass


@main.route('/notebook/<id>')
@login_required
def notebook(id):
    pass


@main.route('/share/<id>', methods=['GET', 'POST'])
@login_required
def share(id):
    pass


@main.route('/favorite/<id>', methods=['GET', 'POST'])
@login_required
def favorite(id):
    pass
