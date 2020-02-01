from flask import Flask, render_template, redirect, request, session
from datetime import datetime, timedelta
from flask_pymongo import PyMongo
from pymongo import MongoClient
import os


app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"]
app.config["MONGO_URI"] = "mongodb://localhost:27017/db"
mongo = PyMongo(app)
client = MongoClient("mongodb://127.0.0.1:27017")


@app.route("/")
def hello():
    hi = "hello"
    return render_template('index.html', hi=hi)

if __name__ == "__main__":
    app.run()

@app.route("/add_entry", methods=["GET", "POST"])

# default goal_display is current time, at EST. takes in form input if posted
def add_entry():
    if request.method == "GET":
        return render_template("addentry.html")
    else:
        journal = request.form.get("journal")
        year=(datetime.now() - timedelta(hours=5)).year
        month=(datetime.now() - timedelta(hours=5)).month
        day=(datetime.now() - timedelta(hours=5)).month
        return render_template("index.html", month=month, day=day, year=year)