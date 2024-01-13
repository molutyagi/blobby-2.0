from flask import Blueprint
from flask import render_template
from datetime import date

others_bp = Blueprint('others', __name__)

year = date.today().year


@others_bp.route("/about")
def about():
    return render_template("about.html", year=year)


@others_bp.route("/contact")
def contact():
    return render_template("contact.html", year=year)
