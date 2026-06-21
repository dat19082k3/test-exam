import requests
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
