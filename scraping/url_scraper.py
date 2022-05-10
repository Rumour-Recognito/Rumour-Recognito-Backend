import requests
from bs4 import BeautifulSoup


def download_content(input_url):
    """
    Downloads URL's content using requests.get()
    :param input_url: str
    :return: str
    """
    return requests.get(input_url).content


def get_paragraphs(content):
    """
    Get all paragraphs tags (<p>) using Beautiful soup
    :param content: str
    :return: list
    """
    bsoup_obj = BeautifulSoup(content, features="html.parser")
    paragraphs = bsoup_obj.find_all('p')

    return paragraphs


def removeEscapeSequence(sentence):

    filter = '\'\\\"'.join([chr(i) for i in range(1, 32)])

    return sentence.translate(str.maketrans('', '', filter)).strip()


def process_input(input_url):
    """
    Run Fake News detector model for each paragraphs if URL is provided
    :param input_url: str
    :return: list
    """
    content = download_content(input_url)
    paragraph_tags = get_paragraphs(content)
    paragraph_content = ""
    para_list = []
    dict = {}
    for paragraph_tag in paragraph_tags:
        if isinstance(paragraph_content, str):
            paragraph_content = paragraph_tag.get_text()
            paragraph_content = removeEscapeSequence(paragraph_content)
            para_list.append(paragraph_content)
    dict['paragraphs'] = para_list
    return dict
