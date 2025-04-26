import re

import numpy as np
import pandas as pd

from amazon_copilot.schemas import Product


def convert_ratings_count(value: str | int) -> int:
    if isinstance(value, str):
        # Remove commas and convert to int
        value = value.replace(",", "")
        if value.isdigit():
            return int(value)
        else:
            return 0
    return value


def convert_rupee_to_dollar(price_str: str) -> int:
    """
    Convert price from Indian Rupee (₹) format to USD as integer

    Args:
        price_str: String price in format "₹XX,XXX"

    Returns:
        Integer price in USD
    """
    if not isinstance(price_str, str) or not price_str:
        return 0

    # Extract numeric value using regex (removing ₹ and comma)
    match = re.search(r"₹([\d,]+)", price_str)
    if not match:
        return 0

    # Remove commas and convert to float
    rupee_amount = float(match.group(1).replace(",", ""))

    # Convert to USD (approximate exchange rate: 1 USD = 83 INR)
    exchange_rate = 85.50
    dollar_amount = rupee_amount / exchange_rate

    # Return as integer
    return int(dollar_amount)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df["no_of_ratings"] = df["no_of_ratings"].apply(convert_ratings_count)
    df["discount_price"] = df["discount_price"].apply(convert_rupee_to_dollar)
    df["actual_price"] = df["actual_price"].apply(convert_rupee_to_dollar)
    df["ratings"] = df["ratings"].astype(float)
    df = df.dropna(subset=["id", "image", "name"])
    return df


def load_csv(
    csv_path: str, nrows: int | None = None, skiprows: int | None = None
) -> pd.DataFrame:
    """Load product data from a CSV file.

    Args:
        csv_path: Path to the CSV file
        nrows: Number of rows to read (None for all)
        skiprows: Number of rows to skip (None for no skipping)

    Returns:
        DataFrame containing the product data
    """
    df = pd.read_csv(csv_path, nrows=nrows, skiprows=skiprows)  # type: ignore
    df = clean_data(df)
    return df


def load_data(
    csv_path: str, nrows: int | None = None, skiprows: int | None = None
) -> list[Product]:
    df = load_csv(csv_path, nrows=nrows, skiprows=skiprows)

    # Replace NaN values with None before creating Product instances
    df = df.replace({np.nan: None})

    products = [Product(**row) for _, row in df.iterrows()]  # type: ignore
    return products
