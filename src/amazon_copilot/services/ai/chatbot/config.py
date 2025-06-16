"""
Configuration constants and settings for the Amazon Copilot AI service.

This module centralizes all configuration values to improve maintainability
and make it easier to adjust settings across the AI service.
"""

import os
from typing import Final

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL_NAME: Final[str] = "gpt-4.1-nano"
OPENAI_TEMPERATURE: Final[float] = 0.0

# Conversation Settings
LAST_N_MESSAGES: Final[int] = 10
RECURSION_LIMIT: Final[int] = 10

# Search Configuration
MIN_FIELDS_FOR_SEARCH: Final[int] = 3
REQUIRED_FIELD_FOR_SEARCH: Final[str] = "query"

# Graph Configuration
GRAPH_THREAD_ID: Final[str] = "conversation"

# Validation
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable is required. "
        "Please set it in your .env file or environment."
    )
