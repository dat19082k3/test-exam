import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

from src.logger import get_logger

load_dotenv()

logger = get_logger("countries")

API_URL = "https://api.restcountries.com/countries/v5"
CACHE_FILE = Path("data/countries_cache.json")
FALLBACK_FILE = Path("data/countries_fallback.json")
API_KEY = os.getenv("RESTCOUNTRIES_API_KEY")

def get_countries() -> list[str]:
    """
    Retrieve a list of country names from restcountries.com.
    Uses a local cache file (data/countries_cache.json) to avoid repeated API calls.
    Returns a small fallback list if both the API and cache fail.
    """
    if CACHE_FILE.exists():
        logger.info("Loading countries from local cache.")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
            
    logger.info("Fetching countries from API via pagination...")
    all_countries = []
    limit = 100
    offset = 0
    has_more = True
    
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    else:
        logger.warning("No API key found in .env. Request might fail if v5 requires it.")

    try:
        while has_more:
            url = f"{API_URL}?limit={limit}&offset={offset}&response_fields=names.common"
            logger.info(f"Fetching: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            payload = response.json()
            data = payload.get("data")
            
            if not data or "objects" not in data:
                raise ValueError(f"Unexpected API response format: {str(payload)[:100]}")
                
            objects = data["objects"]
            meta = data.get("meta", {})
            
            # Extract common names
            for item in objects:
                if "names" in item and "common" in item["names"]:
                    all_countries.append(item["names"]["common"])
                    
            has_more = meta.get("more", False)
            offset += limit
            
        # Save to cache
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(all_countries, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Successfully fetched and cached {len(all_countries)} countries.")
        return all_countries
        
    except Exception as e:
        logger.error(f"Failed to fetch countries from API: {e}")
        
        if FALLBACK_FILE.exists():
            logger.warning(f"Using static fallback file: {FALLBACK_FILE}")
            with open(FALLBACK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
                
        fallback = ["United States", "United Kingdom", "Vietnam", "Japan", "France"]
        logger.warning(f"Using hardcoded fallback list: {fallback}")
        return fallback

if __name__ == "__main__":
    c = get_countries()
    print(f"Total countries: {len(c)}")
    print(f"Sample: {c[:5]}")
