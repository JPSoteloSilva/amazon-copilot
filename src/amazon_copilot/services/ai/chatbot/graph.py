from typing import Literal

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from openai import OpenAI
from pydantic import BaseModel
from typing_extensions import TypedDict

from amazon_copilot.schemas import Product
from amazon_copilot.services.ai.chatbot.config import (
    GRAPH_THREAD_ID,
    LAST_N_MESSAGES,
    MIN_FIELDS_FOR_SEARCH,
    NUM_PRODUCTS_TO_PRESENT,
    OPENAI_API_KEY,
    OPENAI_MODEL_NAME,
    OPENAI_TEMPERATURE,
    RECURSION_LIMIT,
    REQUIRED_FIELD_FOR_SEARCH,
)
from amazon_copilot.services.ai.chatbot.schemas import (
    CollectionResponse,
    Message,
    PresentationResponse,
    UserPreferences,
)
from amazon_copilot.services.ai.chatbot.utils import (
    get_collection_prompt,
    get_presentation_prompt,
)
from amazon_copilot.services.products import list_products
from amazon_copilot.utils import get_qdrant_client

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


class GraphState(TypedDict):
    """
    Represents the state of the conversation graph.

    Attributes:
        history: List of conversation messages
        preferences: User's product preferences collected so far
        products: List of products found from search
    """

    history: list[Message]
    preferences: UserPreferences
    products: list[Product]


def has_sufficient_preferences(preferences: UserPreferences) -> bool:
    """Check if we have enough information to search for products"""
    filled_fields = sum(
        [
            preferences.query is not None,
            preferences.main_category is not None,
            preferences.price_min is not None,
            preferences.price_max is not None,
        ]
    )

    required_field_value = getattr(preferences, REQUIRED_FIELD_FOR_SEARCH)

    result = filled_fields >= MIN_FIELDS_FOR_SEARCH and required_field_value is not None

    return result


def call_openai(
    system_prompt: str, messages: list[Message], response_model: type[BaseModel]
) -> BaseModel | None:
    """Helper function to call OpenAI API with Pydantic model validation"""
    openai_messages = [{"role": "system", "content": system_prompt}]
    openai_messages.extend([msg.model_dump() for msg in messages])

    try:
        completion = client.beta.chat.completions.parse(
            model=OPENAI_MODEL_NAME,
            messages=openai_messages,  # type: ignore
            response_format=response_model,
            temperature=OPENAI_TEMPERATURE,
        )

        if completion.choices[0].message.parsed:
            return completion.choices[0].message.parsed
        else:
            return None

    except Exception:
        return None


def collect_preferences_node(state: GraphState) -> GraphState:
    """
    Node to collect user preferences for product search.
    This handles both initial collection and refinement of preferences.
    """
    # Get the system prompt
    system_prompt = get_collection_prompt()

    # Add current preferences to system prompt if they exist
    if state["preferences"] and any(
        v is not None for v in state["preferences"].model_dump().values()
    ):
        system_prompt += f"\n\nCurrent preferences: {state['preferences'].model_dump()}"

    # Get the last N messages for context
    recent_messages = (
        state["history"][-LAST_N_MESSAGES:]
        if len(state["history"]) > LAST_N_MESSAGES
        else state["history"]
    )

    collection_response = call_openai(
        system_prompt, recent_messages, CollectionResponse
    )

    if collection_response and isinstance(collection_response, CollectionResponse):
        current_preferences = state["preferences"]
        new_preferences = collection_response.preferences
        merged_preferences_dict = current_preferences.model_dump()

        for field, new_value in new_preferences.model_dump().items():
            if new_value is not None:
                merged_preferences_dict[field] = new_value

        state["preferences"] = UserPreferences(**merged_preferences_dict)

        sufficient = has_sufficient_preferences(state["preferences"])

        if not sufficient:
            assistant_message = Message(
                role="assistant", content=collection_response.message
            )
            state["history"].append(assistant_message)
        else:
            pass
    else:
        error_message = Message(
            role="assistant", content="I'm sorry, I couldn't find any products."
        )
        state["history"].append(error_message)

    return state


def search_products_node(state: GraphState) -> GraphState:
    """Handle searching products state"""
    if state["preferences"].query:
        qdrant_client = get_qdrant_client()
        products = list_products(
            client=qdrant_client,
            query=state["preferences"].query,
            collection_name="amazon_products",
            limit=NUM_PRODUCTS_TO_PRESENT,
            main_category=state["preferences"].main_category,
            price_min=state["preferences"].price_min,
            price_max=state["preferences"].price_max,
        )
        state["products"] = products
    else:
        state["products"] = []
    return state


def present_products_node(state: GraphState) -> GraphState:
    """Node to present found products to the user"""
    context_content = (
        "Generate a friendly message introducing these products to the user."
    )

    messages = [Message(role="user", content=context_content)]

    system_prompt = get_presentation_prompt(state["preferences"], state["products"])
    presentation_response = call_openai(system_prompt, messages, PresentationResponse)

    if presentation_response and isinstance(
        presentation_response, PresentationResponse
    ):
        assistant_message = Message(
            role="assistant", content=presentation_response.message
        )
        state["history"].append(assistant_message)
    else:
        error_message = Message(
            role="assistant", content="I'm sorry, I couldn't find any products."
        )
        state["history"].append(error_message)

    return state


def route_after_collection(
    state: GraphState,
) -> Literal["search_products", "collect_preferences"]:
    """
    Conditional edge function to route after preference collection.
    Routes to search if we have sufficient preferences, otherwise stays in collection.
    """
    has_sufficient = has_sufficient_preferences(state["preferences"])
    return "search_products" if has_sufficient else "collect_preferences"


def run_conversation(user_input: str, state: GraphState | None = None) -> GraphState:
    """
    Run the conversation workflow with the given user input.

    Args:
        user_input: The user's message
        state: Optional existing conversation state

    Returns:
        Updated conversation state
    """
    # Initialize state for new conversation
    if state is None:
        state = GraphState(
            history=[Message(role="user", content=user_input)],
            preferences=UserPreferences(),
            products=[],
        )
    else:
        state["history"].append(Message(role="user", content=user_input))

    workflow = StateGraph(GraphState)

    workflow.add_node("collect_preferences", collect_preferences_node)
    workflow.add_node("search_products", search_products_node)
    workflow.add_node("present_products", present_products_node)

    workflow.add_edge(START, "collect_preferences")
    workflow.add_conditional_edges(
        "collect_preferences",
        route_after_collection,
        {
            "collect_preferences": END,
            "search_products": "search_products",
        },
    )
    workflow.add_edge("search_products", "present_products")
    workflow.add_edge("present_products", END)

    app = workflow.compile()

    config: RunnableConfig = {
        "recursion_limit": RECURSION_LIMIT,
        "configurable": {"thread_id": GRAPH_THREAD_ID},
    }

    try:
        result = app.invoke(state, config=config)
        return result  # type: ignore
    except Exception as e:
        error_message = f"I encountered an error: {str(e)}. Let's try again."
        state["history"].append(Message(role="assistant", content=error_message))
        return state
