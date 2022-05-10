from googlesearch import search


def search_google(query, limit):
    lim = int(limit)
    results = []
    search_results = {}
    for i in search(query,      # The query you want to run
                    tld='com',  # The top level domain
                    lang='en',  # The language
                    num=10,     # Number of results per page
                    start=0,    # First result to retrieve
                    stop=lim,  # Last result to retrieve
                    pause=2.0,  # Lapse between HTTP requests
                    ):
        results.append(i)
    search_results['results'] = results
    return search_results
