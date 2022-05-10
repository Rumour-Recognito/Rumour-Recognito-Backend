
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def sentimental_analysis(predictions_list, headlines_list, bodies_list):

    # Uncomment this line for the first time you run in your computer
    # nltk.download("vader_lexicon")
    csil = SentimentIntensityAnalyzer()

    discuss_list = []
    for i in range(len(predictions_list)):
        if(predictions_list[i] == "discuss"):
            curList = []
            curList.append(bodies_list[i])
            curList.append(headlines_list[i])
            discuss_list.append(curList)

    sum = 0
    for list in discuss_list:

        # print(list)

        body = list[0]
        heading = list[1]

        saBody = csil.polarity_scores(body)
        # print(saBody)
        body_compound = saBody['compound']

        saHeading = csil.polarity_scores(heading)
        # print(saHeading)
        heading_compound = saHeading['compound']

        if(body_compound == 0):
            sum += heading_compound
        elif(heading_compound == 0):
            sum += body_compound
        else:
            sum += body_compound * heading_compound

    return sum
