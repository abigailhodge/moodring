from flask import Flask, render_template, redirect, request, session
from gensim.models import KeyedVectors
from numpy import array, mean
import pickle
from datetime import datetime, timedelta
from flask_pymongo import PyMongo

import plotly
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np

w2v_model = None
sent_model = None


class ModelApp(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        print('HIT HERE')
        global sent_model
        global w2v_model
        if not sent_model:
            sent_model = pickle.load(open('ml_code/model.sav', 'rb'))
        print('finished loading sentence model')
        #if not w2v_model:
        #    w2v_model = KeyedVectors.load_word2vec_format('ml_code/GoogleNews-vectors-negative300.bin', binary=True)
        #print('finished loading w2v')
        super(ModelApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)

app = ModelApp(__name__)
app.run()
app.config["TEMPLATES_AUTO_RELOAD"]
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)


@app.route("/")
def hello():
    bar = create_plot()
    return render_template('index.html', plot=bar)


@app.route("/add_entry", methods=["GET", "POST"])

# default goal_display is current time, at EST. takes in form input if posted
def add_entry():
    if request.method == "GET":

        return render_template("addentry.html")
    else:
        journal = request.form.get("journal")
        #get_sentiment(journal)
        bar = create_plot()
        return render_template("index.html", plot=bar)


def get_sentiment(entry):
    global w2v_model
    global sent_model
    word_list = entry.split()
    sentiment_list = []
    for word in word_list:
        if word in w2v_model:
            sentiment_list.append(w2v_model[word])
    vector_array = array(sentiment_list)
    avg_sent = mean(vector_array, axis=0).reshape(1, -1)
    result = sent_model.predict(avg_sent)[0]
    if result == 1:
        print('positive entry', entry)
    else:
        print('negative entry', entry)


sample_df = df = pd.DataFrame({'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 'tag': [1, -1, -1, 1, 1, 1, -1, 1, 1, -1]})

def create_plot():
    data = [
        go.Bar(
            x=sample_df['id'], # assign x as the dataframe column 'x'
            y=sample_df['tag']
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
