import numpy as np
import pandas as pd
import os
import re
import contractions
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


def get_all_query(title, text):
    total = [title + text]
    return total


def remove_punctuation_stopwords_lemma(sentence):
    filter_sentence = ''
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')

    sentence = contractions.fix(sentence) # fix english contractions
    sentence = re.sub(r'[^\w\s]', ' ', sentence)
    sentence = re.sub(r"(\b|\s+\-?|^\-?)(\d+|\d*\.\d+)\b","", sentence) # Remove numbers
    sentence = ''.join(c for c in sentence if not c.isdigit())
    sentence = re.sub(r'\s+', ' ', sentence, flags=re.I) # Replace multiple space with single space

    words = nltk.word_tokenize(sentence)  # tokenization
    words = [w.lower() for w in words if not w in stop_words]  # remove stopwords

    # lemmatization
    for word in words:
        filter_sentence = filter_sentence + ' ' + \
            str(lemmatizer.lemmatize(word)).lower()
    return filter_sentence
