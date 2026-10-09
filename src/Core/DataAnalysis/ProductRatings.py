
def calculate_score_v1(
    rating, reviews_amount, bad_reviews_level,
    price, minimum_price, maximum_price
):
    """Weighted average with rating adjustment."""

    _validate_inputs(
        rating, reviews_amount, bad_reviews_level,
        price, minimum_price, maximum_price
    )

    price_score = _calculate_price_score(
        price, minimum_price, maximum_price
    )
    negative_score = (3 - bad_reviews_level) / 3 * 5
    reliability = reviews_amount / (reviews_amount + 50)

    adjusted_rating = (
        rating * reliability + 3 * (1 - reliability)
    )

    final_score = (
        adjusted_rating * 0.50
        + reliability * 5 * 0.20
        + negative_score * 0.20
        + price_score * 0.10
    )

    return round(final_score, 2)


def calculate_score_v2(
    rating, reviews_amount, bad_reviews_level,
    price, minimum_price, maximum_price
):
    """Weighted average using the original rating."""

    _validate_inputs(
        rating, reviews_amount, bad_reviews_level,
        price, minimum_price, maximum_price
    )

    price_score = _calculate_price_score(
        price, minimum_price, maximum_price
    )
    negative_score = (3 - bad_reviews_level) / 3 * 5
    reliability = reviews_amount / (reviews_amount + 50)

    final_score = (
        rating * 0.50
        + reliability * 5 * 0.20
        + negative_score * 0.20
        + price_score * 0.10
    )

    return round(final_score, 2)


def calculate_score_v3(
    rating, reviews_amount, bad_reviews_level,
    price, minimum_price, maximum_price
):
    """Weighted geometric mean."""

    _validate_inputs(
        rating, reviews_amount, bad_reviews_level,
        price, minimum_price, maximum_price
    )

    price_score = _calculate_price_score(
        price, minimum_price, maximum_price
    )

    # Keep the price factor above zero.
    price_score = 0.5 + (price_score / 5) * 4.5

    negative_score = (3 - bad_reviews_level) / 3 * 5
    reliability = reviews_amount / (reviews_amount + 50)

    adjusted_rating = (
        rating * reliability + 3 * (1 - reliability)
    )
    reliability_score = reliability * 5

    scores = [
        max(adjusted_rating, 0.5),
        max(reliability_score, 0.5),
        max(negative_score, 0.5),
        max(price_score, 0.5)
    ]
    weights = [0.50, 0.20, 0.20, 0.10]

    final_score = 1.0

    for score, weight in zip(scores, weights):
        final_score *= score ** weight

    return round(final_score, 2)


def calculate_score_v4(
    rating, reviews_amount, bad_reviews_level,
    price, minimum_price, maximum_price
):
    """Weighted harmonic mean."""

    _validate_inputs(
        rating, reviews_amount, bad_reviews_level,
        price, minimum_price, maximum_price
    )

    price_score = _calculate_price_score(
        price, minimum_price, maximum_price
    )

    # Keep the price factor above zero.
    price_score = 0.5 + (price_score / 5) * 4.5

    negative_score = (3 - bad_reviews_level) / 3 * 5
    reliability = reviews_amount / (reviews_amount + 50)

    adjusted_rating = (
        rating * reliability + 3 * (1 - reliability)
    )

    scores = [
        max(adjusted_rating, 0.5),
        max(reliability * 5, 0.5),
        max(negative_score, 0.5),
        max(price_score, 0.5)
    ]
    weights = [0.50, 0.20, 0.20, 0.10]

    denominator = sum(
        weight / score
        for weight, score in zip(weights, scores)
    )

    return round(1 / denominator, 2)


def calculate_score_v5(
    rating, reviews_amount, bad_reviews_level,
    price, minimum_price, maximum_price
):
    """Rating-based score with explicit penalties."""

    _validate_inputs(
        rating, reviews_amount, bad_reviews_level,
        price, minimum_price, maximum_price
    )

    price_score = _calculate_price_score(
        price, minimum_price, maximum_price
    )
    reliability = reviews_amount / (reviews_amount + 50)

    adjusted_rating = (
        rating * reliability + 3 * (1 - reliability)
    )

    negative_penalty = bad_reviews_level / 3 * 1.5
    low_review_penalty = (1 - reliability) * 0.5
    price_penalty = (5 - price_score) * 0.10

    final_score = (
        adjusted_rating
        + reliability * 0.5
        - negative_penalty
        - low_review_penalty
        - price_penalty
    )

    final_score = max(0, min(5, final_score))

    return round(final_score, 2)


def _validate_inputs(
    rating, reviews_amount, bad_reviews_level,
    price, minimum_price, maximum_price
):
    if not 0 <= rating <= 5:
        raise ValueError("Rating must be between 0 and 5.")

    if reviews_amount < 0:
        raise ValueError("Reviews amount cannot be negative.")

    if not 0 <= bad_reviews_level <= 3:
        raise ValueError(
            "Bad reviews level must be between 0 and 3."
        )

    if price <= 0 or minimum_price <= 0 or maximum_price <= 0:
        raise ValueError("Prices must be greater than zero.")

    if minimum_price > maximum_price:
        raise ValueError(
            "Minimum price cannot exceed maximum price."
        )

    if not minimum_price <= price <= maximum_price:
        raise ValueError(
            "Price must be within the comparison range."
        )


def _calculate_price_score(price, minimum_price, maximum_price):
    if minimum_price == maximum_price:
        return 5.0

    return (
        (maximum_price - price)
        / (maximum_price - minimum_price)
    ) * 5

"""
# Test data only.
algorithms = [
    ("Algorithm 1", calculate_score_v1),
    ("Algorithm 2", calculate_score_v2),
    ("Algorithm 3", calculate_score_v3),
    ("Algorithm 4", calculate_score_v4),
    ("Algorithm 5", calculate_score_v5)
]

test_cases = [
    {
        "name": "High rating, one review",
        "rating": 5.0,
        "reviews_amount": 1,
        "bad_reviews_level": 0,
        "price": 750,
        "minimum_price": 500,
        "maximum_price": 1000
    },
    {
        "name": "Same rating, 2000 reviews",
        "rating": 5.0,
        "reviews_amount": 2000,
        "bad_reviews_level": 0,
        "price": 750,
        "minimum_price": 500,
        "maximum_price": 1000
    },
    {
        "name": "Many negative reviews",
        "rating": 4.6,
        "reviews_amount": 2000,
        "bad_reviews_level": 3,
        "price": 750,
        "minimum_price": 500,
        "maximum_price": 1000
    },
    {
        "name": "Most expensive product",
        "rating": 4.6,
        "reviews_amount": 2000,
        "bad_reviews_level": 1,
        "price": 1000,
        "minimum_price": 500,
        "maximum_price": 1000
    }
]

for test_case in test_cases:
    print("\n" + test_case["name"])
    print("-" * 40)

    inputs = {
        key: value
        for key, value in test_case.items()
        if key != "name"
    }

    for algorithm_name, algorithm in algorithms:
        score = algorithm(**inputs)
        print(f"{algorithm_name}: {score:.2f}")
"""