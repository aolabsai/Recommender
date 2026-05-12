from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


CATEGORIES = [
    "electronics",
    "home",
    "outdoor",
    "apparel",
    "wellness",
    "office",
]
PRICE_TIERS = ["budget", "midrange", "premium"]
USE_CASES = ["daily", "gift", "travel", "work"]


@dataclass(frozen=True)
class Product:
    name: str
    category: str
    price_tier: str
    sustainable: bool
    brand_style: str
    shipping_speed: str
    use_case: str
    shopper_intent: str
    description: str


@dataclass(frozen=True)
class ShopperContext:
    category: str = "electronics"
    max_price_tier: str = "premium"
    prefers_sustainable: bool = False
    use_case: str = "daily"
    style: str = "minimal"
    shipping_speed: str = "standard"


PRODUCT_CATALOG = [
    Product(
        name="Refurbished Noise-Canceling Headphones",
        category="electronics",
        price_tier="midrange",
        sustainable=True,
        brand_style="minimal",
        shipping_speed="fast",
        use_case="travel",
        shopper_intent="focus",
        description="Certified refurbished headphones for calls, travel, and deep work.",
    ),
    Product(
        name="Compact USB-C Travel Charger",
        category="electronics",
        price_tier="budget",
        sustainable=False,
        brand_style="minimal",
        shipping_speed="fast",
        use_case="travel",
        shopper_intent="utility",
        description="Small multi-port charger for laptops, phones, and tablets.",
    ),
    Product(
        name="Modular Desk Lamp",
        category="home",
        price_tier="midrange",
        sustainable=True,
        brand_style="modern",
        shipping_speed="standard",
        use_case="work",
        shopper_intent="comfort",
        description="Repairable LED desk lamp with warm and cool light modes.",
    ),
    Product(
        name="Organic Cotton Throw Blanket",
        category="home",
        price_tier="premium",
        sustainable=True,
        brand_style="warm",
        shipping_speed="standard",
        use_case="gift",
        shopper_intent="comfort",
        description="Soft, durable blanket made from certified organic cotton.",
    ),
    Product(
        name="Trail Daypack",
        category="outdoor",
        price_tier="midrange",
        sustainable=True,
        brand_style="rugged",
        shipping_speed="fast",
        use_case="travel",
        shopper_intent="adventure",
        description="Lightweight daypack with recycled fabric and hydration sleeve.",
    ),
    Product(
        name="Insulated Steel Bottle",
        category="outdoor",
        price_tier="budget",
        sustainable=True,
        brand_style="minimal",
        shipping_speed="fast",
        use_case="daily",
        shopper_intent="utility",
        description="Leak-proof bottle for commuting, gym bags, and weekend hikes.",
    ),
    Product(
        name="Merino Travel Hoodie",
        category="apparel",
        price_tier="premium",
        sustainable=True,
        brand_style="minimal",
        shipping_speed="standard",
        use_case="travel",
        shopper_intent="comfort",
        description="Odor-resistant hoodie designed for one-bag travel.",
    ),
    Product(
        name="Everyday Canvas Tote",
        category="apparel",
        price_tier="budget",
        sustainable=True,
        brand_style="casual",
        shipping_speed="fast",
        use_case="daily",
        shopper_intent="utility",
        description="Reusable tote for errands, groceries, and books.",
    ),
    Product(
        name="Adjustable Yoga Mat",
        category="wellness",
        price_tier="midrange",
        sustainable=True,
        brand_style="calm",
        shipping_speed="standard",
        use_case="daily",
        shopper_intent="routine",
        description="Non-slip mat with alignment guides for home workouts.",
    ),
    Product(
        name="Sleep Wind-Down Kit",
        category="wellness",
        price_tier="premium",
        sustainable=False,
        brand_style="calm",
        shipping_speed="standard",
        use_case="gift",
        shopper_intent="comfort",
        description="Eye mask, lavender spray, and guided sleep cards.",
    ),
    Product(
        name="Recycled Paper Notebook Set",
        category="office",
        price_tier="budget",
        sustainable=True,
        brand_style="minimal",
        shipping_speed="fast",
        use_case="work",
        shopper_intent="organization",
        description="Three ruled notebooks made from post-consumer paper.",
    ),
    Product(
        name="Ergonomic Monitor Stand",
        category="office",
        price_tier="midrange",
        sustainable=False,
        brand_style="modern",
        shipping_speed="fast",
        use_case="work",
        shopper_intent="comfort",
        description="Aluminum stand with storage space for keyboard and notes.",
    ),
]


def _binary_index(value: str, options: list[str], width: int) -> list[int]:
    if value not in options:
        raise ValueError(f"Unknown value {value!r}; expected one of {options}")

    index = options.index(value)
    return [int(bit) for bit in format(index, f"0{width}b")]


def encode_product(product: Product, context: ShopperContext) -> list[int]:
    """Encode product + shopper context into the existing 8-bit AO input shape."""

    category_bits = _binary_index(product.category, CATEGORIES, 3)
    price_bits = _binary_index(product.price_tier, PRICE_TIERS, 2)
    sustainability_bit = [int(product.sustainable and context.prefers_sustainable)]
    use_case_bits = _binary_index(context.use_case, USE_CASES, 2)
    return category_bits + price_bits + sustainability_bit + use_case_bits


def filter_products(
    catalog: Iterable[Product],
    context: ShopperContext,
) -> list[Product]:
    max_price_index = PRICE_TIERS.index(context.max_price_tier)

    return [
        product
        for product in catalog
        if product.category == context.category
        and PRICE_TIERS.index(product.price_tier) <= max_price_index
    ]


def score_product(
    product: Product,
    context: ShopperContext,
    feedback: dict[str, int] | None = None,
) -> float:
    score = 0.0

    if product.category == context.category:
        score += 0.28
    if PRICE_TIERS.index(product.price_tier) <= PRICE_TIERS.index(context.max_price_tier):
        score += 0.16
    if product.use_case == context.use_case:
        score += 0.18
    if product.sustainable and context.prefers_sustainable:
        score += 0.14
    if product.brand_style == context.style:
        score += 0.10
    if product.shipping_speed == context.shipping_speed:
        score += 0.08
    if context.use_case in {product.use_case, product.shopper_intent}:
        score += 0.06

    if feedback:
        score += max(-0.2, min(0.2, feedback.get(product.name, 0) * 0.05))

    return round(score, 4)


def recommend_products(
    context: ShopperContext,
    catalog: Iterable[Product] = PRODUCT_CATALOG,
    feedback: dict[str, int] | None = None,
    limit: int = 3,
) -> list[tuple[Product, float, list[int]]]:
    candidates = filter_products(catalog, context)
    if not candidates:
        candidates = list(catalog)

    ranked = sorted(
        (
            (product, score_product(product, context, feedback), encode_product(product, context))
            for product in candidates
        ),
        key=lambda item: (-item[1], item[0].name),
    )
    return ranked[:limit]
