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
from image_process import *


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
    id = request.args.get('id')
    post = scrapePosts(id)
    print(post)
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


def process_data(text):
    sentences = text.split('\n')

    link_removed_sentences = []
    for sentence in sentences:
        filteredText = removeLinksAndGetSentences(sentence)
        link_removed_sentences.append(filteredText)

    special_char_removed_sentences = []
    for sentence in link_removed_sentences:
        filteredText = filterTextFromSpecialCharacters(sentence)
        special_char_removed_sentences.append(filteredText)

    
    filtered_sentences = removeEmptySentence(special_char_removed_sentences)

    global status
    status = 0

    translated_sentences = []

    for sentence in filtered_sentences:
        sentence = translate_to_english(sentence)
        translated_sentences.append(sentence)
    
    status = 1
    result = getSimilarNews(translated_sentences)
    return result

# function to remove links from sentences
def removeLinksAndGetSentences(text):
    wordsInText = text.split(' ')
    filteredWord = []

    for word in wordsInText:
        if ('http' not in word and 'www' not in word):
            filteredWord.append(word)

    return ' '.join(filteredWord)

# function to filterTextFromSpecialCharacters
def filterTextFromSpecialCharacters(text):
    text = text.strip()
    filteredText = []
    specialChars = '/*!@#$%^&*()"{}_[]|\\?/<>,.'

    for letter in text:
        if(letter in specialChars):
            filteredText.append(' ')
        else:
            filteredText.append(letter)

    return ''.join(filteredText).strip()


# remove empty space
def removeEmptySentence(sentences):
    nonEmptySentences = []
    for sentence in sentences:
        if sentence != '':
            nonEmptySentences.append(sentence)

    return nonEmptySentences

def getSimilarNews(sentences):
    counter = 1
    bodies = []
    bodiesColumnTitles = ['Body ID', 'articleBody']
    headings = []
    headingsColumnTitles = ['Headline', 'Body ID']

    bodiesContent = []
    headlinesContent = []
    for sentence in sentences:
        allContent = google_search_content(sentence, 5)

        for content in allContent:
            if(content):
                bodiesContent.append(content)
                headlinesContent.append(sentence)
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

    global status
    status = 2
    result = stance_detect(bodiesContent, headlinesContent)
    return result

def google_search_content(query, limit):

    results = search_google(query, limit)
    allContents = []

    for link in results['results']:
        content = process_input(link)
        allContents.extend(content['paragraphs'])

    return allContents

def stance_detect(bodies, headlines):
    load()
    predictions = []
    with open('./result/predictions_test.csv', newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        for each in data:
            predictions.extend(each)
        predictions.remove("Prediction")

    score = sentimental_analysis(predictions, headlines, bodies)

    for prediction in predictions:
        if(prediction == 'agree'):
            score += 1
        elif(prediction == 'disagree'):
            score -= 1

    print(score)
    
    global status
    status = 3

    if(score > 0):
        return "LOOKS REAL"
    elif(score < 0):
        return "LOOKS FAKE"
    else:
        return "UNPREDICTABLE"