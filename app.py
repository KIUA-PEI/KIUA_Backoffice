from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def login():
    return render_template("index.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/home')
def home():
    return render_template("home.html")