import os
from functools import wraps
from flask import Flask, render_template, abort, session
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from flask_login import LoginManager, current_user
from flask_gravatar import Gravatar
from flask_session import Session
from db import User, BlogPost, db
from log_reg import log_bp
from others import others_bp
from manage_user import user_bp
from handle_error import error_bp
from manage_post import post_bp
year = date.today().year
app = Flask(__name__)
app.app_context().push()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['STATIC_FOLDER'] = 'static'

db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)

auth_users = None


@app.context_processor
def inject_vars():
    auth_users = (os.getenv('AUTH_USERS'))
    auth_users = auth_users.split(',')
    auth_users = list(map(int, auth_users))
    return dict(auth_users=auth_users)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get_or_404(int(user_id))


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id not in auth_users:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route("/get_session_data")
def get_session_data():
    return f"Session data: {session.get('username', 'Not set')}"


@app.route('/')
def get_all_posts():
    if current_user.is_authenticated:
        session["username"] = current_user.name
    posts = BlogPost.query.order_by(BlogPost.id.desc()).all()
    return render_template("index.html", all_posts=posts, logged_in=current_user.is_authenticated, year=year)


app.register_blueprint(error_bp)
app.register_blueprint(log_bp)
app.register_blueprint(others_bp)
app.register_blueprint(user_bp)
app.register_blueprint(post_bp)

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


def application(env, start_response):
    return app(env, start_response)

