# Book Scraper & RPA Automation System

An end-to-end pipeline that scrapes book data, enriches it with country information, serves it via a secure REST API, and automates Wikipedia searches for 5-star books to generate an Excel report.

## Features

- Phase 1: Web Scraper (concurrently scrapes books from toscrape.com and backs up HTML)
- Phase 2: Data Enrichment (assigns randomized countries via restcountries.com API)
- Phase 3: REST API (FastAPI server with API Key auth, rate limiting, and pagination)
- Phase 4: RPA Bot (consumes the API, automates a headless browser to search Wikipedia, and generates an Excel report)

## Documentation

For deep dives into the system design and API usage, please refer to:
- [System Architecture (C4 Model & Data Flow)](ARCHITECTURE.md)
- [REST API Standard Operating Procedure (SOP)](API_SOP.md)

## Setup & Installation

Follow these steps to get the system running locally (requires Python 3.13+).

1. Create and activate a virtual environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux/macOS:
source venv/bin/activate
```

2. Install dependencies and browser binaries
```bash
pip install -r requirements.txt
playwright install chromium
```

3. Configure environment variables
```bash
cp .env.example .env
```
Make sure to open the `.env` file and set `API_KEY=your-secret-api-key`. This key is required to access the REST API.

## Usage Guide

The system is composed of modular components. Run them in the following order:

### 1. Run the Web Scraper
Scrapes the target website and saves the raw data to `data/books.json` and `data/books.csv`.
```bash
python src/scraper.py
```

### 2. Start the REST API

**Option A: Using Docker (Recommended)**
Run the API server in a lightweight container. The local `data/` folder is automatically mounted.
```bash
docker-compose up -d --build
```

**Option B: Local Execution**
Starts the server locally. Keep this terminal open.
```bash
uvicorn src.api.main:app --reload
```
View the interactive API docs at: http://localhost:8000/docs

### 3. Run the RPA Bot
Open a new terminal, activate the virtual environment, and run the automation bot. It will fetch the 5-star books from your API, search Wikipedia, and save an Excel file in the `output/` directory.
```bash
python src/bot/wiki_bot.py
```

## Running Tests

The project includes unit tests for both the API and the Scraper. To run them:
```bash
pytest -v
```

## Project Structure

```text
├── .env.example             # Environment variables template
├── data/                    # Generated datasets
├── html_backup/             # Raw HTML backups from the scraper
├── output/                  # Generated Excel reports
├── requirements.txt         # Project dependencies
├── src/
│   ├── scraper.py           # Web scraping script
│   ├── countries.py         # Third-party API integration
│   ├── logger.py            # Centralized logger
│   ├── api/                 # FastAPI REST application
│   └── bot/                 # Playwright RPA bot
└── tests/                   # Pytest suite
```
