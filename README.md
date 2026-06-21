# Book Scraper Project

A robust web scraping pipeline that extracts book data from [Books to Scrape](https://books.toscrape.com), including automatic pagination handling, concurrent HTML backups, and JSON/CSV data exports.

## Prerequisites

- **Python 3.10+** installed on your system.

## Installation & Setup

To avoid conflicting dependencies and permission issues, it is highly recommended to run this project inside a virtual environment.

### 1. Create a virtual environment
```bash
python -m venv venv
```

### 2. Activate the virtual environment
- **Windows**:
  ```cmd
  venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper pipeline from the root directory of the project:

```bash
python -m src.scraper
```

The scraper will automatically:
1. Navigate through the "Sequential Art" category pages.
2. Scrape details for all available books (Title, Price, Availability, URL, Star Rating).
3. Concurrently download and backup the raw HTML of each product page.
4. Export the structured data.

## Output

After a successful run, the following files and directories will be generated:
- `data/books.json`: Scraped data in JSON format.
- `data/books.csv`: Scraped data in CSV format (UTF-8 with BOM for Excel compatibility).
- `html_backup/`: A directory containing the raw HTML files of every scraped book for debugging purposes.
- `logs/`: Application execution logs.

## Troubleshooting

- **`ModuleNotFoundError`**: Ensure you have activated your virtual environment (`venv\Scripts\activate` on Windows, `source venv/bin/activate` on macOS) before running the script.
- **`PermissionError: [Errno 13] Permission denied` (Windows)**: This usually happens if you have `data/books.csv` open in Microsoft Excel while the scraper is trying to write to it. Close the file and run the script again.
- **Missing or broken images in HTML backups**: This is expected. The HTML backups contain raw relative links intended for DOM debugging, not for offline viewing.
