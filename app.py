import imp
from posixpath import commonpath
from flask import Flask, request, jsonify
from scraping.twitter_scraper import *
from scraping.fb_scraper import *
from scraping.url_scraper import *
from flask_cors import CORS
from utility import *

from search_google import *
#from image_process import *


app = Flask(__name__)
CORS(app)
base_dir = './'
### Check if server is suning successfully ###


@app.route('/')
def hello_world():
    return 'Rumour-Reckon Backend running!'


# Provides the current status of the analysis
status = 0


@app.route('/status')
def getStatus():
    print(status)
    return str(status)

### Individual tweet details (without comments)  ###


@app.route('/tweet-scrape')
def scrape_twitter():
    id = request.args.get('id')
    tweet = getTweet(id)
    print(tweet)
    print("Image analysis: ")
    # print(analyze_image(tweet['media'][0]['image_url']))
    result = process_data(tweet['text'])
    return result


@app.route('/tweet-comments-scrape')
def scrape_twitter_comments():
    id = request.args.get('id')
    comments = getTweetComments(id)
    return jsonify(comments)


@app.route('/facebook-scrape')
def scrape_facebook():
    id = request.args.get('id')
    post = scrapePosts(id)
    print(post)
    print("Image analysis: ")
    # print(analyze_image(post['image']))
    result = process_data(post['post_text'])

    return result


@app.route('/url-scrape', methods=['POST'])
def predict():
    if request.method == 'POST':
        data = request.get_json()
        content = process_input(data['link'])
        return content
    else:
        return "Something went wrong"


@app.route('/plain-text')
def analyze_text():
    text = request.args.get('text')

    print(text)

    result = process_data(text)

    return result
