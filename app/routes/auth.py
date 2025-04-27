from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from app.forms import SignupForm, LoginForm
from app.models import User

auth = Blueprint("auth", __name__)

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User.create_user(form.username.data, form.password.data)
        if user:
            login_user(user)
            flash("Signed up successfully!", "success")
            return redirect(url_for("main.chat_home"))
        else:
            flash("Username already exists.", "danger")
    return render_template("signup.html", form=form)

@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("main.home"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html", form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("auth.login"))
