import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from src.logger import get_logger

logger = get_logger("scraper")

BASE_URL = "https://books.toscrape.com/catalogue/category/books/sequential-art_5/"

def fetch_page(page_num: int) -> str | None:
    """
    Fetch the HTML content of a specific category page.
    
    Args:
        page_num: The page number to fetch.
        
    Returns:
        The raw HTML string of the page, or None if the page does not exist (404).
        
    Raises:
        requests.HTTPError if the status code is not 200 or 404.
    """
    if page_num == 1:
        url = f"{BASE_URL}index.html"
    else:
        url = f"{BASE_URL}page-{page_num}.html"
        
    logger.info(f"Fetching page {page_num} from {url}")
    
    response = requests.get(url)
    
    # If the page does not exist (end of pagination), the server returns 404
    if response.status_code == 404:
        logger.info(f"Page {page_num} not found (404). Reached end of pagination.")
        return None
    
    # If any other error occurs (500, 403, etc.), raise an exception to stop the program
    response.raise_for_status()
    
    return response.text

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

def parse_books(html: str, current_url: str) -> list[dict]:
    """
    Parse a list of books from a category page HTML.
    
    Args:
        html: Raw HTML string of the category page.
        current_url: URL of the current page, used to resolve relative links.
        
    Returns:
        List of dictionaries containing book data.
    """
    soup = BeautifulSoup(html, "lxml")
    books = []
    
    for article in soup.select("article.product_pod"):
        # Title
        title_tag = article.select_one("h3 > a")
        title = title_tag["title"] if title_tag else "Unknown"
        
        # Product URL (convert relative to absolute)
        href = title_tag["href"] if title_tag else ""
        product_url = urljoin(current_url, href)
        
        # Price (e.g. '£51.77' -> 51.77)
        price_tag = article.select_one("p.price_color")
        price_text = price_tag.text.strip() if price_tag else "0"
        # Remove currency symbol and non-numeric characters
        price = float(price_text.replace("£", "").replace("Â", "")) 
        
        # Availability
        avail_tag = article.select_one("p.instock.availability")
        availability = avail_tag.text.strip() if avail_tag else "Unknown"
        
        # Star rating (e.g. 'star-rating Three')
        star_tag = article.select_one("p.star-rating")
        star_rating = 0
        if star_tag:
            classes = star_tag.get("class", [])
            for c in classes:
                if c in RATING_MAP:
                    star_rating = RATING_MAP[c]
                    break
                    
        books.append({
            "title": title,
            "price": price,
            "availability": availability,
            "product_url": product_url,
            "star_rating": star_rating
        })
        
    logger.info(f"Parsed {len(books)} books from page.")
    return books
