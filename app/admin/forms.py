from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, EmailField, \
    PasswordField
from wtforms.validators import DataRequired, Length, EqualTo
from ..main.forms import CommentForm


class CommonForm(FlaskForm):
    types = SelectField(u'post category', coerce=int, validators=[DataRequired()])
    source = SelectField(u'source', coerce=int, validators=[DataRequired()])


class SubmitArticlesForm(CommonForm):
    title = StringField(u'Title', validators=[DataRequired(), Length(1, 64)])
    content = TextAreaField(u'content', validators=[DataRequired()])
    summary = TextAreaField(u'abstract', validators=[DataRequired()])


class ManageArticlesForm(CommonForm):
    pass


class DeleteArticleForm(FlaskForm):
    articleId = StringField(validators=[DataRequired()])


class DeleteArticlesForm(FlaskForm):
    articleIds = StringField(validators=[DataRequired()])


class DeleteCommentsForm(FlaskForm):
    commentIds = StringField(validators=[DataRequired()])


class AdminCommentForm(CommentForm):
    article = StringField(validators=[DataRequired()])


class AddArticleTypeForm(FlaskForm):
    name = StringField(u'category name', validators=[DataRequired(), Length(1, 64)])
    introduction = TextAreaField(u'category introduction')
    setting_hide = SelectField(u'property', coerce=int, validators=[DataRequired()])
    menus = SelectField(u'navigation tag', coerce=int, validators=[DataRequired()])
# You must add coerce=int, or the SelectFile validate function only validate the int data


class EditArticleTypeForm(AddArticleTypeForm):
    articleType_id = StringField(validators=[DataRequired()])


class AddArticleTypeNavForm(FlaskForm):
    name = StringField(u'Navigation tag name', validators=[DataRequired(), Length(1, 64)])


class EditArticleNavTypeForm(AddArticleTypeNavForm):
    nav_id = StringField(validators=[DataRequired()])


class SortArticleNavTypeForm(AddArticleTypeNavForm):
    order = StringField(u'No.', validators=[DataRequired()])


class CustomBlogInfoForm(FlaskForm):
    title = StringField(u'Title', validators=[DataRequired()])
    signature = TextAreaField(u'Personalized signature', validators=[DataRequired()])
    navbar = SelectField(u'Navigation bar style', coerce=int, validators=[DataRequired()])


class AddBlogPluginForm(FlaskForm):
    title = StringField(u'plugin name', validators=[DataRequired()])
    note = TextAreaField(u'note')
    content = TextAreaField(u'content', validators=[DataRequired()])


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'old password', validators=[DataRequired()])
    password = PasswordField(u'new password', validators=[
        DataRequired(), EqualTo('password2', message=u'two passwords different')])
    password2 = PasswordField(u'confirm new password', validators=[DataRequired()])


class EditUserInfoForm(FlaskForm):
    username = StringField(u'nick name', validators=[DataRequired()])
    email = EmailField(u'email', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField(u'password confirm', validators=[DataRequired()])
