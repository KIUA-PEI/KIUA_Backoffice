from flask import Blueprint
from flask.templating import render_template
from flask_login import login_required, current_user
from flask import request, flash, redirect, url_for
from website.Dashboard import *

views = Blueprint("views", __name__)


@views.route("/dashboards", methods=["GET","POST"])
@login_required
def dashboards():
    if request.method == "POST":
        d = request.form.get("d")
        
        if d == "":
            flash('Invalid Dashboard name', category='error')
            print("Here")
        else:
            return redirect(url_for('views.createdashboard', dname=d))

    return render_template("dashboards.html")

@views.route("/createdashboard/<dname>", methods=["GET", "POST"])
@login_required
def createdashboard(dname):
    #Criar a dashboard
    db = Dashboard(None, dname)
    print("\n")
    print(db.dash)
    print("\n")
    return render_template("createdashboards.html", dsh = dname)

@views.route("/mymetrics")
@login_required
def mymetrics():
    return render_template("mymetrics.html")

@views.route("/metrics")
@login_required
def metrics():
    return render_template("metrics.html")

@views.route("/help")
@login_required
def help():
    return render_template("help.html")
