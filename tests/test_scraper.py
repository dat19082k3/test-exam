import pytest
from src.scraper import parse_books

def test_parse_books():
    """Test that the HTML parsing logic correctly extracts book data."""
    mock_html = """
    <article class="product_pod">
        <div class="image_container">
                <a href="../../../scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html"><img src="thumb.jpg" alt="Scott Pilgrim" class="thumbnail"></a>
        </div>
        <p class="star-rating Five">
            <i class="icon-star"></i><i class="icon-star"></i><i class="icon-star"></i><i class="icon-star"></i><i class="icon-star"></i>
        </p>
        <h3><a href="../../../scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html" title="Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)">Scott Pilgrim's Precious Little...</a></h3>
        <div class="product_price">
            <p class="price_color">Â£52.29</p>
            <p class="instock availability">
                <i class="icon-ok"></i>
                In stock
            </p>
        </div>
    </article>
    """
    
    current_url = "https://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html"
    books = parse_books(mock_html, current_url)
    
    assert len(books) == 1
    book = books[0]
    
    # Assert extracted values
    assert book["title"] == "Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)"
    assert book["price"] == 52.29
    assert book["availability"] == "In stock"
    assert book["star_rating"] == 5
    assert "scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html" in book["product_url"]

def test_parse_books_empty():
    """Test that parsing an empty or irrelevant HTML returns an empty list."""
    mock_html = "<html><body><h1>No books here</h1></body></html>"
    books = parse_books(mock_html, "http://example.com")
    assert len(books) == 0

def test_parse_books_missing_elements():
    """Test that the scraper gracefully handles missing critical tags."""
    mock_html = """
    <article class="product_pod">
        <div class="image_container"></div>
        <!-- Missing star rating completely -->
        <!-- Missing h3 title completely -->
        <div class="product_price">
            <!-- Missing price_color completely -->
            <!-- Missing availability completely -->
        </div>
    </article>
    """
    books = parse_books(mock_html, "http://example.com")
    assert len(books) == 1
    book = books[0]
    
    assert book["title"] == "Unknown"
    assert book["price"] == 0.0
    assert book["availability"] == "Unknown"
    assert book["star_rating"] == 0
    assert book["product_url"] == "http://example.com" # fallback to current_url when href=""
    
def test_parse_books_malformed_price_and_rating():
    """Test that the scraper handles weird price formats and unknown star ratings."""
    mock_html = """
    <article class="product_pod">
        <p class="star-rating Ten"></p> <!-- Unknown rating class -->
        <h3><a href="book.html" title="Weird Book">Weird Book</a></h3>
        <div class="product_price">
            <p class="price_color">Â£99.99</p> <!-- Weird encoding character -->
        </div>
    </article>
    """
    books = parse_books(mock_html, "http://example.com")
    assert len(books) == 1
    book = books[0]
    
    assert book["star_rating"] == 0 # "Ten" is not in RATING_MAP
    assert book["price"] == 99.99

