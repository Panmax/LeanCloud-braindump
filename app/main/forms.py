# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
__author__ = 'pan'


def validate_tags(form, field):
    if field.data:
        for x in field.data.split(','):
            if len(x) not in range(200+1):
                raise ValidationError('All tags must be less than 200 characters')


class NoteForm(Form):
    title = StringField('Title:', validators=[DataRequired(), Length(1, 200)])
    body = TextAreaField('Dump Your Brain:', validators=[DataRequired()])
    body_html = TextAreaField()
    tags = StringField(validators=[])
    notebook = SelectField(coerce=str)
    submit = SubmitField('Submit')
