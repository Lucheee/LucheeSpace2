from flask import Blueprint, render_template, redirect, url_for, flash, request
from . import db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))


@auth.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get("username")
        first_name = request.form.get("firstname")
        last_name = request.form.get("lastname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        username_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if username_exists:
            flash('Username already taken, choose another username.', category="error")
        elif email_exists:
            flash('Email Address already taken, choose another username.', category="error")
        elif password1 != password2:
            flash('Password do not match!', category='error')
        elif len(username) < 2:
            flash('Username is too short!', category='error')
        elif len(password1) < 6:
            flash('Password is too short!', category='error')
        elif len(email) < 4:
            flash('Email is invalid', category='error')
        else:
            new_user = User(username=username, first_name=first_name, last_name=last_name, email=email, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created successfully!')
            return redirect(url_for('auth.login'))

    return render_template("signup.html", user=current_user)
