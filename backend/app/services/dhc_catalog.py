"""DHC product catalog loading and matching utilities."""

import json
from functools import lru_cache
from pathlib import Path

from app.schemas import DHCProduct


CATALOG_PATH = Path(__file__).resolve().parents[3] / "data" / "dhc_products.json"


@lru_cache
def load_dhc_products() -> list[DHCProduct]:
    """Load DHC product records from the project JSON database."""

    product_data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    return [DHCProduct(**item) for item in product_data]


def get_product_by_id(product_id: str) -> DHCProduct | None:
    """Return one DHC product by id."""

    return next((product for product in load_dhc_products() if product.id == product_id), None)


def search_products_by_nutrient_or_function(keywords: list[str]) -> list[DHCProduct]:
    """Find DHC products whose nutrients or functions match the supplied keywords."""

    normalized_keywords = {keyword.lower() for keyword in keywords}
    matches: list[DHCProduct] = []

    for product in load_dhc_products():
        searchable_terms = {
            *[nutrient.lower() for nutrient in product.nutrients],
            *[function.lower() for function in product.functions],
            product.name.lower(),
            product.category.lower(),
        }
        if searchable_terms & normalized_keywords:
            matches.append(product)

    return matches
