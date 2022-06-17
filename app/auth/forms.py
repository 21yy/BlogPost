# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, Email


class LoginForm(FlaskForm):
    email = EmailField(u'email', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField(u'password', validators=[DataRequired()])