import json
from pathlib import Path

from amazon_copilot.schemas import Product
from amazon_copilot.services.ai.chatbot.schemas import (
    CollectionResponse,
    PresentationResponse,
    UserPreferences,
)

# Get the directory where this file is located
PROMPTS_DIR = Path(__file__).parent / "prompts"
CATEGORIES_FILE = PROMPTS_DIR / "categories.json"


def load_prompt(filename: str) -> str:
    """Load a prompt from a text file."""
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, encoding="utf-8") as file:
        return file.read().strip()


def load_categories() -> list[str]:
    """Load main categories from categories.json file."""
    with open(CATEGORIES_FILE, encoding="utf-8") as file:
        categories_data = json.load(file)
        return categories_data["main_category"]


def get_collection_prompt() -> str:
    """Get the collection prompt with dynamic content."""
    prompt_template = load_prompt("collection.txt")
    main_categories = load_categories()

    prompt = prompt_template.format(
        main_categories=main_categories,
        schema=json.dumps(CollectionResponse.model_json_schema()),
    )
    return prompt


def get_presentation_prompt(
    user_preferences: UserPreferences, products: list[Product]
) -> str:
    """Get the presentation prompt with dynamic content."""
    prompt_template = load_prompt("presentation.txt")

    preferences_text = user_preferences.model_dump_json(exclude_none=True, indent=2)
    products_text = [product.model_dump_json(indent=2) for product in products]

    prompt = prompt_template.format(
        user_preferences=preferences_text,
        products=products_text,
        schema=json.dumps(PresentationResponse.model_json_schema()),
    )
    return prompt
