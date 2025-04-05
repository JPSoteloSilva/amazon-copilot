"""Data loading functionality for Amazon Copilot."""

import argparse
import os
from typing import Any

import pandas as pd

from amazon_copilot.database import QdrantService
from amazon_copilot.models import AmazonProduct


def load_csv(
    csv_path: str = "data/Amazon-Products.csv", nrows: int | None = None
) -> pd.DataFrame:
    """Load product data from a CSV file.

    Args:
        csv_path: Path to the CSV file
        nrows: Number of rows to read (None for all)

    Returns:
        DataFrame containing the product data
    """
    # Explicitly specify dtypes to avoid type-related issues
    return pd.read_csv(  # type: ignore
        csv_path,
        nrows=nrows,
        dtype={
            "id": str,
            "name": str,
            "main_category": str,
            "sub_category": str,
            "image": str,
            "link": str,
            "ratings": str,
            "no_of_ratings": str,
            "discount_price": str,
            "actual_price": str,
        },
        # Handle encoding and errors
        encoding="utf-8",
        on_bad_lines="skip",
    )


def process_dataframe(df: pd.DataFrame) -> list[AmazonProduct]:
    """Process the DataFrame and convert it to AmazonProduct objects.

    Args:
        df: DataFrame containing the product data

    Returns:
        List of AmazonProduct objects
    """
    products: list[AmazonProduct] = []

    for _, row in df.iterrows():  # type: ignore
        try:
            # Convert row data to a dictionary for safer handling
            row_data: dict[str, Any] = row.to_dict()  # type: ignore

            # Convert ratings to float if possible
            ratings: float | None = None
            if "ratings" in row_data and pd.notna(row_data["ratings"]):
                try:
                    ratings_str = str(row_data["ratings"]).strip()
                    if ratings_str and ratings_str != "nan":
                        ratings = float(ratings_str.split()[0])
                except (ValueError, IndexError):
                    pass

            # Create AmazonProduct
            product = AmazonProduct(
                id=str(row_data.get("id", "")),
                name=str(row_data.get("name", "")),
                main_category=str(row_data.get("main_category", "")),
                sub_category=str(row_data.get("sub_category", "")),
                image=str(row_data.get("image", "")),
                link=str(row_data.get("link", "")),
                ratings=ratings,
                no_of_ratings=str(row_data.get("no_of_ratings", "")),
                discount_price=str(row_data.get("discount_price", "")),
                actual_price=str(row_data.get("actual_price", "")),
            )

            # Only add products with valid names
            if product.name and product.name != "nan" and product.name != "None":
                products.append(product)

        except Exception as e:
            # Safe handling of id value
            id_value = row.get("id", "unknown") if hasattr(row, "get") else "unknown"  # type: ignore
            print(f"Error processing row {id_value}: {e}")

    return products


def load_data(nrows: int | None = None) -> None:
    """Load data from CSV and add it to the database.

    Args:
        nrows: Number of rows to read (None for all)
    """
    # Get the absolute path to the CSV file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "../.."))
    csv_path = os.path.join(root_dir, "data/Amazon-Products.csv")

    # Check if the file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"CSV file not found at {csv_path}. Please download the dataset."
        )

    print(f"Loading data from {csv_path}")
    df = load_csv(csv_path, nrows=nrows)
    print(f"Loaded {len(df)} rows from CSV")

    # Process the DataFrame
    products = process_dataframe(df)
    print(f"Created {len(products)} valid product objects")

    # Add products to the database
    db = QdrantService()
    for i, product in enumerate(products):
        db.add_product(product)
        if (i + 1) % 10 == 0:
            print(f"Added {i + 1}/{len(products)} products to the database")

    print(f"Successfully added {len(products)} products to the database")


def main() -> None:
    """Main entry point for data loading script."""
    parser = argparse.ArgumentParser(description="Load product data into the database.")
    parser.add_argument(
        "--nrows", type=int, default=None, help="Number of rows to load from the CSV"
    )
    args = parser.parse_args()

    load_data(nrows=args.nrows)


if __name__ == "__main__":
    main()
