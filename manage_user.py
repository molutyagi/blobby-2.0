from flask import Flask, redirect, url_for, flash, send_from_directory
from flask_login import current_user
from forms import UserDetails
import os
from db import User, BlogPost, db
from functions import img_to_uuid, delete_file
from flask import Blueprint
from flask import render_template
from datetime import date

app = Flask(__name__)
UPLOAD_USER_IMG = "dynamic/uploads/profile_pic"
app.config['UPLOAD_USER_IMG'] = UPLOAD_USER_IMG

user_bp = Blueprint('user_bp', __name__)

year = date.today().year


@user_bp.route("/profile/<int:user_id>", methods=["GET", "POST"])
def profile(user_id):
    user = User.query.get_or_404(user_id)
    # profile_img_url = url_for('user_bp.profile_img', filename=current_user.profile)
    # wall_img_url = url_for('user_bp.wall_img', filename=current_user.wall)
    posts = BlogPost.query.filter_by(author_id=user_id).all()
    return render_template("profile.html", year=year, current_user=current_user, all_posts=posts, user=user)


@user_bp.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if current_user.is_authenticated:
        user = User.query.get_or_404(user_id)
        if user.profile:
            profile_path = os.path.join(UPLOAD_USER_IMG, user.profile)
        if user.wall:
            wall_path = os.path.join(UPLOAD_USER_IMG, user.wall)
        form = UserDetails(
            name=current_user.name,
            about=current_user.about
        )
        if form.validate_on_submit():
            user.about = form.about.data
            user.name = form.name.data
            if form.profile.data or form.wall.data:
                if form.profile.data:
                    p_pic = form.profile
                    p_pic_id = img_to_uuid(p_pic)
                    user.profile = p_pic_id

                if form.wall.data:
                    wall = form.wall
                    wall_id = img_to_uuid(wall)
                    user.wall = wall_id

                try:
                    db.session.commit()
                    if form.profile.data:
                        p_pic.data.save(os.path.join(app.config['UPLOAD_USER_IMG'], p_pic_id))
                        delete_file(profile_path)

                    if form.wall.data:
                        wall.data.save(os.path.join(app.config['UPLOAD_USER_IMG'], wall_id))
                        delete_file(wall_path)
                    return redirect(url_for("user_bp.profile", user_id=user.id))

                except:
                    flash("Error!  Looks like there was a problem...try again!")
                    return redirect(url_for('user_bp.edit_user'))
            else:
                db.session.commit()
                flash("User Updated Successfully!")
            return redirect(url_for("user_bp.profile", user_id=user.id))

        return render_template("edit-user.html", year=year, current_user=current_user, form=form)


@user_bp.route('/profile_img/<filename>')
def profile_img(filename):
    return send_from_directory(app.config['UPLOAD_USER_IMG'], filename)


@user_bp.route('/wall_img/<filename>')
def wall_img(filename):
    return send_from_directory(app.config['UPLOAD_USER_IMG'], filename)
