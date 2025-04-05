"""Main module for the Amazon Copilot e-commerce platform."""

from dotenv import load_dotenv

# Version info since we don't have __init__.py
__version__ = "0.1.0"

# Load environment variables from .env file
load_dotenv()


def main() -> None:
    """Run the Amazon Copilot application."""
    print("Amazon Copilot E-commerce Platform")
    print("----------------------------------")
    print(f"Version: {__version__}")
    print("Ready to start your LLM-powered e-commerce journey!")


if __name__ == "__main__":
    main()
