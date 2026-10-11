import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download("punkt_tab")
nltk.download("stopwords")
nltk.download("vader_lexicon")


def process_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words("english"))

    important_words = [
        word for word in tokens
        if word.isalpha() and word not in stop_words
    ]

    return important_words


def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    compound_score = scores["compound"]

    if compound_score >= 0.05:
        return True
    elif compound_score <= -0.05:
        return False
    else:
        return None


text = input("Enter a sentence: ")

important_words = process_text(text)
sentiment = analyze_sentiment(text)

print("Original text:", text)
print("Important words:", important_words)

if sentiment is True:
    print("Sentiment: Positive")
    print("Result:", True)
elif sentiment is False:
    print("Sentiment: Negative")
    print("Result:", False)
else:
    print("Sentiment: Neutral")
    print("Result: None")
