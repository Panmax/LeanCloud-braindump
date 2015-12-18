# -*- coding: utf-8 -*-
from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, current_user

from . import auth
from .forms import RegistrationForm, LoginForm
from ..controllers.user import UserModel
from ..controllers.note import NotebookModel


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = UserModel.login_with_email(email=form.email.data.lower(), password=form.password.data)
        if user is not None:
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = UserModel.register(form.email.data.lower(), form.username.data, form.password.data)
        NotebookModel.create_default_notebook(user.id)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You hava been lgged out.')
    return redirect(url_for('main.index'))


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    pass
