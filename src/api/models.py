from typing import Optional
from pydantic import BaseModel, HttpUrl, Field, ConfigDict

class BookBase(BaseModel):
    title: str = Field(..., title="Book Title")
    price: float = Field(..., title="Book Price in £", gt=0)
    availability: str = Field(..., title="Stock Availability")
    product_url: str = Field(..., title="URL to the product page")
    star_rating: int = Field(..., title="Star rating (1-5)", ge=1, le=5)
    country: str = Field("Unknown", title="Randomly assigned country")

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
