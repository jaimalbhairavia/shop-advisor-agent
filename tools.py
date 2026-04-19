import json
import os
from langchain_core.tools import tool

_base = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_base, "data/products.json")) as f:
    _products = json.load(f)

with open(os.path.join(_base, "data/price.json")) as f:
    _prices = json.load(f)

with open(os.path.join(_base, "data/safety_rules.json")) as f:
    _safety_rules = json.load(f)

_products_by_id = {p["id"]: p for p in _products}


@tool
def product_search_tool(query: str) -> list:
    """Search the product catalog for items matching the query. Returns a list of matching products with full details."""
    query_words = query.lower().split()
    results = []
    seen = set()

    for product in _products:
        searchable = (
            product["name"].lower()
            + " "
            + product["category"].lower()
            + " "
            + " ".join(product.get("features", []))
        )
        if any(word in searchable for word in query_words):
            if product["id"] not in seen:
                results.append(product)
                seen.add(product["id"])

    return results


@tool
def safety_check(product_ids: list) -> dict:
    """Apply safety rules to a list of product IDs. Returns products grouped into safe, flagged, and blocked."""
    blocked_categories = set(_safety_rules["blocked_categories"])
    flagged_categories = set(_safety_rules["flagged_categories"])
    banned_brands = set(_safety_rules["banned_brands"])
    min_rating = _safety_rules["min_rating_threshold"]

    safe, flagged, blocked = [], [], []

    for pid in product_ids:
        product = _products_by_id.get(pid)
        if not product:
            continue
        if product["category"] in blocked_categories or product["brand"] in banned_brands:
            blocked.append({"id": pid, "reason": "blocked category or banned brand"})
        elif product["rating"] < min_rating:
            blocked.append({"id": pid, "reason": f"rating {product['rating']} is below minimum threshold of {min_rating}"})
        elif product["category"] in flagged_categories:
            flagged.append({"id": pid, "reason": "flagged category requires review", "product": product})
        else:
            safe.append(product)

    return {"safe": safe, "flagged": flagged, "blocked": blocked}


@tool
def price_compare(product_ids: list) -> list:
    """Compare prices across vendors for a list of product IDs. Returns best price and all vendor options per product, sorted cheapest first."""
    results = []

    for pid in product_ids:
        product = _products_by_id.get(pid)
        if not product:
            continue
        vendor_data = _prices.get(pid)
        if vendor_data:
            vendor_prices = vendor_data["prices"]
            best = min(vendor_prices, key=lambda x: x["price"])
        else:
            vendor_prices = [{"vendor": "catalog price", "price": product["price"]}]
            best = vendor_prices[0]

        results.append({
            "id": pid,
            "name": product["name"],
            "best_price": best["price"],
            "best_vendor": best["vendor"],
            "all_prices": vendor_prices,
        })

    return sorted(results, key=lambda x: x["best_price"])
