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
        (product.get("ID", 0) for product in products),
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
        store_name = normalize_store_name(product.get("StoreName"))

        if store_name:
            table.append({
                "ID": product.get("ID"),
                "StoreName": store_name,
                "ProductName": normalize_text(product.get("ProductName")),
                "Price": normalize_text(product.get("Price")),
                "Rating": product.get("Rating"),
                "ProductImage": product.get("ProductImage"),
                "ReviewsAmount": normalize_reviews_amount(
                    product.get("ReviewsAmount")
                ),
                "Reviews": [
                    normalize_text(review).lower()
                    for review in product.get("Reviews", [])
                ],
            })

    return table


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
        if product.get("ID") == product_id:
            product.update(updated_data)
            save_products(products)
            return True

    return False


def delete_product(product_id):
    products = load_products()

    updated_products = [
        product for product in products
        if product.get("ID") != product_id
    ]

    if len(updated_products) == len(products):
        return False

    save_products(updated_products)

    return True