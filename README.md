# moodring
Moodring app for TechTogether Boston 2020
Winner of the Facebook Building Community Challenge

## TEAM MEMBERS
Abigail Hodge

Megan Li

Jacqueline Lincroft

[Vanessa Hu]("https://github.com/vanessa-hu")

Sarah Bluhm

## Inspiration
In an age of often isolating social media profiles, it can be easy to forget how our feelings and attitudes impact the world around us, and how others are more similar to us than we realize. moodring pools together the sentiment of the anonymous thoughts of everyone who uses it—no matter their language—to create a visual representation of the world’s honest emotions over the course of a day. 

## What it does
When a user visits moodring, they are greeted with two views. The first view allows the user to enter anything they want—a rant about their parents, their excitement at landing a new job, a random bit of poetry, how they really feel about Avengers: Endgame. Their message is then fed into a machine learning model and scored as either positive or negative. The user can use whatever language they wish, as the Google Translate API translates all messages into English before they are fed into the model, allowing anyone to put their thoughts into moodring without the need to train dozens of sentiment analysis models. 

The second view aggregates all the messages from the past day. It displays both a list of messages color coded by sentiment, and a “ring” of hourly averages—giving a visual depiction of the ebb and flow of the worlds’ sentiments over the course of a day.

## How we built it

### Sentiment analysis

To train our sentiment analysis classifier, we utilized an open dataset of IMDB reviews categorized by sentiment. This dataset can be located at http://ai.stanford.edu/~amaas/data/sentiment/ 
Citation: Andrew L. Maas, Raymond E. Daly, Peter T. Pham, Dan Huang, Andrew Y. Ng, and Christopher Potts. (2011). Learning Word Vectors for Sentiment Analysis. The 49th Annual Meeting of the Association for Computational Linguistics (ACL 2011).

We built a multi-layer perceptron in sk-learn, utilizing word2vec vector averages as features. word2vec was limited to the 50,000 most common words in English, allowing it to load significantly faster in the app when we later classified user input without a significant loss in accuracy. We determined hyperparameters using a grid search with 10-fold cross validation. Our final model had an accuracy of 83% on the IMDB test data. We then dumped our model into a .sav file and loaded it into our flask application, allowing moodring to use the model without the need for retraining every time the app was reset.

The machine learning code can be found in a jupyter notebook at https://github.com/abigailhodge/moodring/blob/master/ml_code/moodring-trainer.ipynb

### Database

We set up our non-relational database using MongoDB, hosted with AWS. It stored each anonymous entry with its date (datetime object), text, as well as separate fields for month, day, hour, and year for easier entry retrieval when needing to display data based on specific times.

### Web App Framework

moodring is built in Python using the Flask framework. It is hosted using Google App Services. We built this web application using Python, HTML/CSS, the Jinja framework, Flask to route between HTML/CSS pages, as well as Javascript. Custom CSS and Bootstrap provides our clean and friendly UI.

Our homepage (index.html) “/” route uses a later defined function to return plots based on sentiment analysis entries, and the averages of each hour for the past 24 hours, displaying them in the HTML file with Javascript. It also accesses all the entries in our database and passes its information to be displayed dynamically via Javascript, which shows the anonymous messages in the Recent Entries section and are color-coded by its sentiment result: purple for negative and pale yellow for positive. 

Our Add Your Entry page (addentry.html) displays a simple message entry form, that when submitted, sends a POST request received by Python via Flask. In Python, the entry is run through the Google Translate API, and the translated text is fed into our machine learning model and classified as positive or negative. The creation date, (original, non-translated) text, and classification are then written into our database, thus updating the data visualizations on our home screen. 


### Data visualization

We used panda and numpy to clean and map our data, and plot.y to create the polar bar chart.  We developed several iterations of the primary data visualization before settling on the final output, including polar scatter plots, linear histograms, and variations in continuous and discrete color scales.  One thing we struggled with in creating the data visualization was finding a fun and exciting way to display pretty uninteresting binary data – since our ML sentiment analysis model only output a binary positive or negative value, a lot of our initial graphs looked pretty boring with only two colors.  Since we initially chose the name moodring somewhat randomly, we thought it would be fun to tie everything together with some sort of circular visualization, leading us eventually to the polar bar plot.  We also decided to instead aggregate our data into hourly average sentiment values, so we could play with a continuous color scale that looked a little more exciting. 


## What we learned

Our diverse team consisted of beginner to experienced programmers. Each of us rose to meet new challenges, all of us open-minded to learning to use a new web framework, database, or web-app host. We learned to work together and break down daunting tasks into manageable chunks. We had to identify our strengths, unite them in a creative endeavor, and, most importantly, trust in our potential to succeed. Through this project, we augmented our problem-solving and collaborative skills while simultaneously expanding our technical toolbox. 


## What's next for moodring

We would love to expand moodring to display more data visualizations illustrating more specific ranges of emotion, from anger to confusion to joy, by training machine learning models on emotional analysis datasets. Future moodring versions would feature an optional login and user authentication to enable users to monitor their emotional changes and well-being over time. In the future, it would be great to map aggregate emotion analysis of all users over time, even being able to filter by location or date to display emotional variation across time and space.

