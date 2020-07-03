import nltk
from newspaper import Article

# nltk.download()

# url = 'https://www.bbc.com/news/world-africa-45723211'


def scrape_text(url):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()

    authors = article.authors
    news_authors = ''

    for author in authors:
        news_authors += author

    title = article.title
    text = article.text

    total = [news_authors + title + text]

    return total
