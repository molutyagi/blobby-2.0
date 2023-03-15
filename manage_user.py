from flask import Flask, redirect, url_for, flash, send_from_directory, current_app
from flask_login import current_user, login_required

from forms import UserDetails
import os
from db import User, BlogPost, db, Comment
from functions import img_to_uuid, delete_file
from flask import Blueprint
from flask import render_template
from datetime import date
from log_reg import logout_user

app = Flask(__name__)
UPLOAD_USER_IMG = os.getenv('UPLOAD_USER_IMG')
app.config['UPLOAD_USER_IMG'] = UPLOAD_USER_IMG

user_bp = Blueprint('user_bp', __name__)

year = date.today().year


@user_bp.route("/profile/<int:user_id>", methods=["GET", "POST"])
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = BlogPost.query.filter_by(author_id=user_id).all()
    return render_template("profile.html", year=year, current_user=current_user, all_posts=posts, user=user)


@user_bp.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)

    profile_path = os.path.join(app.config['UPLOAD_USER_IMG'], user.profile) if user.profile else None
    wall_path = os.path.join(app.config['UPLOAD_USER_IMG'], user.wall) if user.wall else None

    form = UserDetails(name=user.name, about=user.about)

    if form.validate_on_submit():
        user.about = form.about.data
        user.name = form.name.data

        if form.profile.data or form.wall.data:
            if form.profile.data:
                p_pic = form.profile
                p_pic_id = img_to_uuid(p_pic)
                user.profile = p_pic_id
                p_pic.data.save(os.path.join(app.config['UPLOAD_USER_IMG'], p_pic_id))
                if profile_path:
                    delete_file(profile_path)

            if form.wall.data:
                wall = form.wall
                wall_id = img_to_uuid(wall)
                user.wall = wall_id
                wall.data.save(os.path.join(app.config['UPLOAD_USER_IMG'], wall_id))
                if wall_path:
                    delete_file(wall_path)

        db.session.commit()
        flash("User Updated Successfully!")
        return redirect(url_for("user_bp.profile", user_id=user.id))

    return render_template("edit-user.html", year=year, user=user, current_user=current_user, form=form)


@user_bp.route('/profile_img/<filename>')
def profile_img(filename):
    return send_from_directory(app.config['UPLOAD_USER_IMG'], filename)


@user_bp.route('/wall_img/<filename>')
def wall_img(filename):
    return send_from_directory(app.config['UPLOAD_USER_IMG'], filename)


@user_bp.route("/delete_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    try:
        if user_to_delete.profile:
            profile_path = os.path.join(UPLOAD_USER_IMG, user_to_delete.profile)
            delete_file(profile_path)

        if user_to_delete.wall:
            wall_path = os.path.join(UPLOAD_USER_IMG, user_to_delete.wall)
            delete_file(wall_path)

        for post in user_to_delete.posts:
            delete_post = current_app.view_functions['post_bp.delete_post']
            with current_app.test_request_context():
                delete_post(post_id=post.id)

        Comment.query.filter_by(author_id=user_id).delete()

        logout_user()
        db.session.delete(user_to_delete)
        db.session.commit()

        flash("User was deleted.")
        return redirect(url_for('get_all_posts'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(str(e))
        flash("Whoops!! There was a problem deleting user.")
        return redirect(url_for('get_all_posts'))
