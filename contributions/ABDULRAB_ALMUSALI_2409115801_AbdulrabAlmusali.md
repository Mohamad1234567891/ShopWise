# Contribution Report — Abdulrab Almusali

**Student Name:** ABDULRAB ALMUSALI  
**Student ID:** 2409115801  
**GitHub Username:** AbdulrabAlmusali  
**Project:** ShopWise

## 1. Product Rating Algorithms — `ProductRatings.py`

I implemented five alternative product-scoring algorithms to evaluate and compare products using their ratings, review counts, negative-review levels, and prices.

The implemented algorithms are:

- **Version 1 — Reliability-Adjusted Weighted Average:** Calculates a weighted-average score using an adjusted product rating that accounts for the reliability of the review count.
- **Version 2 — Original-Rating Weighted Average:** Calculates a weighted-average score using the original product rating rather than the adjusted rating.
- **Version 3 — Weighted Geometric Mean:** Combines the scoring factors using a weighted geometric mean.
- **Version 4 — Weighted Harmonic Mean:** Combines the scoring factors using a weighted harmonic mean.
- **Version 5 — Penalty-Based Rating Score:** Calculates a rating-based score with explicit penalties for negative reviews, low review counts, and price.

In addition to the scoring algorithms, I implemented shared input validation through `_validate_inputs()` and price scoring through `_calculate_price_score()`.

The validation function checks rating and price ranges, review counts, and negative-review levels. The file also contains commented test data and test cases intended to compare the algorithms under different product conditions.

Each algorithm uses a different scoring strategy, allowing the resulting product scores to be compared under different review counts, negative-review levels, and price conditions.

## 2. Review Translation — `Translator.py`

I worked on a translation utility for product reviews collected from different online stores. The goal is to convert reviews written in different languages into English so they can be processed more consistently by the ShopWise application.

The implementation uses Argos Translate for local translation and `langdetect` to identify the language of each review. It checks which translation language models are installed, reuses translation objects, and leaves reviews unchanged when they are already in English or cannot be translated.

I also included test code in the same file to check the translation process with sample reviews in different languages and measure the processing time for a larger list of reviews.

The translation utility depends on the availability of suitable language models. Its speed and translation quality need to be evaluated using actual product reviews.

## 3. Initial Text Preprocessing and Sentiment Analysis Implementation — `SentimentAnalysis.py`

My contribution to this file was the initial implementation of text preprocessing and sentiment analysis using NLTK and its VADER sentiment analyzer.

The implementation converts the input text to lowercase, tokenizes it into words, and filters out common English stop words when preparing the list of important words. It also uses VADER's compound sentiment score to classify the original input text as positive, negative, or neutral.

The function returns:

- `True` for positive sentiment.
- `False` for negative sentiment.
- `None` for neutral sentiment.

This description covers only the initial implementation represented by my code.

## 4. Libraries Used

The implementations described in this report use the following libraries:

- **Python standard library**
  - `json` and `pathlib`: Used for JSON data handling and file paths in the product-data implementation, if those functions remain part of my contribution.
  - `time`: Used to measure translation processing time.
- **NLTK**
  - Used for text tokenization, English stop-word filtering, and VADER-based sentiment analysis in the initial sentiment-analysis implementation.
- **Argos Translate**
  - Used for local translation of product reviews into English.
- **langdetect**
  - Used to detect the language of each review.

## 5. Key Contributions

My contributions to ShopWise include implementing five alternative product-scoring algorithms, contributing the initial sentiment-analysis implementation, and working on a translation utility for product reviews. I also contributed product-data handling and ranking functionality when working on `DataExtractor.py`.

These components address product evaluation, data processing, sentiment analysis, and review translation within the project.
