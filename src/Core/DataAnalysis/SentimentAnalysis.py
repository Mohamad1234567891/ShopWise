"""
This file is part of ShopWise, an open-source multi-region, multi-store
price-comparison and product-search engine.

Copyright (c) 2026 Muhammed Bekiroğlu and the ShopWise contributors.

Original ShopWise repository: https://github.com/Mohamad1234567891/ShopWise

Muhammed Bekiroğlu (ShopWise team leader and top contributor) YouTube channel:
    https://www.youtube.com/@ALShajaraComputerScienceInstit

Licensed under the Mozilla Public License 2.0 with Additional Attribution
Terms — see the LICENSE file.
-------------------------------------------------------------------------------------------------------------------------------

Review sentiment scoring. Preprocesses review text with NLTK (lowercase, tokenize, stopwords) and classifies each review with VADER plus ShopWise's severity phrase lists into: positive (0), neutral (1), mildly negative (2) or severely negative (3). The severity feeds the value scoring in StatisticalAnalysis.
"""

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

# Download the NLTK resources used by this file.
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("vader_lexicon", quiet=True)


def ProcessText(text):
    """Original preprocessing function: lowercase, tokenize, and remove stopwords."""
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words("english"))

    important_words = [
        word for word in tokens
        if word.isalpha() and word not in stop_words
    ]

    return important_words


def analyze_sentiment(text):
    """
    Original sentiment function, kept unchanged in behavior for compatibility.

    Returns:
        True  = Positive
        False = Negative
        None  = Neutral
    """
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)["compound"]

    if score >= 0.05:
        return True
    elif score <= -0.05:
        return False
    else:
        return None


SEVERE_NEGATIVE_PHRASES = (
    "broken", "doesn't work", "does not work", "not working",
    "stopped working", "unusable", "defective", "damaged",
    "arrived damaged", "arrived broken", "completely useless",
    "fell apart", "dangerous", "unsafe", "missing parts",
    "won't turn on", "will not turn on", "dead on arrival",
    "not the same product", "wasn't the same product", "isn't the same product"
    "isn't the same", "wasn't the same", "was not the same product", "was not the same",
    "is not the same"
)

MILD_NEGATIVE_PHRASES = (
    "didn't like", "did not like", "not impressed",
    "not what i expected", "disappointed", "could be better",
    "poor quality", "not great", "not good",
)

SEVERE_NEGATION_EXCEPTIONS = (
    "not broken", "isn't broken", "is not broken",
    "not damaged", "isn't damaged", "is not damaged",
    "not defective", "doesn't seem broken",
)


def evaluate_review(text):
    """
    Return the ShopWise product-review severity score.

    0 = Positive
    1 = Neutral
    2 = Mildly negative
    3 = Severely negative
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Please enter a non-empty review.")

    review = " ".join(text.lower().split())
    analyzer = SentimentIntensityAnalyzer()
    compound_score = analyzer.polarity_scores(text)["compound"]

    # Avoid treating common explicit negations as severe failures.
    has_severe_negation = any(
        phrase in review for phrase in SEVERE_NEGATION_EXCEPTIONS
    )
    if not has_severe_negation and any(
        phrase in review for phrase in SEVERE_NEGATIVE_PHRASES
    ):
        return 3

    if any(phrase in review for phrase in MILD_NEGATIVE_PHRASES):
        return 2

    if compound_score >= 0.05:
        return 0
    elif compound_score <= -0.05:
        return 2
    else:
        return 1