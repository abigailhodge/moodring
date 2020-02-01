
from flask import Flask, render_template, redirect, request, session
from gensim.models import KeyedVectors
from numpy import array, mean
import pickle
from datetime import datetime, timedelta
from flask_pymongo import PyMongo
from pymongo import MongoClient
import os
import plotly
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import json
import numpy as np


# https://stackoverflow.com/questions/53682647/mongodb-atlas-authentication-failed-on-python

client=MongoClient("mongodb+srv://sjhbluhm:123password!@cluster0-o0tfo.mongodb.net/test?retryWrites=true&w=majority")
#db = client.test
db = client["moodring"]
collection = db["moodring"]
client.server_info()
try:
    print("connected to Mongodb server")
except:
	print("connection failure")



try:
	client = MongoClient("mongodb+srv://sjhbluhm:123password!@cluster0-o0tfo.mongodb.net/test?retryWrites=true&w=majority")
	client.server_info()
	db = client["moodring"]
	collection = db["moodring"]
	print("connected to Mongodb server")
except:
	print("connection failure")


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
 
        if not w2v_model:
            w2v_model = KeyedVectors.load_word2vec_format('ml_code/GoogleNews-vectors-negative300.bin', binary=True)
        print('finished loading w2v')
        super(ModelApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


app = ModelApp(__name__)
app.run()
app.config["TEMPLATES_AUTO_RELOAD"]

#client = MongoClient("mongodb://127.0.0.1:27017")


@app.route("/")
def hello():
    bar = create_plot()
    
    global collection
    results = collection.find({})
    for result in results:
        	print(result)
        	
    return render_template('index.html', plot=bar)


@app.route("/add_entry", methods=["GET", "POST"])

# default goal_display is current time, at EST. takes in form input if posted
def add_entry():
    if request.method == "GET":

        return render_template("addentry.html")
    else:
        journal = request.form.get("journal")
<<<<<<< HEAD
        
        #year=datetime.now().year
        #month=datetime.now().month
        #day=datetime.now().day
        #print(year)
        #https://api.mongodb.com/python/current/examples/datetimes.html
        sentiment=get_sentiment(journal)
        
        entry = {"date":datetime.utcnow(), "text":journal, "sentiment":sentiment}

        collection.insert_one(entry)
        
        results = collection.find({})
        for result in results:
        	print(result)
        
        return render_template("index.html", month=month, d=day, year=year)

        #get_sentiment(journal)
        bar = create_plot()
        return render_template("index.html", plot=bar)

        year=(datetime.now() - timedelta(hours=5)).year
        month=(datetime.now() - timedelta(hours=5)).month
        day=(datetime.now() - timedelta(hours=5)).month

        sentiment=get_sentiment(journal)
        
        entry = {"date":day, "text":journal, "sentiment":sentiment}
        global collection
        collection.insert_one(entry)
        
        return render_template("index.html", month=month, day=day, year=year)



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
    return result


sample_df = df = pd.DataFrame(
    {'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'review': ["mediocre", "not great", "wonderful", "best day ever to exist", "i am feeling sad", "hello", "another message", "hi", "this is the ninth message", "finally complete"],
    'tag': [1, -1, -1, 1, 1, 1, -1, 1, 1, -1],
    'date': ["YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss"]
    }
)

def create_plot():
    data = [
        go.Bar(
            x=sample_df['id'], # assign x as the dataframe column 'x'
            y=sample_df['tag']
        )
    ]

    # graph option 1: color gradient scatterplot, color represents review length, position represents tag
    fig1 = px.scatter(
        sample_df, 
        x="id", 
        y=sample_df['review'].str.len(), 
        color=sample_df['review'].str.len()
    )

    # graph option 2: polar barplot w/ height representing review length, color representing tag, hover shows text
    fig2 = go.Figure(
        go.Barpolar(
            r = sample_df['review'].str.len(),
            theta = np.arange(0, 360, 360/sample_df['id'].count()),
            text = sample_df['review'],
            width = 20,
            marker_color=sample_df['tag'].map({-1:"#4037b8", 1:"#f0cb46"}),
            marker_line_color="black",
            marker_line_width=2,
            opacity=0.8,
            hoverinfo='text'
        )
    )

    graphJSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

