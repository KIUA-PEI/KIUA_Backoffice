from flask import Blueprint, request, flash, redirect, url_for, session
from flask.templating import render_template
from flask_login import login_required, current_user
from website.Dashboard import *
<<<<<<< HEAD
from website.DashTmp import *
from website.models import Dashboard as Dash, Basic_url, Key_url, Http_url, Token_url
=======
from website.models import Dashboard as Dash, Token_url
from website.models import User
>>>>>>> f3714ad0eab40a468c7b3ac563f3bb74e75b00a7
import datetime
from . import db

views = Blueprint("views", __name__)

#d = DashTmp("Dashboard1", datetime.datetime.now(), 'Public', "http://127.0.0.1:5000/dashboards")



#MyDashboards Page
@views.route("/dashboards", methods=["GET","POST"])
@login_required
def dashboards():
    other_users = (User.query.filter(User.id!=current_user.id).all())

    session['pnamelist'] = []
    session['ptypelist'] = []
    session['querylist'] = []

    if request.method == "POST":
        d = request.form.get("d")
        if d == "":
            flash('ERROR: Invalid Dashboard name', category='error')
        elif Dash.query.filter_by(user_id = current_user.id, nome = d).first() != None:
            flash('ERROR: Dashboard name already exists, choose a new one', category='error')
        else:
            return redirect(url_for('views.createdashboard', dname=d))

    elif request.method == "GET":
        #Apagar um dashboard
        if request.args.get('deleteBTN', '') != "": 
            #Obter o uid da dashboard da base de dados
            dash = Dash.query.filter_by(user_id = current_user.id, nome = request.args.get('deleteBTN', '')).first()
            print("\n"+str(dash.uid)+"\n")
            #Eliminar a dashboard do servidor grafana
            Dashboard.del_dash(uid = dash.uid)
            #Eliminar a dashboard da base de dados do backoffice
            db.session.delete(dash)
            db.session.commit()

        #Mudar para pública a visibilidade de uma dashboard
        elif request.args.get('public', '') != "":
            dash = Dash.query.filter_by(user_id = current_user.id, nome = request.args.get('public', '')).first()
            dash.visibilidade = 1
            db.session.commit()

        #Mudar para privada a visibilidade de uma dashboard
        elif request.args.get('private', '') != "":
            dash = Dash.query.filter_by(user_id = current_user.id, nome = request.args.get('private', '')).first()
            dash.visibilidade = 0
            db.session.commit()


    return render_template("dashboards.html", other_users=other_users)


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
            print(current_user.folder_id)
            uid = dbx.send_dash(current_user.folder_id)

            dash = Dash(uid=uid, nome=dname, visibilidade=0, url="http://40.68.96.164:3000/d/"+str(uid)+"/"+str(dname), user_id = current_user.id, panels =  len(session.get('pnamelist')))
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
        fields =request.form.get("fields")

        # insert flash verifications

        if api_type == "public":
            basic = Basic_url(url=endpoint, name=name, args=fields, period=get_period(period), user_id=current_user.id)
            db.session.add(basic)
            db.session.commit()


        elif api_type == "key-based-authentication":
            key = request.form.get("key-key")
            
            keyapi = Key_url(url=endpoint, name=name, args=fields, period=get_period(period), key=key, user_id=current_user.id)
            db.session.add(keyapi)
            db.session.commit()
            
        elif api_type == "bearer-token-based-authentication":
            token_url = request.form.get("token-url")
            token_ckey = request.form.get("token-ckey")
            token_csecret = request.form.get("token-csecret")
            
            tokenapi = Token_url(url=endpoint, name=name, args=fields, token_url=token_url, period=get_period(period), key=token_ckey, secret=token_csecret, user_id=current_user.id)
            db.session.add(tokenapi)
            db.session.commit()

        elif api_type == "http-authentication":
            user = request.form.get("http-email")
            passx = request.form.get("http-pass")

            httpapi = Http_url(url=endpoint, name=name, args=fields, period=get_period(period), username=user, key=passx, user_id=current_user.id)
            db.session.add(httpapi)
            db.session.commit()

    return render_template("mymetrics.html")

#Show a dashboard page
@views.route("/showdashboard/<userid>/<dname>", methods=["GET", "POST"])
@login_required
def showdashboard(userid, dname):
    
    theme = "Light"
    if request.method == "GET":
        theme = request.args.get('theme', '')
    
    #Obter a dashboard da base de dados
    dash = Dash.query.filter_by(user_id = userid, nome = dname).first()
    urls = []
    #Obter todos os painéis
    for i in range(1, dash.panels+1):
        if theme == "Light":
            urls.append("http://40.68.96.164:3000/d-solo/"+dash.uid+"/"+dash.nome+"?panelId="+str(i)+"&theme=light")
        else:
            urls.append("http://40.68.96.164:3000/d-solo/"+dash.uid+"/"+dash.nome+"?panelId="+str(i)+"&theme=dark")
    if theme == "Light":
        return render_template("showdashboards.html",dname=dname, urls=urls, theme="Dark")
    else:
        return render_template("showdashboards.html",dname=dname, urls=urls, theme="Light")



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
        return "5 minutos"
    elif str == "30-em-30-minutos":
        return "30 minutos"
    elif str == "hora-a-hora":
        return "1 hora"
    elif str == "diariamente":
        return "1 dia"
