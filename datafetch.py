from bs4 import BeautifulSoup
from requests_html import HTMLSession
import requests

NUM_TOP_ARTICLES = 5
BASE_URL = "https://cn.nytimes.com/world/"

def get_top_article_links(num_top_articles): 
    # create an HTML Session object
    session = HTMLSession()
    
    # Use the object above to connect to needed webpage
    resp = session.get(BASE_URL)
 
    # Run JavaScript code on webpage. Needed so that mostViewedWeek div is populated.
    resp.html.render()

    soup = BeautifulSoup(resp.html.html, 'html.parser')
    found = soup.find(id="tabC_mostViewedWeek").find_all("a")

    items = []

    num_iterations = min(num_top_articles, len(found))
    for i in range(num_iterations):
        items.append(found[i]["href"])

    return items

def get_article_text(link):
    session = requests.Session()
    resp = session.get(link)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    found = soup.find_all("div", class_="article-paragraph")

    text = ""
    for item in found:
        text += item.text
    return text

def get_concatenated_text():
    top_article_links = get_top_article_links(NUM_TOP_ARTICLES)
    all_text = ""
    for link in top_article_links:
        all_text += get_article_text(link)
        all_text += "\n"
    
    return all_text

if __name__ == "__main__":
    print(get_concatenated_text())