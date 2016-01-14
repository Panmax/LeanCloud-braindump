# -*- coding: utf-8 -*-
from flask import render_template, redirect, request, url_for, flash, \
    session, jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user
from leancloud import Query

from . import auth
from app import github
from .forms import RegistrationForm, LoginForm
from ..models import _User as User, Notebook


@auth.route('/login', methods=['GET', 'POST'])
@auth.route('/login/<auth>', methods=['GET', 'POST'])
def login(auth=None):
    form = LoginForm()
    if form.validate_on_submit():
        user = User.login_with_email(email=form.email.data.lower().strip(), password=form.password.data)
        if user is not None:
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password')
    elif auth == 'github':
        return github.authorize(callback=url_for('auth.authorized', _external=True, auth='github'))
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.register(form.email.data.lower(), form.username.data, form.password.data)
        Notebook.create_default_notebook(user.id)
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    if 'github_token' in session:
        session.pop('github_token', None)
    flash('You hava been lgged out.')
    return redirect(url_for('main.index'))


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    pass


@auth.route('/login/authorized/<auth>')
def authorized(auth):
    resp = {}
    success = 0
    if auth == 'github':
        resp = github.authorized_response()
        if resp is None:
            flash('You denied the request to sign in.')
            return redirect(request.args.get('next') or url_for('main.index'))
        session['github_token'] = (resp['access_token'], '')
        success = 1
    if success == 1:
        me = github.get('user')
        user = Query(User).equal_to('email', me.data['email']).find()
        if not user:
            user = User.register(me.data['email'], me.data['login'], resp['access_token'])
            Notebook.create_default_notebook(user.id)
        else:
            user = user[0]
        login_user(user)
        return redirect(request.args.get('next') or url_for('main.index'))


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')