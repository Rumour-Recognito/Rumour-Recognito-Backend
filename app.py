import imp
import csv
from posixpath import commonpath
from flask import Flask, request, jsonify
from scraping.twitter_scraper import *
from scraping.fb_scraper import *
from translate_text import *
from scraping.url_scraper import *
from search_google import *
from pred import *
from flask_cors import CORS
from sentimental_analysis import *

app = Flask(__name__)
CORS(app)
base_dir = './'
### Check if server is suning successfully ###


@app.route('/')
def hello_world():
    return 'Rumour-Reckon Backend running!'

### Individual tweet details (without comments)  ###


@app.route('/tweet-scrape')
def scrape_twitter():
    id = request.args.get('id')
    tweet = getTweet(id)
    return tweet


@app.route('/tweet-comments-scrape')
def scrape_twitter_comments():
    id = request.args.get('id')
    comments = getTweetComments(id)
    return jsonify(comments)


@app.route('/facebook-scrape')
def scrape_facebook():
    id = request.args.get('id')
    post = scrapePosts(id)
    return post


@app.route('/translate')
def translate_text():
    text = request.args.get('text')
    translated_text = translate_to_english(text)
    return translated_text


@app.route('/search-google-links')
def google_search_links():
    query = request.args.get('query')
    limit = request.args.get('limit')
    results = search_google(query, limit)
    return results


@app.route('/search-google-content')
def google_search_content():
    query = request.args.get('query')
    limit = request.args.get('limit')

    allContents = google_search_content(query, limit)
    dict = {}
    dict['data'] = allContents

    return dict


def google_search_content(query, limit):

    results = search_google(query, limit)
    allContents = []

    for link in results['results']:
        content = process_input(link)
        allContents.extend(content['paragraphs'])

    return allContents


@app.route('/url-scrape', methods=['POST'])
def predict():
    if request.method == 'POST':
        data = request.get_json()
        content = process_input(data['link'])
        return content
    else:
        return "Something went wrong"


@app.route('/query-list', methods=['POST'])
def sendQuery():
    if request.method == 'POST':
        data = request.get_json()

        counter = 1
        bodies = []
        bodiesColumnTitles = ['Body ID', 'articleBody']
        headings = []
        headingsColumnTitles = ['Headline', 'Body ID']

        sentences = data['queryList']
        for sentence in sentences:
            allContent = google_search_content(sentence, 5)

            for content in allContent:
                bodies.append([counter, content])
                headings.append([sentence, counter])
                counter += 1

        with open('./data/test_bodies.csv', 'w', encoding="utf-8") as f:
            write = csv.writer(f)
            write.writerow(bodiesColumnTitles)
            write.writerows(bodies)

        with open('./data/test_stances_unlabeled.csv', 'w', encoding="utf-8") as f:
            write = csv.writer(f)
            write.writerow(headingsColumnTitles)
            write.writerows(headings)

        dict = {}
        dict['heading'] = headings
        dict['body'] = bodies

        return dict
    else:
        return "Something went wrong"


@app.route('/execute')
def stance_detect():

    load()

    predictions = []
    with open('./result/predictions_test.csv', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        for each in data:
            predictions.extend(each)
        predictions.remove("Prediction")

    bodies = []
    with open('./data/test_bodies.csv', newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        data = list(reader)

        for each in data:
            if(len(each) == 2):
                bodies.append(each[1])

        bodies.remove("articleBody")

    headlines = []
    with open('./data/test_stances_unlabeled.csv', newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        data = list(reader)

        for each in data:
            if(len(each) == 2):
                headlines.append(each[0])

        headlines.remove("Headline")

    score = sentimental_analysis(predictions, headlines, bodies)

    for prediction in predictions:
        if(prediction == 'agree'):
            score += 1
        elif(prediction == 'disagree'):
            score -= 1

    print(score)

    if(score > 0):
        return "LOOKS REAL"
    elif(score < 0):
        return "LOOKS FAKE"
    else:
        return "UNPREDICTABLE"
