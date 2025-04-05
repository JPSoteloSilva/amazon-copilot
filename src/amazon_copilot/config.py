"""Configuration for the Amazon Copilot application."""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class QdrantConfig:
    """Configuration for Qdrant database."""

    def __init__(self) -> None:
        """Initialize Qdrant configuration."""
        self.host = os.environ.get("QDRANT_HOST", "localhost")
        self.port = int(os.environ.get("QDRANT_PORT", "6333"))
        self.collection_name = "amazon_products"
        self.vector_size = 384  # Default size for all-MiniLM-L6-v2


class Config:
    """Application configuration."""

    def __init__(self) -> None:
        """Initialize application configuration."""
        self.data_dir = os.environ.get("DATA_DIR", "./data")
        self.qdrant = QdrantConfig()


# Global configuration instance
settings = Config()
