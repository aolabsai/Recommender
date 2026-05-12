import unittest

from product_domain import (
    PRODUCT_CATALOG,
    Product,
    ShopperContext,
    encode_product,
    filter_products,
    recommend_products,
    score_product,
)


class ProductDomainTest(unittest.TestCase):
    def test_encode_product_matches_ao_input_shape(self) -> None:
        context = ShopperContext(
            category="electronics",
            max_price_tier="midrange",
            prefers_sustainable=True,
            use_case="travel",
        )

        bits = encode_product(PRODUCT_CATALOG[0], context)

        self.assertEqual(len(bits), 8)
        self.assertTrue(all(bit in {0, 1} for bit in bits))

    def test_filter_products_respects_category_and_max_price(self) -> None:
        context = ShopperContext(category="electronics", max_price_tier="budget")

        products = filter_products(PRODUCT_CATALOG, context)

        self.assertEqual([product.name for product in products], ["Compact USB-C Travel Charger"])

    def test_sustainable_travel_context_ranks_headphones_first(self) -> None:
        context = ShopperContext(
            category="electronics",
            max_price_tier="midrange",
            prefers_sustainable=True,
            use_case="travel",
            style="minimal",
            shipping_speed="fast",
        )

        recommendations = recommend_products(context, PRODUCT_CATALOG)

        self.assertEqual(recommendations[0][0].name, "Refurbished Noise-Canceling Headphones")
        self.assertGreater(recommendations[0][1], recommendations[1][1])

    def test_feedback_can_change_ranking(self) -> None:
        context = ShopperContext(
            category="electronics",
            max_price_tier="midrange",
            prefers_sustainable=True,
            use_case="travel",
            style="minimal",
            shipping_speed="fast",
        )

        feedback = {
            "Refurbished Noise-Canceling Headphones": -5,
            "Compact USB-C Travel Charger": 5,
        }
        recommendations = recommend_products(context, PRODUCT_CATALOG, feedback=feedback)

        self.assertEqual(recommendations[0][0].name, "Compact USB-C Travel Charger")

    def test_unknown_category_raises_helpful_error(self) -> None:
        product = Product(
            name="Unknown",
            category="not-a-category",
            price_tier="budget",
            sustainable=False,
            brand_style="minimal",
            shipping_speed="fast",
            use_case="daily",
            shopper_intent="utility",
            description="Invalid test product",
        )

        with self.assertRaisesRegex(ValueError, "Unknown value"):
            encode_product(product, ShopperContext())

    def test_score_is_deterministic(self) -> None:
        context = ShopperContext(category="office", max_price_tier="midrange", use_case="work")
        product = next(item for item in PRODUCT_CATALOG if item.name == "Ergonomic Monitor Stand")

        self.assertEqual(score_product(product, context), score_product(product, context))


if __name__ == "__main__":
    unittest.main()
