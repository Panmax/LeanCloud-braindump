# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from leancloud import Query

from ..controllers.user import UserModel


class LoginForm(Form):
    email = StringField(
        'Email',
        validators=[DataRequired(), Length(1, 254), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(Form):
    email = StringField('Email',
                        validators=[DataRequired(), Length(1, 254), Email()])
    username = StringField('Username',
                           validators=[DataRequired(), Length(1, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Username must have only letters, '
                                                                             'numbers, dots or underscores')])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if UserModel.check_email_exist(field.data.lower()):
            raise ValidationError('Email alread registered.')

    def validate_username(self, field):
        if UserModel.check_username_exist(field.data):
            raise ValidationError('Username already in user')
