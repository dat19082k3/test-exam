import json
from pathlib import Path
from src.api.models import BookCreate, Book

BOOKS_FILE = Path("data/books_with_country.json")

# In-memory store
_books_db: list[dict] = []
_next_id: int = 1

def load_db():
    global _books_db, _next_id
    if BOOKS_FILE.exists():
        with open(BOOKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            _books_db = []
            for idx, item in enumerate(data, start=1):
                item["id"] = idx
                _books_db.append(item)
            _next_id = len(_books_db) + 1
    else:
        _books_db = []
        _next_id = 1

def save_db():
    BOOKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BOOKS_FILE, "w", encoding="utf-8") as f:
        # Strip the in-memory 'id' to keep the JSON clean as originally scraped
        pure_data = [{k: v for k, v in book.items() if k != "id"} for book in _books_db]
        json.dump(pure_data, f, ensure_ascii=False, indent=2)

def get_books(skip: int = 0, limit: int = 100, country: str = None) -> list[dict]:
    if not _books_db:
        load_db()
    
    results = _books_db
    if country:
        results = [b for b in results if b.get("publisher_country") == country]
        
    return results[skip : skip + limit]

def get_book(title_id: str) -> dict | None:
    if not _books_db:
        load_db()
    for book in _books_db:
        title = book.get("title", "")
        url_parts = [p for p in book.get("product_url", "").split("/") if p and p not in ("..", "index.html")]
        slug = url_parts[-1] if url_parts else ""
        
        if title == title_id or slug == title_id:
            return book
    return None

def create_book(book: BookCreate) -> dict:
    global _next_id
    if not _books_db:
        load_db()
    
    new_book = book.model_dump()
    new_book["id"] = _next_id
    _next_id += 1
    _books_db.append(new_book)
    save_db()
    return new_book

def delete_book(title_id: str) -> bool:
    if not _books_db:
        load_db()
        
    for i, book in enumerate(_books_db):
        title = book.get("title", "")
        # Extract slug from product_url (e.g., "scott-pilgrims-precious-little-life-scott-pilgrim-1_987")
        url_parts = [p for p in book.get("product_url", "").split("/") if p and p not in ("..", "index.html")]
        slug = url_parts[-1] if url_parts else ""
        
        # Accept either exact title or the slugified title
        if title == title_id or slug == title_id:
            _books_db.pop(i)
            save_db()
            return True
    return False
