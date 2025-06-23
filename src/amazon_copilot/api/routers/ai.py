import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from amazon_copilot.schemas import Product
from amazon_copilot.services.ai.chatbot.graph import GraphState, run_conversation

router = APIRouter(prefix="/ai", tags=["ai"])

# In-memory storage for conversation states
conversation_states: dict[str, GraphState] = {}


class ConversationRequest(BaseModel):
    user_input: str = Field(..., description="User's message input")
    conversation_uuid: str | None = Field(
        None, description="Optional conversation UUID"
    )


class ConversationResponse(BaseModel):
    conversation_uuid: str = Field(..., description="Unique conversation identifier")
    assistant_message: str = Field(..., description="AI assistant's response message")
    products: list[Product] = Field(
        default_factory=list, description="List of found products"
    )


class ConversationStateResponse(BaseModel):
    conversation_uuid: str = Field(..., description="Unique conversation identifier")
    history: list[dict] = Field(
        default_factory=list, description="Conversation message history"
    )
    preferences: dict = Field(
        default_factory=dict, description="User preferences collected"
    )
    products: list[Product] = Field(
        default_factory=list, description="Products found in conversation"
    )
    message_count: int = Field(
        ge=0, description="Total number of messages in conversation"
    )
    has_products: bool = Field(description="Whether conversation has found products")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    type: str = Field(..., description="Error category")


@router.post(
    "/conversation",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "model": ConversationResponse,
            "description": "Successful conversation turn",
        },
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def handle_conversation(request: ConversationRequest) -> ConversationResponse:
    """
    Handle a conversation turn with the AI assistant.

    Args:
        request: Contains user input and optional conversation UUID

    Returns:
        Response with conversation UUID, assistant message, and products
    """
    try:
        # Generate new UUID if not provided
        conversation_uuid = request.conversation_uuid or str(uuid.uuid4())

        # Get existing state or None for new conversation
        existing_state = conversation_states.get(conversation_uuid)

        # Run the conversation
        updated_state = run_conversation(request.user_input, existing_state)

        # Store the updated state
        conversation_states[conversation_uuid] = updated_state

        # Get the last assistant message
        assistant_messages = [
            msg for msg in updated_state["history"] if msg.role == "assistant"
        ]

        if assistant_messages:
            assistant_message = assistant_messages[-1].content
        else:
            assistant_message = (
                "I'm here to help you find products. What are you looking for?"
            )

        return ConversationResponse(
            conversation_uuid=conversation_uuid,
            assistant_message=assistant_message,
            products=updated_state["products"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process conversation: {str(e)}",
        ) from e


@router.get(
    "/conversation/{conversation_uuid}/state",
    response_model=ConversationStateResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "model": ConversationStateResponse,
            "description": "Conversation state retrieved",
        },
        404: {"model": ErrorResponse, "description": "Conversation not found"},
    },
)
def get_conversation_state(conversation_uuid: str) -> ConversationStateResponse:
    """
    Get the current state of a conversation.

    Args:
        conversation_uuid: UUID of the conversation

    Returns:
        Current conversation state
    """
    if conversation_uuid not in conversation_states:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_uuid} not found",
        )

    state = conversation_states[conversation_uuid]

    return ConversationStateResponse(
        conversation_uuid=conversation_uuid,
        history=[msg.model_dump() for msg in state["history"]],
        preferences=state["preferences"].model_dump(),
        products=state["products"],
        message_count=len(state["history"]),
        has_products=len(state["products"]) > 0,
    )


@router.delete(
    "/conversation/{conversation_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Conversation deleted successfully"},
        404: {"model": ErrorResponse, "description": "Conversation not found"},
    },
)
def delete_conversation(conversation_uuid: str) -> None:
    """
    Delete a conversation and its state.

    Args:
        conversation_uuid: UUID of the conversation to delete
    """
    if conversation_uuid not in conversation_states:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {conversation_uuid} not found",
        )

    del conversation_states[conversation_uuid]


@router.get(
    "/conversations",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"model": list[str], "description": "List of active conversation UUIDs"},
    },
)
def list_conversations() -> list[str]:
    """
    List all active conversation UUIDs.

    Returns:
        List of conversation UUIDs
    """
    return list(conversation_states.keys())
