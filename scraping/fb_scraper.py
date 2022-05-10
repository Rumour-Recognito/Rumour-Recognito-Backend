from facebook_scraper import get_posts


def scrapePosts(link):
    post = next(get_posts(
        post_urls=[link], cookies="cookies.json", options={"comments": True, "reactions": True}))
    return post
