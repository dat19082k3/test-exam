# System Architecture

This document describes the architectural design of the Book Scraper & RPA Automation System using the C4 Model approach (Context, Containers, Components) visualized via Mermaid diagrams.

## 1. System Context (Level 1)

The system context diagram shows how the system fits into the world, interacting with external web platforms to gather, enrich, and report data.

```mermaid
graph TD
    User([End User])
    System[Book Automation System]
    BooksSite[Books.toscrape.com]
    RestCountries[RestCountries API]
    Wiki[Wikipedia]

    User -->|Triggers Pipeline & Views Reports| System
    System -->|Scrapes book catalog| BooksSite
    System -->|Fetches country data| RestCountries
    System -->|Searches for book metadata| Wiki
```

## 2. Container Diagram (Level 2)

The container diagram zooms into the `Book Automation System` to show the distinct executable units and data stores.

```mermaid
graph TD
    subgraph Book Automation System
        Scraper[Web Scraper Module]
        Storage[(Local File System)]
        API[FastAPI REST Server]
        RPA[Playwright RPA Bot]
    end

    BooksSite[books.toscrape.com]
    RestCountries[restcountries.com]
    Wiki[wikipedia.org]

    Scraper -->|1. Scrape HTML| BooksSite
    Scraper -->|2. Get Countries| RestCountries
    Scraper -->|3. Save JSON/CSV & HTML Backup| Storage
    API -->|4. Load Data| Storage
    RPA -->|5. Fetch 5-Star Books via HTTP| API
    RPA -->|6. Search Title| Wiki
    RPA -->|7. Generate Report| Storage
```

## 3. Data Flow & Component Execution (Level 3)

A sequence diagram showing the step-by-step lifecycle of a single book entity through the entire pipeline.

```mermaid
sequenceDiagram
    participant Scraper
    participant ExtAPI as RestCountries
    participant Storage as File System
    participant API as FastAPI
    participant RPA as Wiki Bot
    participant Wiki as Wikipedia

    rect rgb(240, 248, 255)
    note right of Scraper: Phase 1 & 2: Collection
    Scraper->>ExtAPI: GET /v3.1/all
    ExtAPI-->>Scraper: List of Countries
    Scraper->>BooksSite: GET /catalogue/page-X.html
    BooksSite-->>Scraper: Raw HTML
    Scraper->>Storage: Backup HTML & Save books.json
    end

    rect rgb(255, 245, 238)
    note right of API: Phase 3: Serving
    API->>Storage: Read books.json into memory
    API-->>API: Initialize Rate Limiter & Auth
    end

    rect rgb(240, 255, 240)
    note right of RPA: Phase 4: Automation
    RPA->>API: GET /books?min_rating=5 (w/ API_KEY)
    API-->>RPA: JSON List of 5-star Books
    
    loop For Each Book
        RPA->>Wiki: Type book title into Search
        Wiki-->>RPA: Redirect to Article
        RPA->>RPA: Extract Article URL
    end
    
    RPA->>Storage: Save rpa_report_v2.xlsx
    end
```

## 4. Key Design Decisions

- **Stateless API Storage**: Instead of setting up PostgreSQL or SQLite, the API reads `books.json` into memory on application startup (`lifespan` event). This removes database dependencies and keeps the setup dead-simple while remaining incredibly fast.
- **Aggressive Caching**: Wikipedia searches are potentially slow. The Playwright bot reuses a single `BrowserContext` and `Page` object instead of launching new tabs, maximizing speed and minimizing memory overhead.
- **Resilient Parsing**: The scraper doesn't crash on missing tags; it assigns default fallback values, ensuring the pipeline never breaks halfway through a 50-page scrape.
