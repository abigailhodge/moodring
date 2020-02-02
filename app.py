
from flask import Flask, render_template, redirect, request, session
from gensim.models import KeyedVectors
from numpy import array, mean
import pickle
from datetime import datetime, timedelta, date
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
#mongo_uri = os.environ.get('MONGO_URL')

class JournalEntry:
    def __init__(self, date, text, sentiment):
        self.date = date
        self.text = text
        self.sentiment = sentiment

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

        super(ModelApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)



app = ModelApp(__name__)
if __name__ == '__main__':

    app.run()
    app.config["TEMPLATES_AUTO_RELOAD"]



@app.route("/")
def hello():
    bar = create_plot()
    
	#create array of previous entries newest to oldest
    arr_entries = []
    global collection

    for result in collection.find({}).sort("date",-1):
        i = result["date"]
        j = result["text"]
        k = result["sentiment"]
        arr_entries.append([i, j, k])
    
    #find the average of past day's sentiment
    sum = entries = 0
    datetimestamp=datetime.utcnow()
    results = collection.find({"day":datetimestamp.strftime("%d %b %Y ")})
    for result in results:
    		sum += result["sentiment"]
    		entries += 1
    if entries > 0:
    	todaysentiment = sum/entries
    else:
    	todaysentiment = 0
    print(todaysentiment)
    
    return render_template('index.html', plot=bar, arr_entries=arr_entries, index="active",entries="inactive", todaysentiment=todaysentiment)


@app.route("/add_entry", methods=["GET", "POST"])

# default goal_display is current time, at EST. takes in form input if posted
def add_entry():
    if request.method == "GET":

        return render_template("addentry.html")
    else:
        global sent_model
        global w2v_model
        if not sent_model:
            sent_model = pickle.load(open('ml_code/model.sav', 'rb'))
            print('finished loading sentence model')

        if not w2v_model:
            w2v_model = pickle.load(open('ml_code/vectors.sav', 'rb'))
            print('finished loading w2v')
        journal = request.form.get("journal")
        bar = create_plot()
        sentiment=get_sentiment(journal)
        
        datetimestamp=datetime.utcnow()
        entry = {"date":datetimestamp, "text":journal, "sentiment":sentiment, "day":datetimestamp.strftime("%d %b %Y " )}
        global collection
        collection.insert_one(entry)
        return redirect("/")


def get_sentiment(entry):
    global w2v_model
    global sent_model
    word_list = entry.split()
    sentiment_list = []
    for word in word_list:
        if word in w2v_model:
            sentiment_list.append(w2v_model[word])
    if len(sentiment_list) > 0:
    	vector_array = array(sentiment_list)
    	avg_sent = mean(vector_array, axis=0).reshape(1, -1)
    	result = sent_model.predict(avg_sent)[0]
    else:
    	result = 0
    return int(result)


sample_df = df = pd.DataFrame(
    {'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'review': ["mediocre", "not great", "wonderful", "best day ever to exist", "i am feeling sad", "hello", "another message", "hi", "this is the ninth message", "finally complete"],
    'tag': [1, -1, -1, 1, 1, 1, -1, 1, 1, -1],
    'date': ["YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss", "YYYY-mm-ddTHH:MM:ss"]
    }
)

def create_plot():
    
    # graph option 1: polar barplot w/ binary color, height represents string length
    fig1 = go.Figure(
        go.Barpolar(
            r = sample_df['review'].str.len(),
            theta = np.arange(0, 360, 360/sample_df['id'].count()),
            text = sample_df['review'],
            width = 20,
            marker_color=sample_df['tag'].map({-1:"#d67499", 1:"#83ccaa"}),
            marker_line_color="black",
            marker_line_width=2,
            opacity=0.8,
            hoverinfo='text',
            showlegend=False,
        )
    )
    fig1.update_layout(
        title='World Mood',
        plot_bgcolor='rgb(10,10,10)',
        
        polar = dict(
        radialaxis = dict(range=[0, 30], showticklabels=False, ticks=''),
        angularaxis = dict(showticklabels=False, ticks='')
        )
    )

    # graph option 2: polar barplot w/ binary height, color represents string length
    fig2 = px.bar_polar(
        sample_df,
        r=sample_df['tag'].map({-1:1, 1:2}),
        theta=np.arange(0, 360, 360/sample_df['id'].count()),
        color=sample_df['review'].str.len(),
        color_discrete_sequence=px.colors.sequential.Plasma_r,
        hover_name=sample_df['review'],
        #hover_data=none
        )
    fig2.update_layout(
        title='World Mood',
        plot_bgcolor='rgb(10,10,10)',
        
        polar = dict(
        radialaxis = dict(range=[0, 2.5], showticklabels=False, ticks=''),
        angularaxis = dict(showticklabels=False, ticks='')
        )
    )

    # graph option 3: scatterplot w/ binary shape and radius placement, color represents string length
    fig3 = px.scatter_polar(
        sample_df,
        r=sample_df['tag'].map({-1:1, 1:2}),
        theta=np.arange(0, 360, 360/sample_df['id'].count()),
        color=sample_df['review'].str.len(),
        symbol=sample_df['tag'],
        color_discrete_sequence=px.colors.sequential.Plasma_r,
        hover_name='review'
        )
    fig3.update_traces(marker=dict(size=25))
    fig3.update_layout(
        title='World Mood',
        plot_bgcolor='rgb(10,10,10)',
        
        polar = dict(
        radialaxis = dict(range=[0, 2.5], showticklabels=False, ticks=''),
        angularaxis = dict(showticklabels=False, ticks='')
        )
    )

    graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

