from website.models import *
from . import db
from flask import Blueprint

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