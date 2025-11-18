"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Birthday song app schemas

class SongRequest(BaseModel):
    """User request parameters to generate a personalized birthday song"""
    name: str = Field(..., description="Name of the person the song is for")
    age: Optional[int] = Field(None, ge=0, le=130)
    relation: Optional[str] = Field(None, description="Who they are to you (friend, mom, colleague, etc.)")
    style: Literal["pop", "rock", "hiphop", "ballad"] = Field("pop")
    language: Literal["de", "en"] = Field("de")
    tempo: Literal["slow", "medium", "fast"] = Field("medium")

class Song(BaseModel):
    """Generated song document (metadata + lyrics). Audio can be re-generated on the fly"""
    request: SongRequest
    title: str
    lyrics: List[str] = Field(..., description="Lyrics split by lines")
    audio_seconds: float = 0.0
    style: str
    language: str
    preview_note_count: int = 0
