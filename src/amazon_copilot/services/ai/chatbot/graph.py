from typing import Literal

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from openai import OpenAI
from pydantic import BaseModel
from typing_extensions import TypedDict

from amazon_copilot.schemas import (
    AgentResponse,
    Message,
    PresentationResponse,
    Product,
    ProductQuery,
    QuestionsResponse,
)
from amazon_copilot.services.ai.chatbot.config import (
    GRAPH_THREAD_ID,
    LAST_N_MESSAGES,
    MIN_FIELDS_FOR_SEARCH,
    OPENAI_API_KEY,
    OPENAI_MODEL_NAME,
    OPENAI_TEMPERATURE,
    RECURSION_LIMIT,
    REQUIRED_FIELD_FOR_SEARCH,
)
from amazon_copilot.services.ai.chatbot.prompts import (
    get_collection_prompt,
    get_presentation_prompt,
    get_questions_prompt,
)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


class GraphState(TypedDict):
    """
    Represents the state of the conversation graph.

    Attributes:
        history: List of conversation messages
        preferences: User's product preferences collected so far
        products: List of products found from search
        restart_requested: Flag indicating if user wants to restart the conversation
    """

    history: list[Message]
    preferences: ProductQuery
    products: list[Product]
    restart_requested: bool


def search_products(preferences: ProductQuery) -> list[Product]:
    """Mock function to search products - returns a hardcoded list of products"""
    return [
        Product(
            id=1,
            name="Product 1",
            main_category="Category 1",
            sub_category="Subcategory 1",
            image="https://via.placeholder.com/150",
            link="https://example.com/product1",
            ratings=4.5,
            no_of_ratings=100,
            discount_price=100,
            actual_price=120,
        ),
    ]


def has_sufficient_preferences(preferences: ProductQuery) -> bool:
    """Check if we have enough information to search for products"""
    filled_fields = sum(
        [
            preferences.query is not None,
            preferences.main_category is not None,
            preferences.price_min is not None,
            preferences.price_max is not None,
        ]
    )
    return (
        filled_fields >= MIN_FIELDS_FOR_SEARCH
        and getattr(preferences, REQUIRED_FIELD_FOR_SEARCH) is not None
    )


def call_openai(
    prompt: str, user_message: str, response_model: type[BaseModel]
) -> BaseModel | None:
    """Helper function to call OpenAI API with Pydantic model validation"""
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_message},
    ]

    print("=== OpenAI Call Debug ===")
    print(f"Model: {OPENAI_MODEL_NAME}")
    print(f"Response model: {response_model}")
    print(f"System prompt: {prompt}")
    print(f"User message: {user_message}")
    print("=" * 50)

    try:
        completion = client.beta.chat.completions.parse(
            model=OPENAI_MODEL_NAME,
            messages=messages,  # type: ignore
            response_format=response_model,
            temperature=OPENAI_TEMPERATURE,
        )

        if completion.choices[0].message.parsed:
            return completion.choices[0].message.parsed
        else:
            print(
                f"OpenAI parsing failed. Raw response: "
                f"{completion.choices[0].message.content}"
            )
            return None

    except Exception as e:
        print(f"OpenAI API call failed: {str(e)}")
        return None


def collect_preferences_node(state: GraphState) -> GraphState:
    """
    Node to collect user preferences for product search.
    This handles both initial collection and refinement of preferences.
    """
    user_input = state["history"][-1].content

    # Build context from conversation history
    context = ""
    if len(state["history"]) > 1:
        context = "\n".join(
            [
                f"{msg.role}: {msg.content}"
                for msg in state["history"][-LAST_N_MESSAGES:]
            ]
        )

    # Add current preferences to context
    if state["preferences"]:
        context += f"\n\nCurrent preferences: {state['preferences'].model_dump()}"

    full_prompt = get_collection_prompt() + context

    agent_response = call_openai(full_prompt, user_input, AgentResponse)

    if agent_response and isinstance(agent_response, AgentResponse):
        # Merge new preferences with existing ones
        current_preferences = state["preferences"]
        new_preferences = agent_response.preferences
        merged_preferences_dict = current_preferences.model_dump()

        for field, new_value in new_preferences.model_dump().items():
            if new_value is not None:
                merged_preferences_dict[field] = new_value

        state["preferences"] = ProductQuery(**merged_preferences_dict)

        # Only add assistant message if we don't have sufficient preferences to proceed
        # If we have enough info, we'll proceed to search without adding a message
        if not has_sufficient_preferences(state["preferences"]):
            state["history"].append(
                Message(role="assistant", content=agent_response.message)
            )
    else:
        state["history"].append(
            Message(
                role="assistant", content="I'm sorry, I couldn't find any products."
            )
        )

    return state


def search_products_node(state: GraphState) -> GraphState:
    """Handle searching products state"""
    # Search for products using the collected preferences
    products = search_products(state["preferences"])
    state["products"] = products
    return state


def present_products_node(state: GraphState) -> GraphState:
    """Node to present found products to the user"""
    preferences_summary = {
        k: v for k, v in state["preferences"].model_dump().items() if v is not None
    }

    # Create context with products for the AI to reference in generating the message
    context = f"""
    User preferences collected: {preferences_summary}
    Products found: {len(state["products"])} products

    Here are the products to present to the user:
    {[product.model_dump() for product in state["products"]]}

    Generate a friendly message introducing these products to the user.
    """

    prompt = get_presentation_prompt()
    presentation_response = call_openai(prompt, context, PresentationResponse)

    if presentation_response and isinstance(
        presentation_response, PresentationResponse
    ):
        state["history"].append(
            Message(
                role="assistant",
                content=presentation_response.message,
            )
        )
    else:
        state["history"].append(
            Message(
                role="assistant", content="I'm sorry, I couldn't find any products."
            )
        )

    return state


def answer_questions_node(state: GraphState) -> GraphState:
    """Node to answer questions about presented products"""
    user_input = state["history"][-1].content

    # Build comprehensive context with products and conversation history
    products_info = []
    for product in state["products"]:
        product_info = f"""
        Product: {product.name}
        - ID: {product.id}
        - Category: {product.main_category} > {product.sub_category}
        - Price: ${product.discount_price} (original: ${product.actual_price})
        - Rating: {product.ratings}/5 ({product.no_of_ratings} reviews)
        - Link: {product.link}
        """
        products_info.append(product_info.strip())

    # Get recent conversation for context
    recent_messages = []
    for msg in state["history"][-LAST_N_MESSAGES:]:
        recent_messages.append(f"{msg.role}: {msg.content}")

    context = f"""
    PRODUCTS PRESENTED TO USER:
    {chr(10).join(products_info)}

    RECENT CONVERSATION HISTORY:
    {chr(10).join(recent_messages)}

    USER PREFERENCES:
    {state["preferences"].model_dump()}

    The user is asking: {user_input}
    """

    prompt = get_questions_prompt() + f"\n\nContext: {context}"
    questions_response = call_openai(prompt, user_input, QuestionsResponse)

    if questions_response is not None and isinstance(
        questions_response, QuestionsResponse
    ):
        if questions_response.restart:
            state["restart_requested"] = True
            # Reset state for new search but keep the original user input
            state["products"] = []
            state["preferences"] = ProductQuery()
            # Don't add the assistant's restart acknowledgment message yet
            # The collection node will handle the user's original request
        else:
            # Normal question answering - add the response
            state["history"].append(
                Message(role="assistant", content=questions_response.message)
            )
    else:
        state["history"].append(
            Message(
                role="assistant", content="I'm sorry, I couldn't find any products."
            )
        )

    return state


def route_after_collection(
    state: GraphState,
) -> Literal["search_products", "collect_preferences"]:
    """
    Conditional edge function to route after preference collection.
    Routes to search if we have sufficient preferences, otherwise stays in collection.
    """
    has_sufficient = has_sufficient_preferences(state["preferences"])
    route_decision = "search_products" if has_sufficient else "collect_preferences"

    return route_decision


def route_after_questions(
    state: GraphState,
) -> Literal["collect_preferences", "answer_questions"]:
    """
    Conditional edge function to route after answering questions.
    Routes to collection if restart is requested, otherwise stays in questions.
    """
    if state.get("restart_requested", False):
        return "collect_preferences"
    return "answer_questions"


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
            preferences=ProductQuery(),
            products=[],
            restart_requested=False,
        )
        # Start with collection for new conversations
        start_node = "collect_preferences"
    else:
        # Add new user message to existing conversation
        state["history"].append(Message(role="user", content=user_input))
        # Reset restart flag for new input
        state["restart_requested"] = False

        # Determine starting node based on conversation state
        if state["products"]:  # Products have been presented
            start_node = "answer_questions"
        else:  # No products yet, continue collection
            start_node = "collect_preferences"

    # Create workflow with dynamic starting point
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("collect_preferences", collect_preferences_node)
    workflow.add_node("search_products", search_products_node)
    workflow.add_node("present_products", present_products_node)
    workflow.add_node("answer_questions", answer_questions_node)

    if start_node == "collect_preferences":
        # Collection flow
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
    else:
        # Questions flow
        workflow.add_edge(START, "answer_questions")
        workflow.add_conditional_edges(
            "answer_questions",
            route_after_questions,
            {
                "answer_questions": END,
                "collect_preferences": "collect_preferences",
            },
        )
        # If restarting from questions, add collection flow
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
        # Graceful error handling
        error_message = f"I encountered an error: {str(e)}. Let's try again."
        state["history"].append(Message(role="assistant", content=error_message))
        return state
