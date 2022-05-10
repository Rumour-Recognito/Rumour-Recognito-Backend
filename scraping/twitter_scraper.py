from pytwitterscraper import TwitterScraper

tw = TwitterScraper()


def getTweet(id):
    tweets = tw.get_tweetinfo(id)
    post = tweets.contents
    return post


def getTweetComments(id):
    twcomments = tw.get_tweetcomments(id)
    comments = twcomments.contents
    return comments