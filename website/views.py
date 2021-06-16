from flask import Blueprint, request, flash, redirect, url_for, session
from flask.templating import render_template
from flask_login import login_required, current_user
from website.Dashboard import *
from website.models import Dashboard as Dash, Basic, Key, Http, Metrics, Token, MyMetricas, Metrics, Kpi
from website.models import User
from . import db
from influxdb import InfluxDBClient
from website.influxqueries import *

views = Blueprint("views", __name__)

#MyDashboards Page
@views.route("/dashboards", methods=["GET","POST"])
@login_required
def dashboards():
    #Se métricas default não estão no site ainda carregá-las
    if Metrics.query.filter(Metrics.id == 1).first() == None:
        load_metrics()
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
    defaultmetrics = Metrics.query.all()
    for m in defaultmetrics:
        print(m.kpis)
    

    #Obter dados necessários para construir os vários painéis da dashboard
    if request.method == "POST":
        if request.form.get('create') == 'CreatePanel':
            query1 = request.form.getlist("m1")
            #Caso não sejam dadas métricas/indicadores -> ERRO
            if query1 == []:
                flash('ERROR: No metrics were choosen for the graph', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'], defaultmetrics=defaultmetrics)
            
            panelname = request.form.get("panelname")
            #Caso o nome do painel seja inválido -> ERRO
            if panelname == "":
                flash('ERROR: Invalid panel name', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'], defaultmetrics=defaultmetrics)
            #Caso o nome do painel já tenha sido usado -> ERRO
            elif panelname in session.get('pnamelist'):
                flash('ERROR: Panel name was already used', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'], defaultmetrics=defaultmetrics)
            
            paneltype = request.form.getlist("check")
            #Caso não seja fornecido tipo do painel -> ERRO
            if paneltype == []:
                flash('ERROR: Graph type was not indicated', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'], defaultmetrics=defaultmetrics)
            


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

            return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'], defaultmetrics=defaultmetrics)
    
    elif request.method == "GET":
        if request.args.get('dash', '') == 'CreateDash':
            #Caso tente criar uma dashboard sem ter especificado suas defenições -> ERRO
            if session.get('pnamelist') == [] and session.get('ptypelist') == []:
                flash('ERROR: Dashboard especifications were not indicated', category='error')
                return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'], defaultmetrics=defaultmetrics)
            
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

            dash = Dash(uid=uid, nome=dname, visibilidade=0, url="http://40.68.96.164:3000/d/"+str(uid)+"/"+str(dname), user_id = current_user.id, panels= len(session.get('pnamelist')))
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

            flash('SUCESS: Dashboard created sucessfully', category='success')

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

            return render_template("createdashboards.html", dsh = dname, pname=session['pnamelist'], ptype=session['ptypelist'], defaultmetrics=defaultmetrics)

    return render_template("createdashboards.html", dsh = dname, pname=None, ptype=None, defaultmetrics=defaultmetrics)




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

        #Nome inválido
        if name == "":
            flash('ERROR: Invalid Metric name', category='error')
            return render_template("mymetrics.html")
        #Caso já exista uma métrica com um nome igual
        elif MyMetricas.query.filter_by(user_id = current_user.id, name = name).first() != None:
            flash('ERROR: Metric name already exists, choose a new one', category='error')
            return render_template("mymetrics.html")
        #Caso não seja especificado endpoint
        elif endpoint == "":
            flash('ERROR: Source endpoint not specified', category='error')
            return render_template("mymetrics.html")


        #Basic
        if api_type == "public":
            basic = Basic(url=endpoint, name=name, args=fields, period=period, periodstr=get_period(period), user_id=current_user.id)
            db.session.add(basic)
            db.session.commit()
            
            print("pronto a enviar...")
            print("id " + str(basic.id))
            print("basic.url " + basic.url)
            print("basic.period " + str(get_int(basic.period)))
            print("args "+ basic.args)

            #Enviar pedido para a API
            r = requests.get(daemons_api+'/Daemon/Add/Basic',
                {"id":basic.id,
                "url": basic.url,
                "period":get_int(basic.period),
                "args": basic.args,},
                headers={'Authorization': daemons_api_key})
            print("response status: "+str(r.status_code))
            
            #Caso a response da API dê erro 
            if r.status_code != 200 and r.status_code != 201:
                flash('ERROR: Creating metric, Response Code:'+str(r.status_code)+" Response: "+str(r.text), category='error')
                db.session.delete(basic)
                db.session.commit()
                return render_template("mymetrics.html")
            
            #Gerar querys automaticamente
            querys = get_querys(str(basic.id))
            print(querys)

            flash('SUCESS: Metric added sucessfully', category='success')
            print("response text: "+str(r.text))

        # Key
        elif api_type == "key-based-authentication":
            key = request.form.get("key-key")
            
            keyapi = Key(url=endpoint, name=name, args=fields, period=period, periodstr=get_period(period), key=key, user_id=current_user.id)
            db.session.add(keyapi)
            db.session.commit()

            r = requests.get(daemons_api+'/Daemon/Add/Key',
                {"id":keyapi.id,
                "url": keyapi.url,
                "key": keyapi.key,
                "args": keyapi.args,
                "period":get_int(keyapi.period)},
                headers={'Authorization': daemons_api_key})
            # print(r.status_code)

        # Token
        elif api_type == "bearer-token-based-authentication":
            token_url = request.form.get("token-url")
            token_ckey = request.form.get("token-ckey")
            token_csecret = request.form.get("token-csecret")
            
            tokenapi = Token(url=endpoint, name=name, args=fields, token_url=token_url, period=period, periodstr=get_period(period), key=token_ckey, secret=token_csecret, user_id=current_user.id)
            db.session.add(tokenapi)
            db.session.commit()

            r = requests.get(daemons_api+'/Daemon/Add/Token',
                {"id":tokenapi.id,
                "url": tokenapi.url,
                "token_url": tokenapi.token_url,
                "secret": tokenapi.secret,
                "key": tokenapi.key,
                "period":get_int(tokenapi.period),
                "args": tokenapi.args},
                headers={'Authorization':daemons_api_key})
            # print(r.status_code)

        # Http  
        elif api_type == "http-authentication":
            user = request.form.get("http-email")
            passx = request.form.get("http-pass")

            httpapi = Http(url=endpoint, name=name, args=fields, period=period, periodstr=get_period(period), username=user, key=passx, user_id=current_user.id)
            db.session.add(httpapi)
            db.session.commit()

            r = requests.get(daemons_api+'/Daemon/Add/Http',
                {"id":httpapi.id,
                "url": httpapi.url,
                "username": httpapi.username,
                "key": httpapi.key,
                "period": get_int(httpapi.period),
                "args": httpapi.args},
                headers={'Authorization':daemons_api_key})
    
    
    elif request.method == "GET":
        #Apagar uma métrica
        if request.args.get('deleteBTN', '') != "": 
            #Obter a métrica
            basic = Basic.query.filter_by(user_id = current_user.id, id = request.args.get('deleteBTN', '')).first()
            print(basic.id)
            #Eliminar a métrica da API
            r = requests.get(daemons_api+'/Daemon/Remove/Basic',
                {"id":basic.id},
                headers={'Authorization': daemons_api_key})
            print(r.status_code)
            print(r.text)

            #Eliminar a métrica da base de dados influxDB
            client = InfluxDBClient(host='40.68.96.164', port=8086, username="peikpis", password="peikpis_2021")

            client.switch_database('Metrics')
            print(client.query("show measurements"))
            print(client.query("drop measurement \"" + str(basic.id)+"\""))
            print(client.query("show measurements"))
            client.close()

            #Eliminar a métrica da base de dados backoffice
            db.session.delete(basic)
            db.session.commit()

            flash('SUCESS: Metric deleted sucessfully', category='success')
        

    return render_template("mymetrics.html")





#Show a dashboard page
@views.route("/showdashboard/<userid>/<dname>", methods=["GET", "POST"])
@login_required
def showdashboard(userid, dname):
    
    theme = "Light"
    if request.method == "GET":
        theme = request.args.get('theme')
    
    #Obter a dashboard da base de dados
    dash = Dash.query.filter_by(user_id = userid, nome = dname).first()
    urls = []
    #Obter todos os painéis
    for i in range(1, dash.panels+1):
        if theme == "Dark":
            urls.append("http://40.68.96.164:3000/d-solo/"+dash.uid+"/"+dash.nome+"?panelId="+str(i)+"&theme=dark")
        else:
            urls.append("http://40.68.96.164:3000/d-solo/"+dash.uid+"/"+dash.nome+"?panelId="+str(i)+"&theme=light")
    
    if theme == "Light":
        return render_template("showdashboards.html",dname=dname, urls=urls, theme="Dark")
    if theme == "Dark":
        return render_template("showdashboards.html",dname=dname, urls=urls, theme="Light")

    return render_template("showdashboards.html",dname=dname, urls=urls, theme="Dark")



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

def get_int(str):
    if str == "5-em-5-minutos":
        return 5
    elif str == "30-em-30-minutos":
        return 30
    elif str == "hora-a-hora":
        return 60
    elif str == "diariamente":
        return 1440


def load_metrics():
    #Carregar métricas default e as suas Kpis   
    parking = Metrics(name='Parkings', 
    description="""Metric that represents the ocupations of the car parkings in the University of Aveiro.
    It contains informations about how many spots are occupied, free and the total number of spots of each 
    parking in the University.""")
    db.session.add(parking)
    db.session.commit()

    res = get_querys('parking')
    for v in res:
        db.session.add(Kpi(name=v[1], query=v[0], metrica_id=parking.id))
        db.session.commit()

    
    #Carregar métricas default e as suas Kpis   
    wifi = Metrics(name='Wifi Users', 
    description="""Metric that represents the number of devices connected to the University of Aveiro's
    endpoints. It contains informations about how many devices are connected to the several access poinst 
    per depertments from the University.""")
    db.session.add(wifi)
    db.session.commit()

    res = get_querys('wifiusr')
    for v in res:
        db.session.add(Kpi(name=v[1], query=v[0], metrica_id=wifi.id))
        db.session.commit()