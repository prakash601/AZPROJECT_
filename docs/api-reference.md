# API Reference

Complete reference for the Problem Finder REST API.

## Base URL

```
Production: https://<your-deploy>.onrender.com
Local:      http://localhost:8000
```

Interactive docs: `/docs` (Swagger UI) | `/redoc` (ReDoc)

---

## Endpoints

### GET /api/health

Liveness check. Returns 200 when the service is running.

**Request:** No parameters

**Response:**
```json
{
  "status": "ok"
}
```

---

### GET /api/search

Hybrid search combining semantic, keyword, and fuzzy matching via RRF.

**Query Parameters:**

| Parameter | Type    | Required | Default | Constraints        | Description                    |
|-----------|---------|----------|---------|--------------------|---------------------------------|
| `q`       | string  | Yes      | —       | min_length=1       | Search query                    |
| `limit`   | integer | No       | 30      | 1 ≤ limit ≤ 100    | Maximum results to return       |
| `offset`  | integer | No       | 0       | offset ≥ 0         | Pagination offset               |

**Response:**

```json
{
  "query": "two sum",
  "corrected_query": null,
  "execution_time_ms": 45,
  "count": 30,
  "results": [
    {
      "id": 1,
      "platform": "LeetCode",
      "title": "Two Sum",
      "url": "https://leetcode.com/problems/two-sum/",
      "description": "Given an array of integers nums and an integer target...",
      "difficulty": "Easy",
      "tags": ["Array", "Hash Table"],
      "score": 0.234
    }
  ]
}
```

**Fields:**

| Field             | Type     | Description                                              |
|-------------------|----------|----------------------------------------------------------|
| `query`           | string   | Original query as submitted                              |
| `corrected_query` | string?  | Spell-corrected query (null if no correction needed)     |
| `execution_time_ms` | integer | Total request processing time in milliseconds          |
| `count`           | integer  | Number of results returned                               |
| `results`         | array    | Ranked search results                                    |
| `results[].id`    | integer  | Problem ID (database primary key)                        |
| `results[].platform` | string | Source platform (e.g., "LeetCode", "HackerRank")       |
| `results[].title` | string   | Problem title                                            |
| `results[].url`   | string   | Link to the original problem                             |
| `results[].description` | string | Problem description/summary                       |
| `results[].difficulty` | string? | Difficulty level (e.g., "Easy", "Medium", "Hard") |
| `results[].tags`  | string[] | Topic tags                                               |
| `results[].score` | float    | RRF relevance score (higher = more relevant)             |

---

### GET /api/autocomplete

Fast type-ahead suggestions using prefix + trigram matching.

**Query Parameters:**

| Parameter | Type    | Required | Default | Constraints      | Description                    |
|-----------|---------|----------|---------|------------------|---------------------------------|
| `prefix`  | string  | Yes      | —       | min_length=1     | Partial title to complete       |
| `limit`   | integer | No       | 10      | 1 ≤ limit ≤ 50   | Maximum suggestions             |

**Response:**

```json
{
  "prefix": "two",
  "suggestions": [
    {
      "id": 1,
      "title": "Two Sum",
      "url": "https://leetcode.com/problems/two-sum/",
      "platform": "LeetCode"
    }
  ]
}
```

**Fields:**

| Field                       | Type     | Description                    |
|-----------------------------|----------|--------------------------------|
| `prefix`                    | string   | Original prefix as submitted   |
| `suggestions`               | array    | Matching suggestions           |
| `suggestions[].id`          | integer  | Problem ID                     |
| `suggestions[].title`       | string   | Problem title                  |
| `suggestions[].url`         | string   | Link to the original problem   |
| `suggestions[].platform`    | string   | Source platform                |

---

## Example Requests

### Basic Search

```bash
curl "http://localhost:8000/api/search?q=reverse+linked+list"
```

### Paginated Search

```bash
curl "http://localhost:8000/api/search?q=dynamic+programming&limit=20&offset=20"
```

### Typo-Tolerant Search (spell correction)

```bash
curl "http://localhost:8000/api/search?q=binry+serch+trees"
```

Response includes `corrected_query: "binary search trees"`.

### Autocomplete

```bash
curl "http://localhost:8000/api/autocomplete?prefix=longest&limit=8"
```

---

## Error Handling

The API uses FastAPI's default validation. Invalid parameters return **422 Unprocessable Entity**:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 100",
      "input": "200"
    }
  ]
}
```

## Rate Limiting & CORS

- CORS is configured for `http://localhost:5173` and the `FRONTEND_ORIGIN` env var
- Only `GET` methods are allowed
- No built-in rate limiting (deploy behind a proxy for production traffic management)
