from pydantic import BaseModel


class UserPreferences(BaseModel):
    query: str | None = None
    main_category: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    color: str | None = None
    brand: str | None = None


class CollectionResponse(BaseModel):
    message: str
    preferences: UserPreferences


class PresentationResponse(BaseModel):
    message: str


class Message(BaseModel):
    role: str
    content: str
