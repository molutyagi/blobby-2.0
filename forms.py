from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, HiddenField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, ValidationError, URL
from flask_ckeditor import CKEditorField

from db import BlogPost


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_file = FileField("Blog Image File")
    img_url = StringField("Blog Image URL")
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    post_id = HiddenField()
    submit = SubmitField("Submit Post")

    def validate_title(self, field):
        post = BlogPost.query.filter_by(title=field.data).first()
        if post and str(post.id) != self.post_id.data:
            raise ValidationError('Title already exists. Please choose a different one.')


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(' Confirm Password', validators=[DataRequired()])
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