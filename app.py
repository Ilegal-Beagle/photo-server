from flask import Flask, render_template, request
import client
import server

app = Flask(__name__)

@app.route("/")
def homePage():
    return render_template("home.html")

@app.route("/client-page")
def startCommunications():
    return render_template("client_page.html")

@app.route("/about")
def submit():
    return render_template("about.html")