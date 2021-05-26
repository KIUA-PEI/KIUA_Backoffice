from flask import Blueprint
from flask.templating import render_template
from flask_login import login_required, current_user

views = Blueprint("views", __name__)


@views.route("/dashboards")
@login_required
def dashboards():
    return render_template("dashboards.html")

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
