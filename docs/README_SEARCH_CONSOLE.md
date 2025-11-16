# Google Search Console Integration - Technical Documentation

## Overview

This document provides technical details about the Google Search Console integration implementation in SEOAnalyzePro.

## Architecture

### Components

1. **OAuth Handler** (`app/services/gsc_oauth.py`)
   - Manages OAuth 2.0 flow
   - Handles token exchange and refresh
   - Provides credential management

2. **GSC Analyzer** (`app/core/gsc_analyzer.py`)
   - Fetches data from Search Console API
   - Processes analytics data
   - Provides aggregated summaries

3. **Routes** (`app/web/search_console.py`)
   - Web interface routes
   - OAuth callback handling
   - API endpoints

4. **Storage** (`app/services/storage.py`)
   - Stores user tokens per user
   - Manages connection state
   - Handles token persistence

## OAuth Flow

### Step-by-Step Process

1. **User Initiates Connection**
   ```
   User clicks "Connect" → GET /search-console/connect
   ```

2. **Generate State Token**
   ```python
   state = secrets.token_urlsafe(32)
   session['oauth_state'] = state
   session['oauth_username'] = username
   ```

3. **Create Authorization URL**
   ```python
   redirect_uri = url_for('search_console.oauth_callback', _external=True)
   authorization_url, _ = oauth_handler.create_authorization_url(redirect_uri, state)
   ```

4. **User Authorizes**
   ```
   Redirect to Google → User clicks "Allow" → Google redirects back
   ```

5. **Verify State**
   ```python
   state_from_session = session.get('oauth_state')
   state_from_request = request.args.get('state')
   if state_from_session != state_from_request:
       # Error: State mismatch
   ```

6. **Exchange Code for Tokens**
   ```python
   tokens = oauth_handler.exchange_code_for_tokens(code, redirect_uri)
   storage.save_gsc_tokens(username, tokens)
   ```

## Data Fetching

### Performance Summary

**Method:** `GSCAnalyzer.get_performance_summary()`

**API Call:**
```python
request_body = {
    'startDate': start_date.isoformat(),
    'endDate': end_date.isoformat(),
    'rowLimit': 1  # No dimensions = aggregated total
}

response = service.searchanalytics().query(
    siteUrl=site_url,
    body=request_body
).execute()
```

**Returns:** Single row with aggregated totals matching GSC UI exactly.

### Top Queries/Pages

**Method:** `GSCAnalyzer.get_top_queries()` / `get_top_pages()`

**API Call:**
```python
request_body = {
    'startDate': start_date.isoformat(),
    'endDate': end_date.isoformat(),
    'dimensions': ['query'],  # or ['page']
    'rowLimit': limit  # Default 500
}
```

**Returns:** List of rows sorted by performance.

## Security Considerations

### State Parameter

- **Purpose**: Prevent CSRF attacks
- **Generation**: Cryptographically secure random token
- **Storage**: Flask session (signed cookie)
- **Validation**: Must match between request and callback

### Session Management

- **Persistence**: `session.permanent = True` (4 hour lifetime)
- **Security**: Secure cookies in production
  ```python
  SESSION_COOKIE_SECURE = True    # HTTPS only
  SESSION_COOKIE_HTTPONLY = True   # No JavaScript access
  SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
  ```

### Token Storage

- **Location**: `app/users.json` under user's data
- **Encryption**: Not encrypted (stored in user's private data)
- **Refresh**: Automatically refreshed when expired
- **Scope**: Read-only access (`webmasters.readonly`)

## API Endpoints

### `/search-console/connect`
- **Method**: GET
- **Auth**: Required
- **Action**: Initiates OAuth flow
- **Protection**: Prevents multiple simultaneous flows

### `/search-console/oauth2callback`
- **Method**: GET
- **Auth**: Not required (session may be lost)
- **Action**: Handles OAuth callback
- **Security**: Validates state parameter

### `/search-console/api/analytics`
- **Method**: POST
- **Auth**: Required
- **Body**:
  ```json
  {
    "site_url": "https://example.com",
    "days": 7,
    "limit": 500
  }
  ```
- **Response**: Analytics data with summary, queries, and pages

## Error Handling

### State Mismatch
```python
if state_from_session != state_from_request:
    # Clear state to allow retry
    session.pop('oauth_state', None)
    session.pop('oauth_username', None)
    flash("Invalid OAuth state...", "error")
    return redirect(url_for('search_console.index'))
```

### API Errors
```python
try:
    response = service.searchanalytics().query(...)
except Exception as e:
    # Parse error message
    if 'insufficient permissions' in error_msg.lower():
        error_msg = "Insufficient permissions..."
    # Return user-friendly message
```

## Data Structure

### Token Storage Format
```json
{
  "users": {
    "username": {
      "gsc_tokens": {
        "access_token": "...",
        "refresh_token": "...",
        "token_uri": "...",
        "client_id": "...",
        "client_secret": "...",
        "scopes": [...],
        "expiry": "2025-11-03T...",
        "created_at": "2025-11-03T...",
        "properties": [...]
      }
    }
  }
}
```

### Analytics Response Format
```json
{
  "success": true,
  "summary": {
    "total_impressions": 12345,
    "total_clicks": 567,
    "average_ctr": 4.59,
    "average_position": 6.2,
    "period": "7 days",
    "start_date": "2025-10-27",
    "end_date": "2025-11-02"
  },
  "top_queries": [
    {
      "query": "example query",
      "impressions": 1234,
      "clicks": 56,
      "ctr": 4.54,
      "position": 5.2
    }
  ],
  "top_pages": [...]
}
```

## Performance Considerations

### API Rate Limits
- Google Search Console API has rate limits
- Application requests up to 500 rows per query
- Should implement caching for frequently accessed data

### Date Range Calculation
```python
end_date = datetime.now().date() - timedelta(days=1)  # GSC has 1-2 day delay
start_date = end_date - timedelta(days=days-1)
```

### Collapsible Lists
- First 20 items shown by default
- Remaining items in hidden `<tbody>` element
- JavaScript toggle function shows/hides

## Testing

### Manual Testing
```bash
# Test OAuth handler
python3 -c "
from app.services.gsc_oauth import GSCOAuthHandler
handler = GSCOAuthHandler()
print('✅ OAuth handler initialized')
"

# Test service endpoint
curl -X POST http://127.0.0.1:5000/search-console/api/analytics \
  -H "Content-Type: application/json" \
  -d '{"site_url":"https://example.com","days":7}'
```

### Log Monitoring
```bash
# Monitor OAuth flow
sudo journalctl -u seoanalyzepro -f | \
  grep -E "(OAuth|state|redirect|callback)"

# Monitor API calls
sudo journalctl -u seoanalyzepro | \
  grep -E "(searchanalytics|get_performance)"
```

## Future Improvements

1. **Caching**: Cache frequently accessed data
2. **Pagination**: Handle more than 500 results
3. **Filters**: Add dimension filters (country, device, etc.)
4. **Export**: Export data to CSV/JSON
5. **Notifications**: Alert on significant changes
6. **Charts**: Visual representation of trends

## Related Documentation

- Setup Guide: `docs/GOOGLE_SEARCH_CONSOLE_SETUP.md`
- Troubleshooting: `docs/SEARCH_CONSOLE_TROUBLESHOOTING.md`
- Admin Setup: `docs/GSC_ADMIN_SETUP.md`
- User Guide: `docs/USER_GUIDE.md`

