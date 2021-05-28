from flask import Blueprint, request, flash, redirect, url_for, session
from flask.templating import render_template
from flask_login import login_required, current_user
from website.Dashboard import *

views = Blueprint("views", __name__)


pnamelist = []
ptypelist = []

#MyDashboards Page
@views.route("/dashboards", methods=["GET","POST"])
@login_required
def dashboards():

    if request.method == "POST":
        d = request.form.get("d")
        
        if d == "":
            flash('ERROR: Invalid Dashboard name', category='error')
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
            #Caso não sejam dadas métricas/indicadores -> ERRO
            if query1 == [] and query2 == []:
                flash('ERROR: No metrics were choosen for the graph', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=pnamelist, ptype=ptypelist)
            
            panelname = request.form.get("panelname")
            #Caso o nome do painel seja inválido -> ERRO
            if panelname == "":
                flash('ERROR: Invalid panel name', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=pnamelist, ptype=ptypelist)
            #Caso o nome do painel já tenha sido usado -> ERRO
            elif panelname in pnamelist:
                flash('ERROR: Panel name was already used', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=pnamelist, ptype=ptypelist)
            
            paneltype = request.form.getlist("check")
            #Caso não seja fornecido tipo do painel -> ERRO
            if paneltype == []:
                flash('ERROR: Graph type was not indicated', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=pnamelist, ptype=ptypelist)
            
            print(str(query1) + str(query2))
            print(panelname)
            print(paneltype)

            pnamelist.append(panelname)
            ptypelist.append(paneltype)
            return render_template("createdashboards.html", dsh = dname, pname=pnamelist, ptype=ptypelist)
    
    elif request.method == "GET":
        if request.args.get('dash', '') == 'CreateDash':
            
            #Caso tente criar uma dashboard sem ter especificado suas defenições -> ERRO
            if pnamelist == [] and ptypelist == []:
                flash('ERROR: Dashboard especifications were not indicated', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=pnamelist, ptype=ptypelist)
            
            #Criar dashboard
            db = Dashboard(None, dname)
            #Adicionar Painéis e querys
            db.add_query('Graph1', 'graph', ['SCP<3', 'SCP<3'])

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
