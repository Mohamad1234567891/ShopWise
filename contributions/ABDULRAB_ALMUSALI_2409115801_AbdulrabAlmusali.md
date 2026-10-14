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

## 2. Product Data Handling and Ranking — `DataExtractor.py`

I implemented JSON-based product data management using `Assets/UserData.json`.

The implemented functionality includes:

- Loading and saving product records.
- Retrieving the product list.
- Adding products with automatically generated IDs.
- Updating permitted product fields.
- Deleting product records.
- Normalizing product text and review counts.
- Building a normalized product table.

I also implemented product evaluation functions to calculate the average category rating, an adjusted rating based on the product's rating and review count, a quality score, a price score, and a combined product score.

The `rank_products()` function filters invalid product records, calculates product scores, and sorts valid products in descending order of their scores.

These implementations support product data management and provide scoring and ranking functionality for comparing products within ShopWise.

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
  - `json`: Used to read and write product data stored in JSON format.
  - `pathlib`: Used to handle file paths, including the product data file path.
- **NLTK**
  - Used for text tokenization, English stop-word filtering, and VADER-based sentiment analysis in the initial sentiment-analysis implementation.

## 5. Key Contributions

My main contribution to ShopWise was implementing core components for product evaluation, data management, and ranking.

Specifically, I developed five alternative product-scoring algorithms, implemented product data handling and ranking functionality, and contributed the initial implementation of sentiment analysis.

Together, these contributions provide multiple approaches to product scoring, support the organization and evaluation of product data, and establish a basic foundation for sentiment-based text analysis.
