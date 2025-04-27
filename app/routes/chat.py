# app/routes/chat.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return render_template("home.html")

@main.route('/chat')
@login_required
def chat_home():
    return redirect(url_for("main.chat", room="general"))  # or your default room

@main.route("/chat/<room>")
@login_required
def chat(room):
    return render_template("chat.html", room=room, username=current_user.username)
