from flask import Flask
from flask_session import Session
from werkzeug.utils import secure_filename
import uuid as uuid
import redis
import os


def get_session():
    app = Flask(__name__)

    with app.app_context():
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
        Session(app)


def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def img_to_uuid(img):
    fn = secure_filename(img.data.filename)
    img_id = str(uuid.uuid1()) + "_" + fn
    return img_id
