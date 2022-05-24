from flask import Flask, request, jsonify
import pymongo
from scraping.twitter_scraper import *
from scraping.fb_scraper import *
from scraping.url_scraper import *
from flask_cors import CORS
from utility import *
from search_google import *
from image_process import *


app = Flask(__name__)
CORS(app)
base_dir = './'

myclient = pymongo.MongoClient("mongodb+srv://squadra:1234@cluster0.wiuug.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["rumor_recognito_db"]
mycol = mydb["progress"]
mycol.update_many({}, [{'$set': {'status': -1}}])

### Check if server is suning successfully ###
@app.route('/')
def hello_world():
    return 'Rumour-Reckon Backend running!'


# Provides the current status of the analysis
@app.route('/status')
def getStatus():
    data = mycol.find_one()
    return str(data['status'])

### Individual tweet details (without comments)  ###
@app.route('/tweet-scrape')
def scrape_twitter():
    mycol.update_many({}, [{'$set': {'status': 0}}])
    data = request.get_json()
    id = tweet_id_extract(data['link'])
    print(id)
    tweet = getTweet(id)
    print(tweet)
    print("Image analysis: ")
    print(analyze_image(tweet['media'][0]['image_url']))
    result = process_data(tweet['text'])
    return result


@app.route('/tweet-comments-scrape')
def scrape_twitter_comments():
    id = request.args.get('id')
    comments = getTweetComments(id)
    return jsonify(comments)


@app.route('/facebook-scrape')
def scrape_facebook():
    mycol.update_many({}, [{'$set': {'status': 0}}])
    data = request.get_json()
    id = fb_id_extract(data['link'])
    print(id)
    post = scrapePosts(id)
    print(post)
    if(post['image'] != None):
        print("Image analysis: ")
        print(analyze_image(post['image']))
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

    mycol.update_many({}, [{'$set': {'status': 0}}])

    text = request.args.get('text')

    print(text)

    result = process_data(text)

    return result

@app.route('/analyze-image', methods=['POST'])
def analyze():
    mycol.update_many({}, [{'$set': {'status': 0}}])
    file = request.files['file']
    file.save(os.path.join(base_dir, "image.jpg"))
    text = analyze_image('')
    print(text)
    result = process_data(text)
    return result
  