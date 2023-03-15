from werkzeug.utils import send_from_directory
from forms import CreatePostForm, CommentForm
from datetime import date, datetime
from flask import Flask, redirect, url_for, flash, send_from_directory
from flask_login import current_user, login_required
import os
from db import BlogPost, db, Comment
from functions import img_to_uuid, delete_file
from flask import Blueprint
from flask import render_template

app = Flask(__name__)
UPLOAD_BLOG_IMG = os.getenv('UPLOAD_BLOG_IMG')
app.config['UPLOAD_BLOG_IMG'] = UPLOAD_BLOG_IMG

post_bp = Blueprint('post_bp', __name__)

year = date.today().year

@post_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_BLOG_IMG'], filename)

@post_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
# @login_required
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
            return redirect(url_for('post_bp.show_post', post_id=requested_post.id))
        img_url = None
        if requested_post.img_url:
            img_url = url_for('post_bp.uploaded_file', filename=requested_post.img_url)

        return render_template("post.html", post=requested_post, form=form, current_user=current_user, img_url=img_url,
                               year=year, )
    flash("You're not logged-in. Kindly Log-in")
    return redirect(url_for('get_all_posts'))


@post_bp.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    img_url = None
    if form.validate_on_submit():
        if form.img_url.data:
            img = form.img_url
            img_id = img_to_uuid(img)
            img.data.save(os.path.join(app.config['UPLOAD_BLOG_IMG'], img_id))
            img_url = img_id

        try:
            new_post = BlogPost(
                title=form.title.data,
                subtitle=form.subtitle.data,
                body=form.body.data,
                img_url=img_url,
                author=current_user,
                date=datetime.now().strftime("%B %d, %Y %I:%M %p")
            )
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for("get_all_posts"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(str(e))
            form.errors['submit'] = 'Failed to create new post.'
    return render_template("make-post.html", form=form)


@post_bp.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    file_path = None
    img_id = None
    if post.img_url:
        file_path = os.path.join(UPLOAD_BLOG_IMG, post.img_url)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body,
        post_id=post.id
    )
    if edit_form.validate_on_submit():
        if edit_form.img_url:
            img = edit_form.img_url
            img_id = img_to_uuid(img)
            img.data.save(os.path.join(app.config['UPLOAD_BLOG_IMG'], img_id))
        try:
            post.title = edit_form.title.data
            post.subtitle = edit_form.subtitle.data
            post.img_url = img_id
            post.body = edit_form.body.data
            db.session.commit()
            if file_path and img_id:
                delete_file(file_path)
            return redirect(url_for("post_bp.show_post", post_id=post_id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(str(e))
            edit_form.errors['submit'] = 'Failed to create new post.'

    return render_template("make-post.html", form=edit_form, year=year)


@post_bp.route("/delete_post/<int:post_id>", methods=["GET", "POST"])
@login_required
def delete_post(post_id):
    post_to_delete = BlogPost.query.get_or_404(post_id)
    file_path = None
    if post_to_delete.img_url:
        file_path = os.path.join(UPLOAD_BLOG_IMG, post_to_delete.img_url)
    try:
        Comment.query.filter_by(post_id=post_id).delete()
        db.session.delete(post_to_delete)
        db.session.commit()
        if post_to_delete.img_url:
            delete_file(file_path)
        flash("Blog post was deleted.")
        return redirect(url_for('get_all_posts'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(str(e))
        flash("Whoops!! There was a problem deleting that post.")
        return redirect(url_for('get_all_posts'))


@post_bp.route("/delete_comment/<int:cmt_id>", methods=["GET", "POST"])
@login_required
def delete_cmt(cmt_id):
    cmt_to_delete = Comment.query.get_or_404(cmt_id)
    try:
        Comment.query.filter_by(post_id=cmt_id).delete()
        db.session.delete(cmt_to_delete)
        db.session.commit()
        flash("Comment was deleted.")
        return redirect(url_for('post_bp.show_post', post_id=cmt_to_delete.post_id))
    except Exception as e:
        db.session.rollback()
        app.logger.error(str(e))
        flash("Whoops!! There was a problem deleting that comment.")
        return redirect(url_for('post_bp.show_post', post_id=cmt_to_delete.post_id))
