# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, abort, current_app, request
from flask.ext.login import current_user, login_required

from . import main
from .forms import NoteForm, ShareForm, NotebookForm
from ..controllers.user import UserModel
from ..controllers.note import NoteModel, NotebookModel, TagModel
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


@main.route('/news')
def news():
    if current_user.is_authenticated():
        return render_template('app/news.html')
    return render_template('news.html')


@main.route('/settings')
@login_required
def settings():
    pass


@main.route('/trash', methods=['GET', 'POST'])
@login_required
def trash():
    if current_user.is_authenticated():
        notes = NoteModel.get_user_notes(current_user.id, is_deleted=True)
        if not notes:
            flash("Trash is empty, you are so Tidy!")
            return redirect(url_for('.index'))
        return render_template('app/trash.html', notes=notes)
    else:
        return render_template('index.html')


@main.route('/note/<id>')
@login_required
def note(id):
    note = NoteModel(id).get_or_404()
    if current_user != note.author:
        abort(403)
    return render_template('app/note.html', notes=[note])


@main.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    note = NoteModel(id).get_or_404()
    if current_user != note.author:
        abort(403)
    form = NoteForm(notebook=note.notebook_id)
    form.notebook.choices = [(n.id, n.title) for n in NotebookModel.get_user_notebooks(current_user.id)]
    if form.validate_on_submit():
        NoteModel(note.id).update(title=form.title.data, body=form.body.data,
                            body_html=form.body_html.data, notebook_id=form.notebook.data)
        tags = []
        if not len(form.tags.data) == 0:
            for tag in form.tags.data.split(','):
                tags.append(tag.replace(' ', ''))
        note.str_tags = (tags)
        flash('The note has been updated.')
        return redirect(url_for('.index'))
    form.title.data = note.title
    form.body.data = note.body
    form.tags.data = ', '.join(note._get_tags())
    return render_template('app/edit_note.html', note=note, form=form)


@main.route('/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    note = NoteModel(id).get_or_404()
    if current_user != note.author:
        abort(403)
    else:
        NoteModel(id).delete()
        flash('The note has been deleted.')
        return redirect(url_for('.index'))


@main.route('/tag/<name>')
@login_required
def tag(name):
    tag = TagModel.get_by_name(name)
    notes = tag._get_notes()
    return render_template('app/tag.html', notes=notes, tag=name)


@main.route('/notebooks', methods=['GET', 'POST'])
@login_required
def notebooks():
    form = NotebookForm()
    if form.validate_on_submit():
        if not NotebookModel.add(form.title.data, current_user.id):
            flash('A notebook with name {0} already exists.'.format(form.title.data))
        return redirect(url_for('.notebooks'))
    notebooks = NotebookModel.get_user_notebooks(current_user.id)
    return render_template('app/notebooks.html', notebooks=notebooks, form=form)


@main.route('/notebook/<id>')
@login_required
def notebook(id):
    notebook = NotebookModel(id).get_or_404()
    if current_user != notebook.author:
        abort(403)
    return render_template('app/notebook.html', notebook=notebook, notes=notebook._show_notes())


@main.route('/share/<id>', methods=['GET', 'POST'])
@login_required
def share(id):
    note = NoteModel(id).get_or_404()
    if current_user != note.author:
        abort(403)
    form = ShareForm()
    if form.validate_on_submit():
        pass
    return render_template('app/share_note.html', form=form, notes=[note])


@main.route('/favorite/<id>', methods=['GET', 'POST'])
@login_required
def favorite(id):
    note = NoteModel(id).get_or_404()
    if current_user != note.author:
        abort(403)
    else:
        if not note.is_favorite:
            NoteModel.set_favorite(note, True)
            flash('Note marked as favorite')
        else:
            NoteModel.set_favorite(note, False)
            flash('Note removed as favorite')
        return redirect(url_for('.index'))


@main.route('/favorites', methods=['GET'])
@login_required
def favorites():
    notes = NoteModel.get_user_favorite_notes(current_user.id)
    return render_template('app/app.html', notes=notes)
