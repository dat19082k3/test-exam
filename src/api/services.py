import json
from pathlib import Path
from src.api.models import BookCreate, Book

BOOKS_FILE = Path("data/books.json")

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
        json.dump(_books_db, f, ensure_ascii=False, indent=2)

def get_books(skip: int = 0, limit: int = 100) -> list[dict]:
    if not _books_db:
        load_db()
    return _books_db[skip : skip + limit]

def get_book(book_id: int) -> dict | None:
    if not _books_db:
        load_db()
    for book in _books_db:
        if book.get("id") == book_id:
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

def delete_book(book_id: int) -> bool:
    if not _books_db:
        load_db()
        
    for i, book in enumerate(_books_db):
        if book.get("id") == book_id:
            _books_db.pop(i)
            save_db()
            return True
    return False
