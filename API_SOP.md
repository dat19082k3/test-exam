# REST API Standard Operating Procedure (SOP)

This document outlines the standard procedures for integrating with and consuming the Book Scraper REST API.

## 1. Overview

The REST API serves the enriched book data scraped during Phase 1 & 2. It is built using FastAPI and runs strictly in-memory (no external database required).

- **Base URL (Local)**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)

## 2. Authentication

All endpoints (except health check and docs) require an API Key to prevent unauthorized access.

- **Header Key**: `X-API-Key`
- **Header Value**: The secret string defined in your `.env` file under `API_KEY`.

**Example:**
```http
GET /books HTTP/1.1
Host: localhost:8000
X-API-Key: your-secret-api-key
```

## 3. Rate Limiting

To protect the server from abuse, rate limiting is strictly enforced via `slowapi`.
- **Global Limit**: `10 requests per minute` per client IP address.
- **Behavior on limit hit**: Returns HTTP `429 Too Many Requests`.

## 4. Endpoints

### 4.1 Health Check
Verify that the API server is up and running.

- **URL**: `/`
- **Method**: `GET`
- **Auth Required**: No

**Response (200 OK):**
```json
{
  "status": "online",
  "message": "Welcome to the Book Scraper API"
}
```

### 4.2 Fetch Books
Retrieve the list of scraped books. Supports pagination and filtering.

- **URL**: `/books`
- **Method**: `GET`
- **Auth Required**: Yes (`X-API-Key`)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | `int` | `1` | The page number to retrieve (must be >= 1) |
| `limit` | `int` | `10` | Number of items per page (max 100) |
| `min_rating` | `int` | `None`| Filter books with a star rating greater than or equal to this value (1-5) |
| `country` | `str` | `None`| Filter books exactly matching this publisher country |

**Example Request:**
```bash
curl -X GET "http://localhost:8000/books?page=1&limit=5&min_rating=5" -H "X-API-Key: your-secret-api-key"
```

**Response (200 OK):**
```json
{
  "page": 1,
  "limit": 5,
  "total": 12,
  "data": [
    {
      "title": "Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)",
      "price": 52.29,
      "availability": "In stock",
      "product_url": "https://...",
      "star_rating": 5,
      "country": "Croatia"
    }
  ]
}
```

## 5. Standard Error Codes

The API will return the following HTTP status codes when errors occur:

| HTTP Status | Meaning | Reason / Action Required |
|-------------|---------|--------------------------|
| `401` | Unauthorized | Missing or invalid `X-API-Key` header. Ensure your key matches the `.env` file. |
| `422` | Unprocessable Entity | Invalid query parameters (e.g., negative page number, rating > 5). Check the response body for validation details. |
| `429` | Too Many Requests | Rate limit exceeded (10 req/min). Wait 60 seconds before retrying. |
| `500` | Internal Server Error | Unexpected server crash or missing `data/books.json` file. |
