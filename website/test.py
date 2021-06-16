from website.models import *
from . import db
from flask import Blueprint
from pprint import pprint as p
from influxdb import InfluxDBClient
from website.config import *
import requests

test = Blueprint("test", __name__)

@test.route("/filldatabasedefaultmetrics")
def metricas():
    data = [
        [
            "Estacionamentos", 
            "Descrição dos parques de estacionamento da UA",
            [
                ["Free parkings in the library", "SELECT Livre, Capacidade FROM parking WHERE Nome = 'Biblioteca' AND $timeFilter"],
                ["Occupied parkings in the library", "SELECT Ocupado, Capacidade FROM parking WHERE Nome = 'Biblioteca' AND $timeFilter"],
                ["Free Parkings in ESTGA" , "SELECT Livre, Capacidade FROM parking WHERE Nome = 'ESTGA' AND $timeFilter"],
                ["Occupied Parkings in ESTGA" , "SELECT Ocupado, Capacidade FROM parking WHERE Nome = 'ESTGA' AND $timeFilter"],
                ["Free Parkings in Incubadora" , "SELECT Livre, Capacidade FROM parking WHERE Nome = 'Incubadora' AND $timeFilter"],
                ["Occupied Parkings in Incubadora" , "SELECT Ocupado, Capacidade FROM parking WHERE Nome = 'Incubadora' AND $timeFilter"],
                ["Free Parkings in Subterraneo" , "SELECT Livre, Capacidade FROM parking WHERE Nome = 'Subterraneo' AND $timeFilter"],
                ["Occupied Parkings in Subterraneo" , "SELECT Ocupado, Capacidade FROM parking WHERE Nome = 'Subterraneo' AND $timeFilter"],
                ["Free Parkings in Residencias" , "  SELECT Livre, Capacidade FROM parking WHERE Nome = 'Residencias' AND $timeFilter"],
                ["Occupied Parkings in Residencias" , "SELECT Ocupado, Capacidade FROM parking WHERE Nome = 'Residencias' AND $timeFilter"]
            ]
        ], 
        [
            "Dispositivos ligados ao wi-fi",
            "Descreição dos dispositivos ligados à rede de Wi-fi",
            [ 
                ["Total devices connected to ua", "SELECT sum(wifiCount) as TotalUsers FROM wifiusr WHERE $timeFilter GROUP BY time(1h) fill(null)"],
                ["Total devices connected to library wifi", "SELECT wifiCount as UsersBiblioteca FROM wifiusr WHERE Nome = 'biblioteca' AND $timeFilter"],
                ["Total devices connected to aauav wifi", "SELECT wifiCount as UsersAAUAV FROM wifiusr WHERE Nome = 'aauav' AND $timeFilter"], 
                ["Total devices connected to cicfano wifi", "SELECT wifiCount as UsersCICFANO FROM wifiusr WHERE Nome = 'cicfano' AND $timeFilter"],
                ["Total devices connected to dao wifi", "SELECT wifiCount as UsersDAO FROM wifiusr WHERE Nome = 'dao' AND $timeFilter"],
                ["Total devices connected to dbio wifi", "SELECT wifiCount as UsersDBIO FROM wifiusr WHERE Nome = 'dbio' AND $timeFilter"],
                ["Total devices connected to dscpt wifi", "SELECT wifiCount as UsersDSCPT FROM wifiusr WHERE Nome = 'dscpt' AND $timeFilter"],
                ["Total devices connected to deca wifi", "SELECT wifiCount as UsersDECA FROM wifiusr WHERE Nome = 'deca' AND $timeFilter"],
                ["Total devices connected to deti wifi", "SELECT wifiCount as UsersDETI FROM wifiusr WHERE Nome = 'deti' AND $timeFilter"],
                ["Total devices connected to dmat wifi", "SELECT wifiCount as UsersDMAT FROM wifiusr WHERE Nome = 'dmat' AND $timeFilter"],
                ["Total devices connected to dcivil wifi", "SELECT wifiCount as UsersDCIVIL FROM wifiusr WHERE Nome = 'decivil' AND $timeFilter"],
                ["Total devices connected to dgeit wifi", "SELECT wifiCount as UsersDEGEIT FROM wifiusr WHERE Nome = 'degeit' AND $timeFilter"],
                ["Total devices connected to dep wifi", "SELECT wifiCount as UsersDEP FROM wifiusr WHERE Nome = 'dep' AND $timeFilter"],
                ["Total devices connected to dfis wifi", "SELECT wifiCount as UsersDFIS FROM wifiusr WHERE Nome = 'fis' AND $timeFilter"],
                ["Total devices connected to it wifi", "SELECT wifiCount as UsersIT FROM wifiusr WHERE Nome = 'it' AND $timeFilter"],
                ["Total devices connected to ietta wifi", "SELECT wifiCount as UsersIETTA FROM wifiusr WHERE Nome = 'ietta' AND $timeFilter"],
                ["Total devices connected to isca wifi", "SELECT wifiCount as UsersISCA FROM wifiusr WHERE Nome = 'isca' AND $timeFilter"],
                ["Total devices connected to dgeo wifi" , "SELECT wifiCount as UsersGEO FROM wifiusr WHERE Nome = 'geo' AND $timeFilter"],
            ]
        ]
    ]
    for d in data:
        m = Metrics(name=d[0], description=d[1])
        db.session.add(m)
        db.session.commit()
        for kpi in d[2]:
            k = Kpi(name=kpi[0], query=kpi[1], metrica_id=m.id)
            db.session.add(k)
            db.session.commit()
    db.session.commit()

    return "successfully added to db"

@test.route("/utilizadores")
def utilizadores():
    users = User.query.all()
    return str(users)

@test.route("/dashboards/<email>")
def dashboardByUser(email):
    user = User.query.filter_by(email=email).first()
    dashboards = user.dashboards
    return str(dashboards)


@test.route("/fill")
def fill():
    user = User.query.filter_by(email="pedro.abreu@ua.pt").first()

    uid = "12334542"
    visibilidade = "1"
    url = "https://hbvhidbvidvidgv"


    d1 = Dashboard(uid=uid, visibilidade=visibilidade, url=url, user_id = user.id)

    uid = "35849596"
    visibilidade = "0"
    url = "https://hbvhidbsvvpgv"

    d2 = Dashboard(uid=uid, visibilidade=visibilidade, url=url, user_id = user.id)

    db.session.add(d1)
    db.session.add(d2)
    db.session.commit()

    return str(user.dashboards)

@test.route("/testdb")
def testdb():
    # create a user
    user = User.query.filter_by(email="pedro.abreu@ua.pt").first()

    # create dashboards of user
    d1 = Dashboard(uid="92384721", nome="dash1", visibilidade=1, url="https://hbvhidbsvvpgv", user_id=user.id)
    db.session.add(d1)
    d2 = Dashboard(uid="2348432", nome="dash2", visibilidade=0, url="https://hbvhidbsvvp.fubrf", user_id=user.id)
    db.session.add(d2)

    # create metrics of user
    m1 = Basic(url="https://hbvhidbsvvpgv", name="metric1", period=5, periodstr="5 minutos", type="basic", user_id=user.id)
    db.session.add(m1)
    m2 = Http(url="https://hbvhidbsvvpgv", name="metric2", period=10, periodstr="10 minutos", type="key", user_id=user.id)
    db.session.add(m2)

    db.session.commit()

    return str(user)


@test.route("/getmeasurements")
def test_measurements():

    #Open Client
    client = InfluxDBClient(host='40.68.96.164', port=8086, username="peikpis", password="peikpis_2021")

    #Switch to Metrics database
    print("Test:")
    client.switch_database('Test')
    print(client.query("show measurements"))
    print("Metrics")
    client.switch_database('Metrics')
    print(client.query("show measurements"))
    print("_internal")
    client.switch_database('_internal')
    print(client.query("show measurements"))

    client.close()

    return "gude"


@test.route("/delete/<id>")
def delete_id(id):
    #Open Client
    client = InfluxDBClient(host='40.68.96.164', port=8086, username="peikpis", password="peikpis_2021")

    #Switch to Metrics database
    print("Metrics:")
    client.switch_database('Metrics')
    print(client.query("show measurements"))
    print(client.query("drop measurement \"" + id+"\""))
    print(client.query("show measurements"))
    client.close()

    print("pronto a enviar...")
    r = requests.get(daemons_api+'/Daemon/Remove/Basic',
        {"id":id},
        headers={'Authorization': daemons_api_key})
    print(r.status_code)
    print(r.text)

    return str(r)

@test.route("/deleteDummyMetric")
def delete_metric():
    u = MyKpi.query.filter_by(id == 1).first()
    db.session.delete(u)
    db.session.commit()
    return "all gude now"