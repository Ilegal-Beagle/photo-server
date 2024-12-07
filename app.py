from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def homePage():
    return render_template("home.html", person="Adrian")

@app.route("/start-comms")
def startCommunications():
    return render_template("client_page")

@app.route("/about")
def submit():
    return render_template("about.html")