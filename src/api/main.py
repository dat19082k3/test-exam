import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Query
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from src.api.models import BookCreate, Book
from src.api import services

load_dotenv()

def verify_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")):
    expected_key = os.getenv("API_KEY")
    if not expected_key:
        raise HTTPException(status_code=500, detail="API_KEY not configured on server")
    if not x_api_key or x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

@asynccontextmanager
async def lifespan(app: FastAPI):
    services.load_db()
    yield

app = FastAPI(
    title="Book Scraper API",
    description="API for accessing scraped books with Country data",
    dependencies=[Depends(verify_api_key)],
    lifespan=lifespan
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/books", response_model=list[Book])
@limiter.limit("30/minute")
def get_books(
    request: Request, 
    skip: int = Query(0, ge=0, description="Number of records to skip"), 
    limit: int = Query(100, ge=1, le=100, description="Max records to return"),
    country: str = Query(None, description="Filter books by publisher country")
):
    """Retrieve all books with pagination and optional filtering."""
    return services.get_books(skip=skip, limit=limit, country=country)

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

@app.delete("/books/{title_id}", status_code=200)
@limiter.limit("10/minute")
def delete_book(request: Request, title_id: str):
    """Delete a book record by its title."""
    success = services.delete_book(title_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"detail": "Book deleted"}
