import os
import secrets
from datetime import date
from functools import wraps

from flask import Flask, render_template, redirect, url_for, flash, abort, send_from_directory, current_app
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import LoginManager, current_user, login_required

from db import User, BlogPost, db, Comment
from flask_session import Session
from forms import CommentForm, CreatePostForm
from functions import delete_file, img_to_uuid
from log_reg import log_bp
from manage_user import user_bp
from others import others_bp
from modify_db import modify_db

# from handle_error import handle_error_bp
# from manage_post import post_bp

app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = secrets.token_hex(16)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

UPLOAD_USER_IMG = "dynamic/profile_pic"
app.config['UPLOAD_USER_IMG'] = UPLOAD_USER_IMG
UPLOAD_BLOG_IMG = "dynamic/blog_img"
app.config['UPLOAD_BLOG_IMG'] = UPLOAD_BLOG_IMG
app.config['STATIC_FOLDER'] = 'static'
# db = SQLAlchemy(app)
db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)

# load_dotenv()
# auth_users = (os.getenv('AUTH_USERS'))
auth_users = [1, 2]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get_or_404(user_id)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id not in auth_users:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


app.register_blueprint(log_bp)
app.register_blueprint(others_bp)
app.register_blueprint(user_bp)
# app.register_blueprint(handle_error_bp)
# app.register_blueprint(post_bp)


gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)
year = date.today().year


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    # modify_db()
    return render_template("index.html", all_posts=posts, logged_in=current_user.is_authenticated, year=year,
                           auth_users=auth_users)


# @app.route('/search', methods=["POST"])
# def search():
#     form = SearchForm()
#     posts = BlogPost.query
#     if form.validate_on_submit():
#         searched = form.searched.data
#         posts = posts.filter(BlogPost.content.like('%' + searched + '%'))
#         posts = posts.order_by(BlogPost.title).all()
#
#         return render_template("search.html",
#                                form=form,
#                                searched=searched,
#                                posts=posts)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_BLOG_IMG'], filename)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
# @login_required
def show_post(post_id):
    if current_user.is_authenticated:
        requested_post = BlogPost.query.get_or_404(post_id)
        # all_comments = Comment.query.filter_by(post_id=requested_post.id).all()
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
            return redirect(url_for('show_post', post_id=post_id))
        img_url = None
        if requested_post.img_url:
            img_url = url_for('uploaded_file', filename=requested_post.img_url)

        return render_template("post.html", post=requested_post, form=form, current_user=current_user, img_url=img_url,
                               year=year, )
    flash("You're not logged-in. Kindly Log-in")
    return redirect(url_for('get_all_posts'))


@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        print("valid")
        if form.img_url.data:
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
            print("form")
        else:
            print("else")
            new_post = BlogPost(
                title=form.title.data,
                subtitle=form.subtitle.data,
                body=form.body.data,
                img_url=None,
                author=current_user,
                date=date.today().strftime("%B %d, %Y")
            )
            db.session.add(new_post)
            db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, year=year)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    file_path = os.path.join(UPLOAD_BLOG_IMG, post.img_url) if post.img_url else None

    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():

        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.body = edit_form.body.data

        if edit_form.img_url:
            img = edit_form.img_url
            img_id = img_to_uuid(img)
            img.data.save(os.path.join(app.config['UPLOAD_BLOG_IMG'], img_id))
            post.img_url = img_id

            if file_path:
                delete_file(file_path)

        db.session.commit()

        return redirect(url_for("show_post", post_id=post_id))

    return render_template("make-post.html", form=edit_form, year=year)


@app.route("/delete_post/<int:post_id>", methods=["GET", "POST"])
@login_required
def delete_post(post_id):
    post_to_delete = BlogPost.query.get_or_404(post_id)
    file_path = os.path.join(UPLOAD_BLOG_IMG, post_to_delete.img_url)
    try:
        Comment.query.filter_by(post_id=post_id).delete()
        db.session.delete(post_to_delete)
        db.session.commit()
        delete_file(file_path)
        flash("Blog post was deleted.")
        return redirect(url_for('get_all_posts'))
    except:
        flash("Whoops!! There was a problem deleting that post.")
        return redirect(url_for('get_all_posts'))


@app.route("/delete_comment/<int:cmt_id>", methods=["GET", "POST"])
@login_required
def delete_cmt(cmt_id):
    cmt_to_delete = Comment.query.get_or_404(cmt_id)
    try:
        Comment.query.filter_by(post_id=cmt_id).delete()
        db.session.delete(cmt_to_delete)
        db.session.commit()
        flash("Comment was deleted.")
        return redirect(url_for('show_post', post_id=cmt_to_delete.post_id))
    except:
        flash("Whoops!! There was a problem deleting that comment.")
        return redirect(url_for('show_post', post_id=cmt_to_delete.post_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500 @ app.errorhandler(404)


@app.errorhandler(401)
def page_not_found(e):
    return render_template("401.html"), 401


@app.errorhandler(403)
def page_not_found(e):
    return render_template("403.html"), 403


if __name__ == "__main__":
    app.run(debug=True)
# serve(app, host='0.0.0.0', port=80, threads=1)
