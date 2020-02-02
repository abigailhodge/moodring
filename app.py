
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
from google.cloud import translate_v2 as translate

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
translate_client = None

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

    for result in collection.find({}).sort("dtstamp",-1):
        i = result["dtstamp"]
        j = result["text"]
        k = result["sentiment"]
        arr_entries.append([i, j, k])
    
    
    #find the average of past day's sentiment
    sum = entries = 0
    datetimestamp=datetime.utcnow()
    results = collection.find({"day":datetimestamp.strftime("%d "),"month":datetimestamp.strftime("%m "), "year":datetimestamp.strftime("%Y ")})
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
        global translate_client
        if not sent_model:
            sent_model = pickle.load(open('ml_code/model.sav', 'rb'))
            print('finished loading sentence model')
        if not w2v_model:
            w2v_model = pickle.load(open('ml_code/vectors.sav', 'rb'))
            print('finished loading w2v')
        if not translate_client:
            translate_client = translate.Client()
        journal = request.form.get("journal")
        bar = create_plot()
        sentiment=get_sentiment(journal)
        datetimestamp=datetime.utcnow()
        entry = {"dtstamp":datetimestamp, "text":journal, "sentiment":sentiment, "hour":datetimestamp.strftime("%H "), "day":datetimestamp.strftime("%d "), "month":datetimestamp.strftime("%m "), "year":datetimestamp.strftime("%Y ")}
        global collection
        collection.insert_one(entry)
        return redirect("/")


def get_sentiment(entry):
    global w2v_model
    global sent_model
    global translate_client
    response = translate_client.translate(entry, target_language='en')
    translation = response['translatedText']
    print(translation)
    word_list = translation.split()
    sentiment_list = []
    for word in word_list:
        lowercase_word = word.lower()
        if lowercase_word  in w2v_model:
            sentiment_list.append(w2v_model[lowercase_word ])
    if len(sentiment_list) > 0:
    	vector_array = array(sentiment_list)
    	avg_sent = mean(vector_array, axis=0).reshape(1, -1)
    	result = sent_model.predict(avg_sent)[0]
    else:
    	result = 0
    return int(result)


def create_plot():
    global collection
    results = collection.find({})
    journals = []
    tags = []
    dates = []
    for r in results:
        journals.append(r["text"])
        dates.append(r['day'])
        tags.append(r['sentiment'])
    ids = range(1,len(journals)+1)
    sample_df = df = pd.DataFrame(
        {'id': ids,
        'review': journals,
        'tag': tags,
        'date': dates
        }
    )

    hraverage = []
    now = datetime.utcnow()
    for i in range(24):
    	avrg = 0
    	sum = 0
    	entries = 0
    	then = now - timedelta(hours=i)
    	results = collection.find({"hour":then.strftime("%H "),"day":then.strftime("%d "),"month":then.strftime("%m "), "year":then.strftime("%Y ")})
    	for result in results:
    		sum += result["sentiment"]
    		entries += 1
    	if entries > 0:
    		avrg = sum/entries
    	else:
    		avrg = 0
    	hraverage.append(avrg)
    print(hraverage)
    avg_ids = range(24,0,-1)
    sample_df2 = df2 = pd.DataFrame(
        {'id': avg_ids,
        'average':hraverage
        }
    )
    # graph option 2: polar barplot w/ binary height, color represents string length
    fig2 = px.bar_polar(
        sample_df2,
        r=sample_df2['average'].add(1),
        theta=np.arange(0, 360, 360/24),
        color=sample_df2['average'],
        color_continuous_scale=['purple', 'yellow']
        )
    fig2.update_layout(
        title='World Mood',
        plot_bgcolor='rgb(10,10,10)',
        
        polar = dict(
        radialaxis = dict(range=[0,2.5], showticklabels=False, ticks=''),
        angularaxis = dict(showticklabels=False, ticks='')
        )
    )

    graphJSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

