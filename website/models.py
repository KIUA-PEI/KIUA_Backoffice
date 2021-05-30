
from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    fname = db.Column(db.String(150))
    lname = db.Column(db.String(150))
    # dashboards do utilizador
    dashboards = db.relationship("Dashboard", backref='user', lazy=True)
    # metricas do utilizador(dividas pelo tipo de api)
    basic = db.relationship("Basic_url", backref="user", lazy=True)
    key = db.relationship("Key_url", backref="user", lazy=True)
    http = db.relationship("Http_url", backref="user", lazy=True)
    token = db.relationship("Token_url", backref="user", lazy=True)

class Dashboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, unique=True)
    # data criação
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    # small description
    description = db.Column(db.String(250))
    visibilidade = db.Column(db.Integer, nullable=False) # 0 -> privada, 1 -> pública
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    panels = db.relationship("Panels", backref="dashboard", lazy=True)


# cada gráfico de uma dashboard
class Panels(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kpi = db.Column(MutableList.as_mutable(PickleType)) # lista com o nome dos kpi que o utilizador selecionou na checkbox
    dashboard_id = db.Column(db.Integer, db.ForeignKey("dashboard.id"), nullable=False)

## ----------
# métricas default do website
class Metrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    kpis = db.relationship("Kpi", backref="metrics", lazy=True)


class Kpi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column((db.String(100)))
    metrica_id = db.Column(db.Integer, db.ForeignKey("metrics.id"), nullable=False)

## ------------

class Basic_url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500),nullable=False)
    # data criação
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    args = db.Column(db.String(750),nullable=True)
    period = db.Column(db.Integer(), nullable=False)
    status = db.Column(db.Boolean(),default=True)
    error = db.Column(db.String(75))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"API(URL = {self.url}, period={self.period}, status = {self.status})"
      
class Key_url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500),nullable=False)
    # data criação
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    args = db.Column(db.String(750),nullable=True)
    period = db.Column(db.Integer())
    key = db.Column(db.String(300))
    status = db.Column(db.Boolean(),nullable=False,default=True)
    error = db.Column(db.String(75))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"API(URL={self.url}, period={self.period},status={self.status})"
    
class Http_url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500),nullable=False)
    # data criação
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    args = db.Column(db.String(750),nullable=True)
    period = db.Column(db.Integer())
    key = db.Column(db.String(300))
    username = db.Column(db.String(300))
    status = db.Column(db.Boolean(),nullable=False,default=True)
    error = db.Column(db.String(75))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"API(URL={self.url}, period={self.period},status={self.status})"  
    
class Token_url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500),nullable=False)
    # data criação
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    token_url = db.Column(db.String(500),nullable=False)
    args = db.Column(db.String(750),nullable=True)
    period = db.Column(db.Integer())
    key = db.Column(db.String(300))
    secret = db.Column(db.String(300))
    content_type = db.Column(db.String(50))
    auth_type = db.Column(db.String(50))
    status = db.Column(db.Boolean(),nullable=False,default=True)
    error = db.Column(db.String(75))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"API(URL={self.url}, period={self.period}, status={self.status})"