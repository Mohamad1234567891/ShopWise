import json

with open(r"..\..\..\Assets\FakeData.Json", "r", encoding = "utf-8") as file:
    data = file.read()

products = json.loads("[" + data.strip().rstrip(",") + "]")

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

table = []
next_id = 1

for product in products:

    store_name = normalize_store_name(product.get("StoreName"))

    if store_name:
        table.append({
            "ID": next_id,
            "StoreName": (product["StoreName"]),
            "ProductName": normalize_store_name(normalize_text(product.get("ProductName"))),
            "Price": normalize_text(product.get("Price")),
            "Rating": product.get("Rating"),
            "ProductImage": product.get("ProductImage"),
            "ReviewsAmount": normalize_reviews_amount(product.get("ReviewsAmount")),
            "Reviews": [normalize_text(review).lower() for review in product.get("Reviews", [])],
        })

        next_id += 1

for product in table:
    print(product)