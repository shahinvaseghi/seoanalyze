API (Current and Planned)
=========================

Current Endpoints
-----------------

### Authentication & Core
- `GET /health` → "ok"
- `GET /login` → renders login page
- `POST /login` → authenticates form credentials
- `GET /logout` → clears session and redirects to `/login`
- `GET /` → redirects to `/dashboard` or `/login`
- `GET /dashboard` → protected page

### User Management (Admin Only)
- `GET /users/` → admin-only users list
- `GET|POST /users/create` → admin-only create user
- `GET|POST /users/<username>/edit` → admin-only edit user
- `POST /users/<username>/delete` → admin-only delete user

### Google Search Console
- `GET /search-console/` → Search Console dashboard (requires connection)
- `GET /search-console/connect` → Initiate OAuth flow
- `GET /search-console/oauth2callback` → OAuth callback handler
- `POST /search-console/disconnect` → Disconnect GSC account
- `POST /search-console/api/analytics` → Get analytics data
  - **Request Body:**
    ```json
    {
      "site_url": "https://example.com",
      "days": 7,
      "limit": 25000
    }
    ```
  - **Response:**
    ```json
    {
      "success": true,
      "summary": {
        "total_impressions": 12345,
        "total_clicks": 567,
        "average_ctr": 4.59,
        "average_position": 6.2
      },
      "top_queries": [...],
      "top_pages": [...]
    }
    ```
- `GET /search-console/api/properties` → Get user's Search Console properties
- `GET /search-console/help` → Help page (Persian & English)
- `GET /search-console/admin/setup` → Admin OAuth credentials upload page
- `POST /search-console/admin/upload-credentials` → Upload OAuth credentials (Admin only)

### Google Search Console Reports
- `GET /search-console/reports/` → GSC Reports dashboard
- `POST /search-console/reports/generate` → Generate comprehensive analytics reports
  - **Request Body:**
    ```json
    {
      "site_url": "sc-domain:example.com",
      "days": 30
    }
    ```
  - **Response:**
    ```json
    {
      "success": true,
      "period": "2025-10-17 to 2025-11-16",
      "avg_position_change": -0.5,
      "reports": {
        "high_impressions_low_clicks": [...],
        "high_impressions_zero_clicks": [...],
        "clicks_decreased_25pct": [...],
        "highest_clicks": [...],
        "lowest_impressions_clicks": [...],
        "highest_ctr": [...],
        "lowest_ctr": [...],
        "zero_clicks_low_ctr": [...],
        "clicks_high_position": [...]
      }
    }
    ```
- `POST /search-console/reports/internal-links` → Analyze internal links structure
  - **Request Body:**
    ```json
    {
      "site_url": "sc-domain:example.com",
      "days": 30,
      "limit": 50
    }
    ```
  - **Response:**
    ```json
    {
      "success": true,
      "highest_internal_links": [...],
      "lowest_internal_links": [...],
      "total_pages_analyzed": 50
    }
    ```
- `POST /search-console/reports/pages-by-query` → Search pages by specific query
  - **Request Body:**
    ```json
    {
      "site_url": "sc-domain:example.com",
      "query": "seo tools",
      "days": 30
    }
    ```
  - **Response:**
    ```json
    {
      "success": true,
      "query": "seo tools",
      "exact": {
        "total": 15,
        "top5": [...],
        "bottom5": [...]
      },
      "contain": {
        "total": 8,
        "top5": [...],
        "bottom5": [...]
      }
    }
    ```

Authentication
--------------
- Session cookie-based; login sets `session['user']`.
- Add CSRF and rate-limits in a future version.

Planned Endpoints (MVP+)
------------------------
- `/api/analyze/competitors` (POST)
- `/api/analyze/keyword` (POST)
- `/api/analyze/gap` (POST)
- `/api/status` (GET)
- `/api/results` (GET)

Notes
-----
- Prefer Blueprints per domain and JSON responses for API routes.
- Add OpenAPI schema once API stabilizes.


