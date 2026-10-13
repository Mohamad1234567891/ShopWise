import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

# Download the NLTK resources used by this file.
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("vader_lexicon", quiet=True)


def process_text(text):
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


# New feature: classify product reviews by negative severity.
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


if __name__ == "__main__":
    review_text = input("Enter a product review: ")

    try:
        important_words = process_text(review_text)
        original_result = analyze_sentiment(review_text)
        severity = evaluate_review(review_text)

        labels = {
            0: "Positive",
            1: "Neutral",
            2: "Mildly negative",
            3: "Severely negative",
        }

        print("Original text:", review_text)
        print("Important words:", important_words)
        print("Original analyze_sentiment result:", original_result)
        print("Severity:", labels[severity])
        print("Severity score:", severity)
    except ValueError as error:
        print(error)