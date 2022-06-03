from flask import Flask, request, jsonify
from bson.objectid import ObjectId
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

### Check if server is running successfully ###


@app.route('/')
def hello_world():
    return 'Rumour-Reckon Backend running!'

# Return Job ID for client


@app.route('/getId')
def getJobId():
    job = {"status": -1, "type": -1, "news_text": "",
           "similar_news": [], "result": ""}
    x = mycol.insert_one(job)
    return str(x.inserted_id)

# Delete Job details


@app.route('/deleteId')
def deleteJob():
    jobId = request.args.get('jobId')
    obj = {"_id": ObjectId(jobId)}
    x = mycol.delete_one(obj)
    return "Deleted successfully!"


# Provides the current status of the analysis
@app.route('/status')
def getStatus():
    jobId = request.args.get('jobId')
    data = mycol.find_one({"_id": ObjectId(jobId)})
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
    data = request.get_json()
    mycol.update_one({'_id': ObjectId(data['jobId'])}, {"$set": {"status": 0}}, upsert=False)
    mycol.update_one({'_id': ObjectId(data['jobId'])}, {"$set": {"type": 1}}, upsert=False)
    id = tweet_id_extract(data['link'])
    print(id)
    tweet = getTweet(id)
    print(tweet)
    tweetText = tweet['text']
    print("Before image: " + tweetText)
    if tweet['media']:
        print("Image analysis: ")
        print(analyze_image(tweet['media'][0]['image_url'], 'url'))
        tweetText = tweetText + " " + \
            analyze_image(tweet['media'][0]['image_url'], 'url')
    print("After image: " + tweetText)
    mycol.update_one({'_id': ObjectId(data['jobId'])}, {"$set": {"news_text": tweetText}}, upsert=False)
    result = process_data(tweetText, data['jobId'])
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
    data = request.get_json()
    mycol.update_one({'_id': ObjectId(data['jobId'])}, {"$set": {"status": 0}}, upsert=False)
    mycol.update_one({'_id': ObjectId(data['jobId'])}, {"$set": {"type": 0}}, upsert=False)
    id = fb_id_extract(data['link'])
    print(id)
    post = scrapePosts(id)
    print(post)
    postText = post['post_text']
    if(post['image'] != None):
        print("Image analysis: ")
        print(analyze_image(post['image'], 'url'))
        postText = postText + " " + analyze_image(post['image'], 'url')
    print(postText)
    mycol.update_one({'_id': ObjectId(data['jobId'])}, {"$set": {"news_text": postText}}, upsert=False)
    result = process_data(postText, data['jobId'])

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
    text = request.args.get('text')
    jobId = request.args.get('jobId')
    mycol.update_one({'_id': ObjectId(jobId)}, {"$set": {"status": 0}}, upsert=False)
    mycol.update_one({'_id': ObjectId(jobId)}, {"$set": {"type": 2}}, upsert=False)
    mycol.update_one({'_id': ObjectId(jobId)}, {"$set": {"news_text": text}}, upsert=False)
    print(text)

    result = process_data(text, jobId)

    return result

# Analyze Image OCR


@app.route('/analyze-image', methods=['POST'])
def analyze():
    jobId = request.args.get('jobId')
    mycol.update_one({'_id': ObjectId(jobId)}, {"$set": {"status": 0}}, upsert=False)
    mycol.update_one({'_id': ObjectId(jobId)}, {"$set": {"type": 3}}, upsert=False)
    file = request.files['file']
    file.save(os.path.join(base_dir, "image.jpg"))
    text = analyze_image(file, 'file')
    print(text)
    mycol.update_one({'_id': ObjectId(jobId)}, {"$set": {"news_text": text}}, upsert=False)
    result = process_data(text, jobId)
    return result
