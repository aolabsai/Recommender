# Product Catalog Recommender Domain

This example adapts the AO Labs recommender pattern to an e-commerce product catalog. It uses a local product dataset, deterministic feature encoding, and a fallback ranker so reviewers can validate the domain without API keys or private AO packages.

## Domain

The catalog covers electronics, home, outdoor, apparel, wellness, and office products. Each product includes:

- category
- price tier
- sustainability flag
- brand style
- shipping speed
- use case
- shopper intent
- description

## AO Input Encoding

The product recommender keeps the same 8-bit input shape used by the base recommender architecture:

| Segment | Bits | Source |
| --- | ---: | --- |
| Category | 3 | Product category |
| Price tier | 2 | Product price tier |
| Sustainability | 1 | Whether the product matches a sustainability preference |
| Use case | 2 | Shopper context |

This maps to `arch_i = [3, 2, 1, 2]` in `arch__ProductRecommender.py`.

## Run the Demo

Streamlit UI:

```bash
streamlit run product_recommender.py
```

CLI fallback:

```bash
python3 product_recommender.py
```

## Validate

```bash
python3 -m unittest tests/test_product_domain.py
python3 -m py_compile product_domain.py product_recommender.py arch__ProductRecommender.py tests/test_product_domain.py
```
