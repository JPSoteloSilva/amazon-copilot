import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

from amazon_copilot.qdrant_client import QdrantClient
from amazon_copilot.schemas import Product


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def get_qdrant_client() -> QdrantClient:
    """Get a QdrantClient instance."""
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    dense_model = os.getenv("DENSE_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    sparse_model = os.getenv("SPARSE_MODEL", "Qdrant/bm25")
    return QdrantClient(
        host=host,
        port=port,
        dense_model_name=dense_model,
        sparse_model_name=sparse_model,
    )


def convert_ratings_count(value: str | int) -> int:
    if isinstance(value, str):
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

    match = re.search(r"₹([\d,]+)", price_str)
    if not match:
        return 0

    rupee_amount = float(match.group(1).replace(",", ""))
    exchange_rate = 85.50
    dollar_amount = rupee_amount / exchange_rate
    return int(dollar_amount)


def validate_image_url(url: str, timeout: int = 5) -> bool:
    """
    Validate if an image URL is accessible and returns a valid response.

    Args:
        url: The image URL to validate
        timeout: Request timeout in seconds

    Returns:
        True if the image URL is valid and accessible, False otherwise
    """
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        # Check if status code is successful (2xx) and content type is image
        if response.status_code >= 200 and response.status_code < 300:
            content_type = response.headers.get("content-type", "").lower()
            return content_type.startswith("image/")
        return False
    except (requests.RequestException, requests.Timeout, Exception):
        return False


def validate_image_urls_batch(urls: list[str], max_workers: int = 20) -> list[bool]:
    """
    Validate multiple image URLs concurrently with progress bar.

    Args:
        urls: List of image URLs to validate
        max_workers: Maximum number of concurrent threads

    Returns:
        List of boolean values indicating which URLs are valid
    """
    logger = get_logger(__name__)
    results = [False] * len(urls)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all validation tasks
        future_to_index = {
            executor.submit(validate_image_url, url): i for i, url in enumerate(urls)
        }

        # Process completed tasks with progress bar
        with tqdm(total=len(urls), desc="Validating image URLs", unit="url") as pbar:
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    logger.warning(f"Error validating URL at index {index}: {e}")
                    results[index] = False
                pbar.update(1)

    return results


def clean_data(df: pd.DataFrame, validate_images: bool = True) -> pd.DataFrame:
    """
    Clean the data from the csv file

    Args:
        df: DataFrame containing the product data
        validate_images: Whether to validate image URLs and filter out invalid ones

    Returns:
        DataFrame containing the cleaned product data
    """
    logger = get_logger(__name__)
    initial_count = len(df)

    df = df.dropna(
        subset=[
            "id",
            "image",
            "name",
            "main_category",
            "actual_price",
            "discount_price",
        ]
    )
    df["ratings"] = df["ratings"].astype(str)
    df = df[df["ratings"] != "Get"]
    df = df[df["ratings"] != "FREE"]
    df = df[~df["ratings"].str.contains("₹")]

    df["no_of_ratings"] = df["no_of_ratings"].apply(convert_ratings_count)
    df["discount_price"] = df["discount_price"].apply(convert_rupee_to_dollar)
    df["actual_price"] = df["actual_price"].apply(convert_rupee_to_dollar)
    df["ratings"] = df["ratings"].astype(float)
    df = df.replace({np.nan: None})

    # Validate image URLs if requested
    if validate_images and len(df) > 0:
        logger.info(f"Validating {len(df)} image URLs...")
        image_urls = df["image"].tolist()
        valid_images = validate_image_urls_batch(image_urls)

        # Filter out rows with invalid images
        df = df[valid_images].reset_index(drop=True)
        invalid_count = sum(not valid for valid in valid_images)
        logger.info(f"Filtered out {invalid_count} products with invalid image URLs")

    final_count = len(df)
    logger.info(f"Data cleaning complete: {initial_count} -> {final_count} products")

    return df


def load_data(
    csv_path: str,
    nrows: int | None = None,
    skiprows: int = 0,
    validate_images: bool = True,
) -> list[Product]:
    """
    Load the data from the csv file

    Args:
        csv_path: Path to the csv file
        nrows: Number of rows to read
        skiprows: Number of data rows to skip (header is always preserved)
        validate_images: Whether to validate image URLs and filter out invalid ones

    Returns:
        List of Product instances
    """
    # Skip data rows while preserving header row (row 0)
    if skiprows > 0:
        # Create list that skips rows 1 through skiprows but keeps row 0 (header)
        skiprows_list = list(range(1, skiprows + 1))
        df = pd.read_csv(csv_path, nrows=nrows, skiprows=skiprows_list, header=0)
    else:
        df = pd.read_csv(csv_path, nrows=nrows, header=0)

    start_id = skiprows + 1
    ids = list(range(start_id, start_id + len(df)))
    df["id"] = ids

    df = clean_data(df, validate_images=validate_images)
    products = [
        Product(
            id=row["id"],
            name=row["name"],
            main_category=row["main_category"],
            sub_category=row["sub_category"],
            image=row["image"],
            link=row["link"],
            ratings=row["ratings"],
            no_of_ratings=row["no_of_ratings"],
            discount_price=row["discount_price"],
            actual_price=row["actual_price"],
        )
        for _, row in df.iterrows()
    ]
    return products
