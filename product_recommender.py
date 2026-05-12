from __future__ import annotations

from product_domain import (
    CATEGORIES,
    PRICE_TIERS,
    USE_CASES,
    PRODUCT_CATALOG,
    ShopperContext,
    recommend_products,
)


def running_inside_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except ModuleNotFoundError:
        return False


def run_cli_demo() -> None:
    context = ShopperContext(
        category="electronics",
        max_price_tier="midrange",
        prefers_sustainable=True,
        use_case="travel",
        style="minimal",
        shipping_speed="fast",
    )

    for product, score, bits in recommend_products(context, PRODUCT_CATALOG):
        print(f"{score:.2f} {bits} {product.name} - {product.description}")


def run_streamlit_app() -> None:
    import streamlit as st

    st.set_page_config(page_title="AO Product Recommender", page_icon="🛒")
    st.title("AO Product Catalog Recommender")
    st.caption("A local e-commerce recommender domain for continuously trainable AO agents.")

    category = st.selectbox("Shopping category", CATEGORIES)
    max_price_tier = st.selectbox("Maximum price tier", PRICE_TIERS, index=1)
    use_case = st.selectbox("Shopping use case", USE_CASES)
    prefers_sustainable = st.checkbox("Prefer sustainable products", value=True)
    style = st.selectbox(
        "Preferred style",
        ["minimal", "modern", "warm", "rugged", "casual", "calm"],
    )
    shipping_speed = st.selectbox("Shipping preference", ["standard", "fast"], index=1)

    if "product_feedback" not in st.session_state:
        st.session_state.product_feedback = {}

    context = ShopperContext(
        category=category,
        max_price_tier=max_price_tier,
        prefers_sustainable=prefers_sustainable,
        use_case=use_case,
        style=style,
        shipping_speed=shipping_speed,
    )

    st.subheader("Recommendations")
    for product, score, bits in recommend_products(
        context,
        PRODUCT_CATALOG,
        feedback=st.session_state.product_feedback,
    ):
        with st.container(border=True):
            st.markdown(f"### {product.name}")
            st.write(product.description)
            st.write(
                {
                    "score": score,
                    "ao_binary_input": bits,
                    "category": product.category,
                    "price_tier": product.price_tier,
                    "sustainable": product.sustainable,
                    "shipping_speed": product.shipping_speed,
                    "use_case": product.use_case,
                }
            )

            col_like, col_dislike = st.columns(2)
            with col_like:
                if st.button("Recommend more", key=f"like-{product.name}"):
                    st.session_state.product_feedback[product.name] = (
                        st.session_state.product_feedback.get(product.name, 0) + 1
                    )
                    st.rerun()
            with col_dislike:
                if st.button("Show less", key=f"dislike-{product.name}"):
                    st.session_state.product_feedback[product.name] = (
                        st.session_state.product_feedback.get(product.name, 0) - 1
                    )
                    st.rerun()


if __name__ == "__main__":
    if running_inside_streamlit():
        run_streamlit_app()
    else:
        run_cli_demo()
