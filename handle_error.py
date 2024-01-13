import traceback

from flask import Blueprint, render_template

error_bp = Blueprint('error_bp', __name__, template_folder='templates')


@error_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@error_bp.app_errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


@error_bp.app_errorhandler(401)
def page_not_found(e):
    return render_template("401.html"), 401


@error_bp.app_errorhandler(403)
def page_not_found(e):
    return render_template("403.html"), 403

# @error_bp.app_errorhandler(Exception)
# def general_exception(e):
#     print(e)
#     print(traceback.format_exc())
#     return render_template('error.html')
