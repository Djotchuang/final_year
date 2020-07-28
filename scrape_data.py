import nltk
from newspaper import Article

# nltk.download()

# url = 'https://www.bbc.com/news/world-africa-45723211'


def scrape_text(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()

    title = article.title
    text = article.text

    total = [title + text]

    return total
