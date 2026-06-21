import os
import pytest
from fastapi.testclient import TestClient

# Set up test environment before importing the app
os.environ["API_KEY"] = "test-secret-key"

from src.api.main import app
from src.api import services

client = TestClient(app)
HEADERS = {"X-API-Key": "test-secret-key"}

@pytest.fixture(autouse=True)
def mock_db(tmp_path):
    # Override the database file for testing
    test_db_file = tmp_path / "test_books.json"
    
    # Pre-populate with some data
    import json
    initial_data = [
        {
            "id": 1,
            "title": "Test Book 1",
            "price": 10.99,
            "availability": "In stock",
            "product_url": "http://test1.com",
            "star_rating": 5,
            "publisher_country": "Vietnam"
        },
        {
            "id": 2,
            "title": "Test Book 2",
            "price": 5.99,
            "availability": "In stock",
            "product_url": "http://test2.com",
            "star_rating": 3,
            "publisher_country": "Japan"
        }
    ]
    with open(test_db_file, "w", encoding="utf-8") as f:
        json.dump(initial_data, f)

    # Patch the services module
    original_file = services.BOOKS_FILE
    services.BOOKS_FILE = test_db_file
    services.load_db() # Reload with test data
    
    # Clear rate limits before each test by resetting the Limiter's storage
    app.state.limiter.reset()
    
    yield
    
    services.BOOKS_FILE = original_file
    services.load_db()

def test_unauthorized_access():
    response = client.get("/books")
    assert response.status_code == 401

def test_get_all_books():
    response = client.get("/books", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Test Book 1"

def test_get_book_success():
    response = client.get("/books/1", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Book 1"

def test_get_book_not_found():
    response = client.get("/books/999", headers=HEADERS)
    assert response.status_code == 404

def test_create_book():
    new_book = {
        "title": "New Test Book",
        "price": 15.0,
        "availability": "In stock",
        "product_url": "http://new.com",
        "star_rating": 4,
        "publisher_country": "USA"
    }
    response = client.post("/books", json=new_book, headers=HEADERS)
    assert response.status_code == 201
    assert response.json()["id"] == 3
    assert response.json()["title"] == "New Test Book"

def test_create_book_invalid_data():
    invalid_book = {
        "title": "New Test Book",
        "price": "Not a float", # Invalid
        "availability": "In stock",
        "product_url": "http://new.com",
        "star_rating": 6, # Invalid, max is 5
        "publisher_country": "USA"
    }
    response = client.post("/books", json=invalid_book, headers=HEADERS)
    assert response.status_code == 422

def test_delete_book():
    response = client.delete("/books/Test Book 1", headers=HEADERS)
    assert response.status_code == 200
    
    # Verify it's gone
    response2 = client.get("/books/1", headers=HEADERS)
    assert response2.status_code == 404

def test_rate_limiter():
    # POST is limited to 10/minute.
    valid_book = {
        "title": "Spam Book",
        "price": 1.0,
        "availability": "In stock",
        "product_url": "http://spam.com",
        "star_rating": 1,
        "publisher_country": "Spam"
    }
    
    # 10 successful requests
    for _ in range(10):
        res = client.post("/books", json=valid_book, headers=HEADERS)
        assert res.status_code == 201
        
    # The 11th request should be rate limited
    response = client.post("/books", json=valid_book, headers=HEADERS)
    assert response.status_code == 429

def test_get_books_pagination_valid():
    response = client.get("/books?skip=1&limit=1", headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Book 2"

def test_get_books_pagination_invalid_limit():
    # Limit > 100 should be rejected by Pydantic Query validator
    response = client.get("/books?limit=101", headers=HEADERS)
    assert response.status_code == 422

def test_get_books_pagination_negative_skip():
    # Skip < 0 should be rejected
    response = client.get("/books?skip=-1", headers=HEADERS)
    assert response.status_code == 422

def test_create_book_negative_price():
    # Price must be > 0
    invalid_book = {
        "title": "Cheap Book",
        "price": -5.0,
        "availability": "In stock",
        "product_url": "http://cheap.com",
        "star_rating": 4,
        "publisher_country": "USA"
    }
    response = client.post("/books", json=invalid_book, headers=HEADERS)
    assert response.status_code == 422

def test_create_book_zero_star_rating():
    # Star rating must be >= 1
    invalid_book = {
        "title": "Bad Book",
        "price": 10.0,
        "availability": "In stock",
        "product_url": "http://bad.com",
        "star_rating": 0,
        "publisher_country": "USA"
    }
    response = client.post("/books", json=invalid_book, headers=HEADERS)
    assert response.status_code == 422

def test_create_book_missing_title():
    # Title is required
    invalid_book = {
        "price": 10.0,
        "availability": "In stock",
        "product_url": "http://bad.com",
        "star_rating": 3,
        "publisher_country": "USA"
    }
    response = client.post("/books", json=invalid_book, headers=HEADERS)
    assert response.status_code == 422

def test_get_book_invalid_id_type():
    # ID must be an integer, strings should fail validation
    response = client.get("/books/abc", headers=HEADERS)
    assert response.status_code == 422

