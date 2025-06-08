from amazon_copilot.shared.schemas import Product


def list_products() -> list[Product]:
    p1 = Product(
        id=1,
        name="Product 1",
        main_category="Main Category 1",
        sub_category="Sub Category 1",
        image="https://via.placeholder.com/150",
        link="https://www.amazon.com/product1",
        ratings=4.5,
        no_of_ratings=100,
        discount_price=100,
        actual_price=150,
    )
    p2 = Product(
        id=2,
        name="Product 2",
        main_category="Main Category 2",
        sub_category="Sub Category 2",
        image="https://via.placeholder.com/150",
        link="https://www.amazon.com/product2",
        ratings=4.0,
        no_of_ratings=50,
        discount_price=80,
        actual_price=100,
    )
    return [p1, p2]


def get_product(product_id: int) -> Product | None:
    return Product(
        id=product_id,
        name=f"Product {product_id}",
        main_category=f"Main Category {product_id}",
        sub_category=f"Sub Category {product_id}",
        image=f"https://via.placeholder.com/150?text={product_id}",
        link=f"https://www.amazon.com/product{product_id}",
        ratings=4.0,
        no_of_ratings=50,
        discount_price=80,
        actual_price=100,
    )
