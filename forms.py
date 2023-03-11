from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    # img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    img_url = FileField("Blog Image")
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Login")


class CommentForm(FlaskForm):
    body = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Post Comment")


class UserDetails(FlaskForm):
    name = StringField('Name')
    profile = FileField("Profile Pic")
    wall = FileField("Wall Image")
    about = CKEditorField("About Yourself")
    submit = SubmitField("Update Details")


class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")
