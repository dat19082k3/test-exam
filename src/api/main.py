import os
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from src.api.models import BookCreate, Book
from src.api import services

load_dotenv()

def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    expected_key = os.getenv("API_KEY")
    if not expected_key:
        raise HTTPException(status_code=500, detail="API_KEY not configured on server")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

app = FastAPI(
    title="Book Scraper API",
    description="API for accessing scraped books with Country data",
    dependencies=[Depends(verify_api_key)]
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
def startup_event():
    services.load_db()

@app.get("/books", response_model=list[Book])
@limiter.limit("30/minute")
def get_books(request: Request, skip: int = 0, limit: int = 100):
    """Retrieve all books with pagination."""
    return services.get_books(skip=skip, limit=limit)

@app.get("/books/{book_id}", response_model=Book)
@limiter.limit("30/minute")
def get_book(request: Request, book_id: int):
    """Retrieve a specific book by its ID."""
    book = services.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/books", response_model=Book, status_code=201)
@limiter.limit("10/minute")
def create_book(request: Request, book: BookCreate):
    """Create a new book record."""
    return services.create_book(book)

@app.delete("/books/{book_id}", status_code=200)
@limiter.limit("10/minute")
def delete_book(request: Request, book_id: int):
    """Delete a book record by its ID."""
    success = services.delete_book(book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"detail": "Book deleted"}
