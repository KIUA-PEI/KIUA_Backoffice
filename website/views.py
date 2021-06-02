from flask import Blueprint, request, flash, redirect, url_for, session
from flask.templating import render_template
from flask_login import login_required, current_user
from website.Dashboard import *
from website.DashTmp import *
import datetime

views = Blueprint("views", __name__)

database = []
#d = DashTmp("Dashboard1", datetime.datetime.now(), 'Public', "http://127.0.0.1:5000/dashboards")



#MyDashboards Page
@views.route("/dashboards", methods=["GET","POST"])
@login_required
def dashboards():

    session['pnamelist'] = []
    session['ptypelist'] = []
    session['querylist'] = []

    if request.method == "POST":
        d = request.form.get("d")
        
        if d == "":
            flash('ERROR: Invalid Dashboard name', category='error')
        else:
            return redirect(url_for('views.createdashboard', dname=d))

    return render_template("dashboards.html", db=database)


#Create Dashboard Page
@views.route("/createdashboard/<dname>", methods=["GET", "POST"])
@login_required
def createdashboard(dname):

    #Obter dados necessários para construir os vários painéis da dashboard
    if request.method == "POST":
        if request.form.get('create') == 'CreatePanel':

            query1 = request.form.getlist("m1")
            #Caso não sejam dadas métricas/indicadores -> ERRO
            if query1 == []:
                flash('ERROR: No metrics were choosen for the graph', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'])
            
            panelname = request.form.get("panelname")
            #Caso o nome do painel seja inválido -> ERRO
            if panelname == "":
                flash('ERROR: Invalid panel name', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'])
            #Caso o nome do painel já tenha sido usado -> ERRO
            elif panelname in session.get('pnamelist'):
                flash('ERROR: Panel name was already used', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'])
            
            paneltype = request.form.getlist("check")
            #Caso não seja fornecido tipo do painel -> ERRO
            if paneltype == []:
                flash('ERROR: Graph type was not indicated', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'])
            


            #Adicionar nome dos paineis à lista de paineis adicionados até ao momento
            if 'pnamelist' in session:
                session['pnamelist'] = session.get('pnamelist')
            else:
                session['pnamelist'] = []
            session['pnamelist'].append(panelname)
            #Adicionar tipo de painel à lista de tipos adicionados até ao momento
            if 'ptypelist' in session:
                session['ptypelist'] = session.get('ptypelist')
            else:
                session['ptypelist'] = []
            session['ptypelist'].append(paneltype[0])
            #Adicionar querys à lista de querys adicionados até ao momento
            if 'querylist' in session:
                session['querylist'] = session.get('querylist')
            else:
                session['querylist'] = []
            if query1:
                session['querylist'].append(query1)
            
            print(session['pnamelist'])
            print(session['ptypelist'])
            print(session['querylist'])

            return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'])
    
    elif request.method == "GET":
        if request.args.get('dash', '') == 'CreateDash':
            
            #Caso tente criar uma dashboard sem ter especificado suas defenições -> ERRO
            if session.get('pnamelist') == [] and session.get('ptypelist') == []:
                flash('ERROR: Dashboard especifications were not indicated', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=pnamelist, ptype=ptypelist)
            
            #Criar dashboard
            db = Dashboard(None, dname)
            pnl = session.get('pnamelist')
            ptl = session.get('ptypelist')
            ql = session.get('querylist')
            #Adicionar Painéis e querys
            for i in range(0, len(session.get('pnamelist'))):
                db.add_query(pnl[i], ptl[i], ql[i])
            #Enviar a dashboard para o servidor
            uid = db.send_dash()

            database.append(DashTmp(dname, datetime.datetime.now(), 'Public', "http://40.68.96.164:3000/d/"+str(uid)+"/"+str(dname)))


            print(session['pnamelist'])
            print(session['ptypelist'])
            print("\n")
            print(json.dumps(db.dash))
            print("\n")
            
            #Limpar dados da criação da dashboard
            session['pnamelist'] = []
            session['ptypelist'] = []
            session['querylist'] = []

            return render_template("dashboards.html", db=database)
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
