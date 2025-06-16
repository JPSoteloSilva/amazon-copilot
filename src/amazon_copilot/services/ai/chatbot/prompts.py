import json
from pathlib import Path

from amazon_copilot.schemas import (
    AgentResponse,
    PresentationResponse,
    QuestionsResponse,
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
    categories_list = ", ".join(f'"{cat}"' for cat in main_categories)

    # Use replace instead of format to avoid issues with JSON schema curly braces
    prompt = prompt_template.replace("{main_categories}", categories_list)
    prompt = prompt.replace("{schema}", json.dumps(AgentResponse.model_json_schema()))
    return prompt


def get_presentation_prompt() -> str:
    """Get the presentation prompt with dynamic content."""
    prompt_template = load_prompt("presentation.txt")
    # Use replace instead of format to avoid issues with JSON schema curly braces
    return prompt_template.replace(
        "{schema}", json.dumps(PresentationResponse.model_json_schema())
    )


def get_questions_prompt() -> str:
    """Get the questions prompt."""
    prompt_template = load_prompt("questions.txt")
    # Use replace instead of format to avoid issues with JSON schema curly braces
    return prompt_template.replace(
        "{schema}", json.dumps(QuestionsResponse.model_json_schema())
    )
