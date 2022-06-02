from translate_text import *
import csv
import pymongo
import re
from search_google import *
from sentimental_analysis import *
from scraping.url_scraper import *
from pred import *

myclient = pymongo.MongoClient(
    "mongodb+srv://squadra:1234@cluster0.wiuug.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["rumor_recognito_db"]
mycol = mydb["progress"]

# Preprocess sentences and translate


def process_data(text):
    sentences = text.split('\n')

    mycol.update_many({}, [{'$set': {'status': 1}}])

    link_removed_sentences = []
    for sentence in sentences:
        filteredText = removeLinksAndGetSentences(sentence)
        link_removed_sentences.append(filteredText)

    special_char_removed_sentences = []
    for sentence in link_removed_sentences:
        filteredText = filterTextFromSpecialCharacters(sentence)
        special_char_removed_sentences.append(filteredText)

    filtered_sentences = removeEmptySentence(special_char_removed_sentences)

    mycol.update_many({}, [{'$set': {'status': 2}}])

    translated_sentences = []

    for sentence in filtered_sentences:
        sentence = translate_to_english(sentence)
        translated_sentences.append(sentence)

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

# Search news from Google


def getSimilarNews(sentences):

    mycol.update_many({}, [{'$set': {'status': 3}}])

    counter = 1
    bodies = []
    headings = []

    for sentence in sentences:
        allContent = google_search_content(sentence, 5)

        for content in allContent:
            if(content):
                bodies.append([counter, content])
                headings.append([sentence, counter])
                counter += 1

    result = stance_detect(headings, bodies)
    return result


def google_search_content(query, limit):
    results = search_google(query, limit)
    allContents = []

    for link in results['results']:
        content = process_input(link)
        allContents.extend(content['paragraphs'])

    return allContents

# Execute model


def stance_detect(headlines_list, bodies_list):
    mycol.update_many({}, [{'$set': {'status': 4}}])

    predictions = load(headlines_list, bodies_list)

    headlines = []
    bodies = []
    for item in headlines_list:
        headlines.append(item[0])

    for item in bodies_list:
        bodies.append(item[1])

    score = sentimental_analysis_for_discuss(predictions, headlines, bodies)

    mycol.update_many({}, [{'$set': {'status': 5}}])

    print(score)

    if(score > 0):
        return "LOOKS REAL"
    elif(score < 0):
        return "LOOKS FAKE"
    else:
        return "UNPREDICTABLE"

# Extract id from fb url


def fb_id_extract(url):
    id = re.findall(
        r'(?:(?:http|https):\/\/(?:www|m|mbasic|business)\.(?:facebook|fb)\.com\/)(?:photo(?:\.php|s)|permalink\.php|video\.php|media|watch\/|questions|notes|[^\/]+\/(?:activity|posts|videos|photos))[\/?](?:fbid=|story_fbid=|id=|b=|v=|)([0-9]+|[^\/]+\/[\d]+)', url)
    return id[0]

# Extract id from twitter url


def tweet_id_extract(url):
    id = re.findall(r'twitter\.com\/.*\/status(?:es)?\/([^\/\?]+)', url)
    return id[0]
