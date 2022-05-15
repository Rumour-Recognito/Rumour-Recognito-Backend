
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def sentimental_analysis_for_discuss(predictions_list, headlines_list, bodies_list):

    # Uncomment this line for the first time you run in your computer
    # nltk.download("vader_lexicon")
    csil = SentimentIntensityAnalyzer()

    discuss_list = []
    agree_list = []
    disagree_list = []
    for i in range(len(predictions_list)):
        if(predictions_list[i] == "discuss"):
            curList = []
            curList.append(bodies_list[i])
            curList.append(headlines_list[i])
            discuss_list.append(curList)
        elif(predictions_list[i] == 'agree'):
            curList = []
            curList.append(bodies_list[i])
            curList.append(headlines_list[i])
            agree_list.append(curList)
        elif(predictions_list[i] == 'disagree'):
            curList = []
            curList.append(bodies_list[i])
            curList.append(headlines_list[i])
            disagree_list.append(curList)

    sum = 0
    for list in discuss_list:

        body = list[0]
        heading = list[1]

        saBody = csil.polarity_scores(body)
        body_compound = saBody['compound']

        saHeading = csil.polarity_scores(heading)
        heading_compound = saHeading['compound']

        if(body_compound == 0):
            sum += heading_compound
        elif(heading_compound == 0):
            sum += body_compound
        else:
            sum += body_compound * heading_compound

    for list in agree_list:

        body = list[0]
        heading = list[1]

        saBody = csil.polarity_scores(body)
        body_compound = saBody['compound']

        saHeading = csil.polarity_scores(heading)
        heading_compound = saHeading['compound']

        if(body_compound * heading_compound > 0):
            sum += 1

    for list in disagree_list:

        body = list[0]
        heading = list[1]

        saBody = csil.polarity_scores(body)
        body_compound = saBody['compound']

        saHeading = csil.polarity_scores(heading)
        heading_compound = saHeading['compound']

        if(body_compound * heading_compound > 0):
            sum -= 1

    return sum
