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

myclient = pymongo.MongoClient(
    "mongodb+srv://squadra:1234@cluster0.wiuug.mongodb.net/?retryWrites=true&w=majority")
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

# resets the status to -1
@app.route('/reset-status')
def resetStatus():
    mycol.update_many({}, [{'$set': {'status': -1}}])
    data = mycol.find_one()
    return str(data['status'])

### Individual tweet details (without comments)  ###
@app.route('/tweet-scrape', methods=['POST'])
def scrape_twitter():
    mycol.update_many({}, [{'$set': {'status': 0}}])
    data = request.get_json()
    id = tweet_id_extract(data['link'])
    print(id)
    tweet = getTweet(id)
    print(tweet)
    tweetText = tweet['text']
    print("Before image: " + tweetText)
    if tweet['media']:
        print("Image analysis: ")
        print(analyze_image(tweet['media'][0]['image_url']))
        tweetText = tweetText + " " + analyze_image(tweet['media'][0]['image_url'])
    print("After image: " + tweetText)
    result = process_data(tweetText)
    return result

# Scrapes tweet comments
@app.route('/tweet-comments-scrape')
def scrape_twitter_comments():
    id = request.args.get('id')
    comments = getTweetComments(id)
    return jsonify(comments)

# Scrape Facebook posts
@app.route('/facebook-scrape', methods=['POST'])
def scrape_facebook():
    mycol.update_many({}, [{'$set': {'status': 0}}])
    data = request.get_json()
    id = fb_id_extract(data['link'])
    print(id)
    post = scrapePosts(id)
    print(post)
    postText = post['post_text']
    if(post['image'] != None):
        print("Image analysis: ")
        print(analyze_image(post['image']))
        postText = postText + " " + analyze_image(post['image'])
    print(postText)
    result = process_data(postText)

    return result

# Scrape plain URL
@app.route('/url-scrape', methods=['POST'])
def predict():
    if request.method == 'POST':
        data = request.get_json()
        content = process_input(data['link'])
        return content
    else:
        return "Something went wrong"

# Plain text checking
@app.route('/plain-text')
def analyze_text():

    mycol.update_many({}, [{'$set': {'status': 0}}])

    text = request.args.get('text')

    print(text)

    result = process_data(text)

    return result

# Analyze Image OCR
@app.route('/analyze-image', methods=['POST'])
def analyze():
    mycol.update_many({}, [{'$set': {'status': 0}}])
    file = request.files['file']
    file.save(os.path.join(base_dir, "image.jpg"))
    text = analyze_image('')
    print(text)
    result = process_data(text)
    return result
