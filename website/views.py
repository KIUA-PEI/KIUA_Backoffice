from flask import Blueprint
from flask.templating import render_template
from flask_login import login_required, current_user
from flask import request, flash

views = Blueprint("views", __name__)


@views.route("/dashboards", methods=["GET", "POST"])
@login_required
def dashboards():
    if request.method == "POST":
        d = request.form.get("d")

        print("Dash"+d)
        if d == "":
            flash('Invalid Dashboard name', category='error')
            print("Here")
        else:
            return render_template("createdashboards.html", dash = d)
    return render_template("dashboards.html")

@views.route("/createdashboard")
@login_required
def createdashboards():
    return render_template("createdashboards.html")

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
