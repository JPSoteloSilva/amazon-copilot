import os

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from amazon_copilot.services.products import add_products
from amazon_copilot.utils import get_logger, get_qdrant_client, load_data

app = typer.Typer(help="Amazon Copilot CLI for managing product data")
console = Console()
logger = get_logger(__name__)


@app.command(help="Create a new collection in Qdrant")
def create_collection(
    collection_name: str = typer.Argument(..., help="Name of the collection to create"),
) -> None:
    """Create a new collection in Qdrant"""
    client = get_qdrant_client()
    logger.info(f"Creating collection '{collection_name}'")

    collection_created = client.create_collection(collection_name)

    if collection_created:
        logger.info(f"Collection '{collection_name}' created successfully")
    else:
        logger.warning(f"Collection '{collection_name}' already exists")


@app.command(help="Delete a collection from Qdrant")
def delete_collection(
    collection_name: str = typer.Argument(..., help="Name of the collection to delete"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force deletion without confirmation"
    ),
) -> None:
    """Delete a collection from Qdrant"""
    if not force:
        confirm = typer.confirm(
            f"Are you sure you want to delete collection '{collection_name}'?"
        )
        if not confirm:
            logger.info("Deletion cancelled")
            return

    client = get_qdrant_client()
    logger.info(f"Deleting collection '{collection_name}'")

    try:
        deleted = client.delete_collection(collection_name)
        if deleted:
            logger.info(f"Collection '{collection_name}' deleted successfully")
        else:
            logger.error(f"Failed to delete collection '{collection_name}'")
    except Exception as e:
        logger.error(f"Error deleting collection: {e}")


@app.command(help="Search for products in Qdrant")
def search_products(
    query: str = typer.Argument(..., help="Search query"),
    collection_name: str = typer.Argument(
        "amazon_products", help="Name of the collection to search"
    ),
    main_category: str | None = typer.Option(None, help="Filter by main category"),
    sub_category: str | None = typer.Option(None, help="Filter by sub category"),
    limit: int = typer.Option(10, help="Maximum number of results to return"),
    offset: int = typer.Option(0, help="Offset for pagination"),
) -> None:
    """Search for products in Qdrant"""
    client = get_qdrant_client()
    logger.info(f"Searching for '{query}' in collection '{collection_name}'")

    try:
        results = client.search_similar_products(
            query=query,
            collection_name=collection_name,
            main_category=main_category,
            sub_category=sub_category,
            limit=limit,
            offset=offset,
        )

        if not results:
            logger.info("No products found")
            return

        table = Table(title=f"Search Results for '{query}'")
        table.add_column("ID", justify="right")
        table.add_column("Name", no_wrap=False)
        table.add_column("Category", no_wrap=False)
        table.add_column("Price ($)", justify="right")
        table.add_column("Rating", justify="center")

        for product in results:
            table.add_row(
                str(product.id),
                product.name,
                (f"{product.main_category or ''} > {product.sub_category or ''}"),
                f"{product.discount_price or 'N/A'}",
                (f"{product.ratings or 'N/A'} ({product.no_of_ratings or 0})"),
            )

        console.print(table)

    except Exception as e:
        logger.error(f"Error searching products: {e}")


@app.command(help="Load products from CSV into Qdrant")
def load_products(
    data_path: str = typer.Argument(..., help="Path to CSV file with product data"),
    collection_name: str = typer.Argument(
        ..., help="Name of the collection to load data into"
    ),
    nrows: int | None = typer.Option(None, help="Number of rows to read from CSV"),
    skiprows: int = typer.Option(0, help="Number of rows to skip from CSV"),
    batch_size: int = typer.Option(1000, help="Batch size for loading data"),
) -> None:
    """Load products from CSV into Qdrant"""
    if not os.path.exists(data_path):
        logger.error(f"File not found: {data_path}")
        raise typer.Exit(1)

    client = get_qdrant_client()
    logger.info(
        f"Loading products from '{data_path}' into collection '{collection_name}'"
    )

    products = load_data(data_path, nrows=nrows, skiprows=skiprows)

    try:
        successful_adds, failed_products = add_products(
            client=client,
            collection_name=collection_name,
            products=products,
            batch_size=batch_size,
        )
        logger.info(f"Products loaded successfully: {len(successful_adds)}")
        logger.info(f"Failed products: {failed_products}")
    except Exception as e:
        logger.error(f"Error loading products: {e}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    load_dotenv()
    app()
