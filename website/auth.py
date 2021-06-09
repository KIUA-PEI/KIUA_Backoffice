
from website.models import User
from flask import Blueprint
from flask.templating import render_template
from flask import request, flash, redirect, url_for
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from website.Dashboard import * 

auth = Blueprint("auth", __name__)

@auth.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        print(remember)

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=remember)
                return redirect(url_for("views.dashboards"))
            else: 
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("index.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        password = request.form.get("password")
        repeatpassword = request.form.get("repeatpassword")

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists.", category="error")

        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(fname) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password != repeatpassword:
            flash('Passwords don\'t match.', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, password=generate_password_hash(password, method="sha256") , fname=fname, lname=lname)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=False)
            flash('Account created with success!', category='success')
            new_user.folder_id = Dashboard.create_folder(str(new_user.id))
            print(new_user.folder_id)
            db.session.commit()
            print(new_user.folder_id)
            return redirect(url_for("views.dashboards"))

    return render_template("register.html")


