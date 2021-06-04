from flask import Blueprint, request, flash, redirect, url_for, session
from flask.templating import render_template
from flask_login import login_required, current_user
from website.Dashboard import *
from website.models import Dashboard as Dash, Token_url
import datetime
from . import db

views = Blueprint("views", __name__)

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
        elif Dash.query.filter_by(nome = d).first() != None:
            flash('ERROR: Dashboard name already exists, choose a new one', category='error')
        else:
            return redirect(url_for('views.createdashboard', dname=d))

    elif request.method == "GET":
        if request.args.get('deleteBTN', '') != "": 
            dashname = request.args.get('deleteBTN', '')
            #Obter o uid da dashboard da base de dados
            dash = Dash.query.filter_by(nome = dashname).first()
            print("\n"+str(dash.uid)+"\n")
            #Eliminar a dashboard do servidor grafana
            Dashboard.del_dash(uid = dash.uid)
            #Eliminar a dashboard da base de dados do backoffice
            db.session.delete(dash)
            db.session.commit()

    return render_template("dashboards.html")


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
                return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'])
            
            #Criar dashboard
            dbx = Dashboard(None, dname)
            pnl = session.get('pnamelist')
            ptl = session.get('ptypelist')
            ql = session.get('querylist')
            #Adicionar Painéis e querys
            for i in range(0, len(session.get('pnamelist'))):
                dbx.add_query(pnl[i], ptl[i], ql[i])
            #Enviar a dashboard para o servidor
            uid = dbx.send_dash()

            dash = Dash(uid=uid, nome=dname, visibilidade=1, url="http://40.68.96.164:3000/d/"+str(uid)+"/"+str(dname), user_id = current_user.id)
            db.session.add(dash)
            db.session.commit()

            print(session['pnamelist'])
            print(session['ptypelist'])
            print("\n")
            print(json.dumps(dbx.dash))
            print("\n")
            
            #Limpar dados da criação da dashboard
            session['pnamelist'] = []
            session['ptypelist'] = []
            session['querylist'] = []

            return redirect(url_for("views.dashboards"))
        #Cancelar todo o processo de criar uma dashboard
        elif request.args.get('dash', '') == 'Cancel':
            #Limpar dados da criação da dashboard
            session['pnamelist'] = []
            session['ptypelist'] = []
            session['querylist'] = []
            return redirect(url_for("views.dashboards"))
        #Eliminar um dos paineis de uma dashboard
        elif request.args.get('deletePanel', ''):
            i = session.get('pnamelist').index(request.args.get('deletePanel', ''))
            session['pnamelist'] = session.get('pnamelist')
            session['ptypelist'] = session.get('ptypelist')
            session['querylist'] = session.get('querylist')
            session['pnamelist'].pop(i)
            session['ptypelist'].pop(i)
            session['querylist'].pop(i)

            return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'])
   
    return render_template("createdashboards.html", dsh = dname, pname=None, ptype=None)

#My Metrics Page
@views.route("/mymetrics", methods=["GET", "POST"])
@login_required
def mymetrics():
    if request.method == "POST":
        name = request.form.get("metric-name")
        period = request.form.get("dropdown-period")
        endpoint = request.form.get("endpoint")
        api_type = request.form.get("dropdown-api-type")
        # print(name, period, endpoint, api_type)

        # insert flash verifications

        if api_type == "public":
            fields =request.form.get("fields")
            print(fields)

        elif api_type == "key-based-authentication":
            key = request.form.get("key-key")
            fields =request.form.get("fields")
            print(key, fields)

            # adicionar à base de dados

            # enviar dados à api do alex
            
        elif api_type == "bearer-token-based-authentication":
            token_url = request.form.get("token-url")
            token_ckey = request.form.get("token-ckey")
            token_csecret = request.form.get("token-csecret")
            fields =request.form.get("fields")
            print(token_url, token_ckey, token_csecret, fields)

        elif api_type == "http-authentication":
            http_email = request.form.get("http-email")
            http_pass = request.form.get("http-pass")
            fields =request.form.get("fields")
            print(http_email, http_pass, fields)

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


def get_period(str):
    if str == "5-em-5-minutos":
        return 5
    elif str == "30-em-30-minutos":
        return 30
    elif str == "hora-a-hora":
        return 60
    elif str == "diariamente":
        return 24*60
