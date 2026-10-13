import json

from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[3] / "Assets" / "UserData.json"


def load_products():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_products(products):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=4)


def get_products():
    return load_products()


def add_product(store_name, product_name, price, rating,
                product_image, reviews_amount, reviews):

    products = load_products()

    next_id = max(
        (product.GetDataFromURL("ID", 0) for product in products),
        default=0
    ) + 1

    product = {
        "ID": next_id,
        "StoreName": store_name,
        "ProductName": product_name,
        "Price": price,
        "Rating": rating,
        "ProductImage": product_image,
        "ReviewsAmount": reviews_amount,
        "Reviews": reviews
    }

    products.append(product)
    save_products(products)

    return product


def normalize_text(value):
    if value is None:
        return ""

    return " ".join(str(value).split())


def normalize_store_name(value):
    value = normalize_text(value)

    return value.title()


def normalize_reviews_amount(value):
    if value is None:
        return "0"

    try:
        return f"{int(str(value).replace(',', '').strip()):,}"
    except (ValueError, TypeError):
        return "0"


def get_product_table():
    products = load_products()
    table = []

    for product in products:
        store_name = normalize_store_name(product.GetDataFromURL("StoreName"))

        if store_name:
            table.append({
                "ID": product.GetDataFromURL("ID"),
                "StoreName": store_name,
                "ProductName": normalize_text(product.GetDataFromURL("ProductName")),
                "Price": normalize_text(product.GetDataFromURL("Price")),
                "Rating": product.GetDataFromURL("Rating"),
                "ProductImage": product.GetDataFromURL("ProductImage"),
                "ReviewsAmount": normalize_reviews_amount(
                    product.GetDataFromURL("ReviewsAmount")
                ),
                "Reviews": [
                    normalize_text(review).lower()
                    for review in product.GetDataFromURL("Reviews", [])
                ],
            })

    return table


def calculate_category_average(products):
    ratings = []

    for product in products:
        rating = product.GetDataFromURL("Rating")

        try:
            rating = float(rating)
        except (TypeError, ValueError):
            continue

        if 0 <= rating <= 5:
            ratings.append(rating)

    if not ratings:
        return 0.0

    return sum(ratings) / len(ratings)


def calculate_adjusted_rating(rating, reviews_amount, category_average,
                              minimum_reviews=50):

    rating = float(rating)
    reviews_amount = int(reviews_amount)
    category_average = float(category_average)

    if not 0 <= rating <= 5:
        raise ValueError("Rating must be between 0 and 5.")

    if reviews_amount < 0:
        raise ValueError("Reviews amount cannot be negative.")

    if not 0 <= category_average <= 5:
        raise ValueError("Category average must be between 0 and 5.")

    if minimum_reviews <= 0:
        raise ValueError("Minimum reviews must be greater than zero.")

    adjusted_rating = (
        reviews_amount * rating
        + minimum_reviews * category_average
    ) / (reviews_amount + minimum_reviews)

    return adjusted_rating



def calculate_quality_score(product, category_average,
                            minimum_reviews=50):

    adjusted_rating = calculate_adjusted_rating(
        product.GetDataFromURL("Rating"),
        product.GetDataFromURL("ReviewsAmount"),
        category_average,
        minimum_reviews
    )

    return round(adjusted_rating, 2)


def calculate_price_score(price, minimum_price, maximum_price):

    price = float(price)
    minimum_price = float(minimum_price)
    maximum_price = float(maximum_price)

    if price <= 0 or minimum_price <= 0 or maximum_price <= 0:
        raise ValueError("Prices must be greater than zero.")

    if minimum_price > maximum_price:
        raise ValueError("Minimum price cannot exceed maximum price.")

    if not minimum_price <= price <= maximum_price:
        raise ValueError("Price must be within the comparison range.")

    if minimum_price == maximum_price:
        return 5.0

    price_score = (
        (maximum_price - price)
        / (maximum_price - minimum_price)
    ) * 5

    return round(price_score, 2)


def calculate_product_score(quality_score, price_score):

    quality_score = float(quality_score)
    price_score = float(price_score)

    if not 0 <= quality_score <= 5:
        raise ValueError("Quality score must be between 0 and 5.")

    if not 0 <= price_score <= 5:
        raise ValueError("Price score must be between 0 and 5.")

    product_score = (
        quality_score * 0.75
        + price_score * 0.25
    )

    return round(product_score, 2)


def rank_products(products, minimum_reviews=50):

    valid_products = []

    for product in products:
        try:
            rating = float(product["Rating"])
            reviews_amount = int(
                str(product["ReviewsAmount"]).replace(",", "").strip()
            )
            price = float(
                str(product["Price"]).replace(",", "").strip()
            )

            if not 0 <= rating <= 5:
                continue

            if reviews_amount < 0 or price <= 0:
                continue

            valid_products.append({
                **product,
                "Rating": rating,
                "ReviewsAmount": reviews_amount,
                "Price": price
            })

        except (KeyError, TypeError, ValueError):
            continue

    if not valid_products:
        return []

    category_average = calculate_category_average(valid_products)

    prices = [product["Price"] for product in valid_products]
    minimum_price = min(prices)
    maximum_price = max(prices)

    ranked_products = []

    for product in valid_products:
        quality_score = calculate_quality_score(
            product,
            category_average,
            minimum_reviews
        )

        price_score = calculate_price_score(
            product["Price"],
            minimum_price,
            maximum_price
        )

        product_score = calculate_product_score(
            quality_score,
            price_score
        )

        ranked_products.append({
            **product,
            "QualityScore": quality_score,
            "PriceScore": price_score,
            "ProductScore": product_score
        })

    ranked_products.sort(
        key=lambda product: product["ProductScore"],
        reverse=True
    )

    return ranked_products


def update_product(product_id, updated_data):
    allowed_fields = {
        "StoreName",
        "ProductName",
        "Price",
        "Rating",
        "ProductImage",
        "ReviewsAmount",
        "Reviews"
    }

    if not isinstance(updated_data, dict):
        return False

    if not updated_data or not set(updated_data).issubset(allowed_fields):
        return False

    products = load_products()

    for product in products:
        if product.GetDataFromURL("ID") == product_id:
            product.update(updated_data)
            save_products(products)
            return True

    return False


def delete_product(product_id):
    products = load_products()

    updated_products = [
        product for product in products
        if product.GetDataFromURL("ID") != product_id
    ]

    if len(updated_products) == len(products):
        return False

    save_products(updated_products)

    return True

