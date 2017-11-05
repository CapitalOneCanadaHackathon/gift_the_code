

# tweets = pd.read_json('the519_tweets.json')
# tweets.to_csv('the519_tweets.csv', index=False)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from os import path
from PIL import Image

from nltk.corpus import stopwords

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

from collections import Counter
import nltk
import re as regex

from time import time

tweets = pd.read_json('the519_tweets.json')
tweets['YYYYMM'] = tweets['timestamp'].map(lambda x: str(x.year) + '-' + str(x.month))

alice_coloring = np.array(Image.open("519.png"))


class TwitterData_Initialize():
    data = []
    processed_data = []
    wordlist = []

    data_model = None
    data_labels = None
    is_testing = False

    def initialize(self, json_file, is_testing_set=False, from_cached=None):
        if from_cached is not None:
            self.data_model = pd.read_json(from_cached)
            return

        self.is_testing = is_testing_set

        self.data = pd.read_json(json_file)
        self.processed_data = self.data
        self.wordlist = []
        self.data_model = None
        self.data_labels = None

class TwitterCleanuper:
    def iterate(self):
        for cleanup_method in [self.remove_urls,
                               self.remove_usernames,
                               self.remove_na,
                               self.remove_special_chars,
                               self.remove_numbers]:
            yield cleanup_method

    @staticmethod
    def remove_by_regex(tweets, regexp):
        tweets.loc[:, "text"].replace(regexp, "", inplace=True)
        return tweets

    def remove_urls(self, tweets):
        return TwitterCleanuper.remove_by_regex(tweets, regex.compile(r"http.?://[^\s]+[\s]?"))

    def remove_na(self, tweets):
        return tweets[tweets["text"] != "Not Available"]

    def remove_special_chars(self, tweets):  # it unrolls the hashtags to normal words
        for remove in map(lambda r: regex.compile(regex.escape(r)), [",", ":", "\"", "=", "&", ";", "%", "$",
                                                                     "@", "%", "^", "*", "(", ")", "{", "}",
                                                                     "[", "]", "|", "/", "\\", ">", "<", "-",
                                                                     "!", "?", ".", "'",
                                                                     "--", "---", "#"]):
            tweets.loc[:, "text"].replace(remove, "", inplace=True)
        return tweets

    def remove_usernames(self, tweets):
        return TwitterCleanuper.remove_by_regex(tweets, regex.compile(r"@[^\s]+[\s]?"))

    def remove_numbers(self, tweets):
        return TwitterCleanuper.remove_by_regex(tweets, regex.compile(r"\s?[0-9]+\.?[0-9]*"))

class TwitterData_Cleansing(TwitterData_Initialize):
    def __init__(self, previous):
        self.processed_data = previous.processed_data

    def cleanup(self, cleanuper):
        t = self.processed_data
        for cleanup_method in cleanuper.iterate():
            if not self.is_testing:
                t = cleanup_method(t)
            else:
                if cleanup_method.__name__ != "remove_na":
                    t = cleanup_method(t)

        self.processed_data = t

data = TwitterData_Initialize()
data.initialize('the519_tweets.json')
data = TwitterData_Cleansing(data)
data.cleanup(TwitterCleanuper())



word_string = ' '.join(data.processed_data['text'])


stopwords = set(STOPWORDS)
stopwords.add("RT")
stopwords.add("Im")
stopwords.add("pm")

# wordcloud = WordCloud().generate(word_string)

# Display the generated image:
# the matplotlib way:
import matplotlib.pyplot as plt

# lower max_font_size
wordcloud = WordCloud(font_path='Montserrat-Bold.ttf',random_state=42,max_font_size=40,relative_scaling=0.4,stopwords=stopwords, mask=alice_coloring,background_color="white").generate(word_string)
image_colors = ImageColorGenerator(alice_coloring)
plt.figure()
plt.imshow(wordcloud.recolor(color_func=image_colors), interpolation="bilinear")
plt.axis("off")
wordcloud.to_file("519_wordcloud.png")
plt.show()
