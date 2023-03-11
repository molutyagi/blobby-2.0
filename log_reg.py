from flask import Blueprint
from flask import render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required
from forms import RegisterForm, LoginForm
from db import User, db
from datetime import date

log_bp = Blueprint('log_reg', __name__)

year = date.today().year


@log_bp.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, login instead!")
            return redirect(url_for('login'))
        if form.password.data != form.confirm_password.data:
            flash("Password does not match. Try again.")
            return redirect(url_for('log_reg.register'))
        hashed = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hashed
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form, logged_in=current_user.is_authenticated, year=year)


@log_bp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("That email doesn't exist. Kindly Register.")
            return redirect(url_for('log_reg.login'))
        elif check_password_hash(user.password, password):
            login_user(user)
            flash("Successfully logged in.")
            return redirect(url_for('get_all_posts'))
        else:
            flash("Wrong Password. Please try again.")
            return redirect(url_for('log_reg.login'))
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated, year=year)


@log_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!  Thanks For Stopping By...")
    return redirect(url_for('get_all_posts'))
