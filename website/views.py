from flask import Blueprint, request, flash, redirect, url_for
from flask.templating import render_template
from flask_login import login_required, current_user
from website.Dashboard import *

views = Blueprint("views", __name__)

#Global lists to save panel types and names
pnamelist = []
ptypelist = []

#MyDashboards Page
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


#Create Dashboard Page
@views.route("/createdashboard/<dname>", methods=["GET", "POST"])
@login_required
def createdashboard(dname):

    #Obter dados necessários para construir os vários painéis da dashboard
    if request.method == "POST":
        if request.form.get('create') == 'CreatePanel':
            query1 = request.form.getlist("m1")
            query2 = request.form.getlist("m2")
            panelname = request.form.get("panelname")
            paneltype = request.form.getlist("check")
            print(str(query1) + str(query2))
            print(panelname)
            print(paneltype)

            pnamelist.append(panelname)
            ptypelist.append(paneltype)
            return render_template("createdashboards.html", dsh = dname, pname=pnamelist, ptype=ptypelist)
    elif request.method == "GET":
        if request.args.get('dash', '') == 'CreateDash':
            db = Dashboard(None, dname)
            print("\n")
            print(db.dash)
            print("\n")
            pnamelist.clear()
            ptypelist.clear()
            return render_template("dashboards.html")
    return render_template("createdashboards.html", dsh = dname, pname=None, ptype=None)

#My Metrics Page
@views.route("/mymetrics")
@login_required
def mymetrics():
    return render_template("mymetrics.html")

#Default Metrics Page
@views.route("/metrics")
@login_required
def metrics():
    return render_template("metrics.html")

#Help Page
@views.route("/help")
@login_required
def help():
    return render_template("help.html")
