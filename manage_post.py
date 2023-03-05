from functions import delete_file, img_to_uuid
from only import admin_only
from werkzeug.utils import secure_filename, send_from_directory
from forms import CreatePostForm, CommentForm
from flask import Flask, redirect, url_for, flash
from flask_login import current_user
import os
from db import BlogPost, db, Comment
from flask import Blueprint
from flask import render_template
from datetime import date

app = Flask(__name__)
UPLOAD_BLOG_IMG = "dynamic/uploads/blog_img"
app.config['UPLOAD_BLOG_IMG'] = UPLOAD_BLOG_IMG

post_bp = Blueprint('post_bp', __name__)

year = date.today().year



@post_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_BLOG_IMG'], filename)


@post_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    if current_user.is_authenticated:
        requested_post = BlogPost.query.get_or_404(post_id)
        form = CommentForm()
        if form.validate_on_submit():
            if not current_user.id:
                return redirect(url_for('get_all_posts'))
            new_comment = Comment(
                text=form.body.data,
                post_id=post_id,
                author_id=current_user.id
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('get_all_posts'))

        img_url = url_for('post_bp.uploaded_file', filename=requested_post.img_url)

        return render_template("post.html", post=requested_post, form=form, current_user=current_user, img_url=img_url,
                               year=year)
    flash("You're not logged-in. Kindly Log-in")
    return redirect(url_for('get_all_posts'))



@post_bp.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        img = form.img_url
        img_id = img_to_uuid(img)
        img.data.save(os.path.join(app.config['UPLOAD_BLOG_IMG'], img_id))
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=img_id,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, year=year)


@post_bp.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    file_path = os.path.join(UPLOAD_BLOG_IMG, post.img_url)
    if edit_form.validate_on_submit():
        img = edit_form.img_url
        img_id = img_to_uuid(img)
        img.data.save(os.path.join(app.config['UPLOAD_BLOG_IMG'], img_id))

        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = img_id
        post.body = edit_form.body.data
        db.session.commit()

        delete_file(file_path)
        return redirect(url_for("post_bp.show_post", post_id=post.id))

    return render_template("post_bp.make-post.html", form=edit_form, year=year)


@post_bp.route("/delete/<int:post_id>", methods=["GET", "POST"])
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get_or_404(post_id)
    file_path = os.path.join(UPLOAD_BLOG_IMG, post_to_delete.img_url)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        delete_file(file_path)
        flash("Blog post was deleted.")
        return redirect(url_for('get_all_posts'))
    except:
        flash("Whoops!! There was a problem deleting that post.")
        return redirect(url_for('get_all_posts'))
