from website.models import *
from . import db
from flask import Blueprint
from pprint import pprint as p

test = Blueprint("test", __name__)

@test.route("/metricasdb")
def metricas():
    data = [
        ["Estacionamentos", 
            [   "num. lugares ocupados Residencias", 
                "num. lugares ocupados Biblioteca", 
                "variação num. lugares ocupados Residencias", 
                "variação num. lugares ocupados Biblioteca", 
                "num. total de lugares ocupados em todos os estacionamentos"]
            ], 
        ["Wifi Users", 
            [
                "num. disp. ligados na biblioteca",
                "num. disp. ligados no Deti",
                "num. disp. ligados no CPCT",
                "variação num. disp. ligados na biblioteca",
                "variação num. disp. ligados no Deti",
                "variação num. disp. ligados no CPCT",
                "num. de disp. ligados em todos os departamentos edifícios"
            ]
        ]
    ]
    for d in data:
        db.session.add(Metrics(name=d[0]))
        metrica_id = Metrics.query.filter_by(name=d[0]).first().id
        for kpi in d[1]:
            db.session.add(Kpi(name=kpi, metrica_id=metrica_id))
        db.session.commit()

    return "added to db"

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
    m1 = Basic(url="https://hbvhidbsvvpgv", name="metric1", type="basic")
    db.session.add(m1)
    m2 = Http(url="https://hbvhidbsvvpgv", name="metric2", type="http")
    db.session.add(m2)

    return str(user)