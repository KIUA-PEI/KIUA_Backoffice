from sqlalchemy.sql.expression import null
from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType
from sqlalchemy.orm import backref, declarative_base

Base = declarative_base()


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    fname = db.Column(db.String(150))
    lname = db.Column(db.String(150))
    dashboards = db.relationship("Dashboard", backref='user', lazy=True)                # dashboards do utilizador
    metrics = db.relationship("MyMetrics", backref='user', lazy=True)                  # metricas do utilizador
    folder_id = db.Column(db.Integer, unique=True)
    admin = db.Column(db.Integer) #0->User, 1->Admin
    defaultmetrics = db.relationship("DefaultMetrics", backref="user", lazy=True)

    def __repr__(self):
        return "id: " + str(self.id) + ", email: " + self.email + ", " + self.fname + " " + self.lname

# user dashboards
class Dashboard(db.Model):
    __tablename__ = 'dashboard'

    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, unique=True)
    nome = db.Column(db.String(150), nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())                    # data de criação
    visibilidade = db.Column(db.Integer, nullable=False)                                # 0 -> privada, 1 -> pública
    url = db.Column(db.String(150), nullable=False)
    panels = db.Column(db.Integer, unique=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return "id: " + str(self.id) + "uid: " + str(self.uid) + "date: " + str(self.date) + "url: " + str(self.url) + ", user_id: " + str(self.user_id)

#Tabela metrics
class Metrics(db.Model, Base):
    __tablename__ = 'metrics'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500),nullable=False)
    name = db.Column(db.String(50),nullable=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())                    # data de criação
    args = db.Column(db.String(750),nullable=True)
    period = db.Column(db.Integer(), nullable=False)
    periodstr = db.Column(db.String(30), nullable=True)
    status = db.Column(db.Boolean(),default=True)
    type = db.Column(db.String(50))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity':'metrics',
    }


# user metrics
class MyMetrics(Metrics):
    __tablename__ = 'mymetrics'

    id = db.Column(db.Integer, db.ForeignKey('metrics.id'), primary_key=True)
    mykpi = db.relationship("MyKpi", backref="metrics", lazy=True)

    __mapper_args__ = {
        'polymorphic_identity':'mymetrics',
    }

# indicadores gerados para as métricas introduzidas pelo utilizador
# tem nome e query gerado automaticamente
class MyKpi(db.Model):
    __tablename__= 'mykpi'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=True)
    query = db.Column(db.String(300), nullable=True)

    my_metrica_id = db.Column(db.Integer, db.ForeignKey("mymetrics.id"))

## ----------
# métricas default do website
# uma métrica default, tem um nome, uma descrição usadas na página Métricas
# um métrica default tem ainda uma lista de kpis usadas para fazer display no website das métricas e indicadores default do website
class DefaultMetrics(Metrics):
    __tablename__ = 'defaultmetrics'

    id = db.Column(db.Integer, db.ForeignKey('metrics.id'), primary_key=True)
    description = db.Column(db.String(3000), nullable=True)
    kpi = db.relationship("Kpi", backref="defaultmetrics", lazy=True)

    __mapper_args__ = {
        'polymorphic_identity':'defaultmetrics',
    }


class Kpi(db.Model):
    __tablename__ = 'kpi'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column((db.String(100)))
    query = db.Column(db.String(300))

    metrica_id = db.Column(db.Integer, db.ForeignKey("defaultmetrics.id"), nullable=False)