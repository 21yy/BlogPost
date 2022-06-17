#coding:utf-8
import wtforms
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Optional


class CommentForm(FlaskForm):
    name = StringField(u'nickname', validators=[DataRequired()])
    email = wtforms.EmailField(u'email', validators=[DataRequired(), Length(1, 64)])
    content = TextAreaField(u'content', validators=[DataRequired(), Length(1, 1024)])
    follow = StringField(validators=[DataRequired()])
