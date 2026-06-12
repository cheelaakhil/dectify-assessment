"""
Pydantic schemas for favorites.
"""
from datetime import datetime
from typing import Any
from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    item_type: str   # apod | mars | asteroid | eonet
    item_payload: dict[str, Any]


class FavoriteResponse(BaseModel):
    id: int
    item_type: str
    item_payload: dict[str, Any]
    saved_at: datetime

    model_config = {"from_attributes": True}

class FavoriteDeleteResponse(BaseModel):
    message: str
