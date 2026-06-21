import os
import httpx
from dotenv import load_dotenv

load_dotenv()

def get_5_star_books(api_url: str = "http://localhost:8000/books", limit: int = 100):
    """
    Fetch books from the REST API and filter for 5-star ratings.
    """
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found in environment variables")
        
    headers = {"X-API-Key": api_key}
    
    # In production, we would use a while loop with `skip` parameter to fetch all pages.
    response = httpx.get(f"{api_url}?limit={limit}", headers=headers)
    response.raise_for_status()
    
    books = response.json()
    return [book for book in books if book.get("star_rating") == 5]

if __name__ == "__main__":
    print("Fetching 5-star books from API...")
    try:
        five_star_books = get_5_star_books()
        print(f"Success! Found {len(five_star_books)} 5-star books:")
        for idx, b in enumerate(five_star_books, 1):
            print(f"{idx}. {b['title']} (Country: {b.get('country')})")
    except Exception as e:
        print(f"Error fetching books: {e}")
