import csv
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
from pathlib import Path
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

BACKUP_DIR = Path("html_backup")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def save_html_backup(product_url: str, title: str) -> str:
    """
    Download raw HTML of the product page and save it to html_backup/ for backup purposes.
    
    Args:
        product_url: The absolute URL of the product page.
        title: The title of the book to be used as the filename.
        
    Returns:
        The path where the HTML file was saved.
    """
    safe_title = re.sub(r'[^\w\-]', '_', title)
    safe_title = re.sub(r'_+', '_', safe_title).strip('_')
    
    filepath = BACKUP_DIR / f"{safe_title}.html"
    
    logger.info(f"Backing up HTML for '{title}' to {filepath}")

    response = requests.get(product_url)
    response.raise_for_status()
    
    with open(filepath, "wb") as f:
        f.write(response.content)
        
    return str(filepath)

def save_to_json(books: list[dict], filepath: str) -> None:
    """Save scraped books to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(books)} books to JSON: {filepath}")

def save_to_csv(books: list[dict], filepath: str) -> None:
    """Save scraped books to a CSV file."""
    if not books:
        logger.warning(f"No books to save to CSV: {filepath}")
        return
        
    # Use utf-8-sig to include BOM so Excel opens it correctly
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["title", "price", "availability", "product_url", "star_rating"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(books)
        
    logger.info(f"Saved {len(books)} books to CSV: {filepath}")

def main():
    """Main pipeline for scraping books."""
    logger.info("Starting web scraper pipeline...")
    start_time = time.time()
    
    all_books = []
    page_num = 1
    
    while True:
        html = fetch_page(page_num)
        if html is None:
            break
            
        current_url = f"{BASE_URL}index.html" if page_num == 1 else f"{BASE_URL}page-{page_num}.html"
        books_on_page = parse_books(html, current_url)
        all_books.extend(books_on_page)
        
        # Backup HTML concurrently to save time
        # ponytail: max_workers=10 provides a balance between speed and not overwhelming the server
        with ThreadPoolExecutor(max_workers=10) as executor:
            for book in books_on_page:
                executor.submit(save_html_backup, book["product_url"], book["title"])
            
        page_num += 1
        
    logger.info(f"Finished scraping {page_num - 1} pages.")
    
    save_to_json(all_books, "data/books.json")
    save_to_csv(all_books, "data/books.csv")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Pipeline completed in {elapsed_time:.2f} seconds. Total books: {len(all_books)}")

if __name__ == "__main__":
    main()
