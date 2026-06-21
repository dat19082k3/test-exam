from typing import Optional
from pydantic import BaseModel, HttpUrl, Field

class BookBase(BaseModel):
    title: str = Field(..., title="Book Title")
    price: float = Field(..., title="Book Price in £")
    availability: str = Field(..., title="Stock Availability")
    product_url: str = Field(..., title="URL to the product page")
    star_rating: int = Field(..., title="Star rating (1-5)", ge=1, le=5)
    country: str = Field("Unknown", title="Randomly assigned country")

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int

    class Config:
        from_attributes = True
