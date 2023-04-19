from flask import Flask
from flask_session import Session
from werkzeug.utils import secure_filename
import uuid as uuid
import os
import re


def check_password(password):
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    return bool(re.match(pattern, password))


def get_session():
    app = Flask(__name__)

    with app.app_context():
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

        app.config["SESSION_PERMANENT"] = False
        app.config["SESSION_TYPE"] = "cookie"
        app.config["SESSION_COOKIE_SECURE"] = True
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
        Session(app)


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def img_to_uuid(img):
    fn = secure_filename(img.data.filename)
    img_id = str(uuid.uuid1()) + "_" + fn
    return img_id
