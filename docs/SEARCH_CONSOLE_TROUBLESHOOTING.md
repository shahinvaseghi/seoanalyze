# Google Search Console - Troubleshooting Guide

## Overview

This guide covers common issues with Google Search Console integration and their solutions.

## OAuth Connection Issues

### Problem: State Mismatch Error

**Symptoms:**
```
❌ State mismatch!
Session state: nAwquQMC9O8FqRMd0a7i...
Request state: FyHigQTmrj2ZonbSWtZf...
```

**Causes:**
1. **Multiple simultaneous connect requests**: Clicking "Connect" multiple times quickly
2. **Session issues with multiple Gunicorn workers**: Different workers handling requests
3. **Session expiry**: State token expired before OAuth callback
4. **Browser refresh**: Page refresh during OAuth flow

**Solutions:**

#### Solution 1: Wait and Retry
1. Clear the OAuth state by refreshing the page
2. Wait a few seconds
3. Click "Connect" **only once** and wait
4. Complete the Google OAuth flow without refreshing

#### Solution 2: Check Session Configuration
```bash
# Verify SECRET_KEY is set
sudo systemctl cat seoanalyzepro | grep SECRET_KEY

# Check session configuration
grep -A 5 "SESSION" app/web/app.py
```

#### Solution 3: Check for Multiple Workers
```bash
# Check worker count
sudo systemctl cat seoanalyzepro | grep "gunicorn.*-w"

# If using multiple workers, session should work with signed cookies
# Verify SECRET_KEY is consistent across workers
```

#### Solution 4: Review Logs
```bash
# Check OAuth logs
sudo journalctl -u seoanalyzepro --since "5 minutes ago" | grep -E "(OAuth|state|redirect)"

# Look for patterns:
# - Multiple "Generated redirect" in same second = double-click
# - Different worker PIDs = session cross-worker issue
```

### Problem: OAuth Flow Already in Progress

**Symptoms:**
- Flash message: "OAuth flow already in progress. Please wait or try again in a moment."
- Can't start new connection

**Solution:**
1. Wait 30 seconds
2. Refresh the page
3. Try connecting again

**Prevention:**
- Click "Connect" only once
- Don't refresh during OAuth flow
- Wait for redirect from Google

### Problem: Redirect URI Mismatch

**Symptoms:**
```
Error 400: redirect_uri_mismatch
```

**Solutions:**
1. **Verify redirect URI in Google Cloud Console:**
   - Go to: Google Cloud Console → APIs & Services → Credentials
   - Edit your OAuth 2.0 Client ID
   - Check "Authorized redirect URIs" contains exactly:
     ```
     https://seoanalyze.shahinvaseghi.ir/search-console/oauth2callback
     ```
   - **Important**: No trailing slash!

2. **Verify redirect_uris in config file:**
   ```bash
   cat configs/google_oauth_client.json | grep -A 5 redirect_uris
   ```

3. **Match with actual request:**
   ```bash
   # Check logs for actual redirect_uri used
   sudo journalctl -u seoanalyzepro | grep "Generated redirect_uri"
   ```

### Problem: Invalid Client Secret

**Symptoms:**
```
Error: Invalid client secret
```

**Solutions:**
1. Download fresh credentials from Google Cloud Console
2. Replace `configs/google_oauth_client.json`
3. Set permissions: `chmod 600 configs/google_oauth_client.json`
4. Restart service: `sudo systemctl restart seoanalyzepro`

## Data Display Issues

### Problem: Data Doesn't Match Google Search Console

**Symptoms:**
- Numbers in application differ from Google Search Console UI
- Impressions/Clicks mismatch

**Causes:**
1. **Data delay**: GSC has 1-2 day delay
2. **Date range mismatch**: Different timezone or date calculation
3. **API aggregation**: Different calculation methods

**Solutions:**

#### Solution 1: Check Date Range
- Application shows data up to **yesterday** (GSC has 1-2 day delay)
- Google Search Console UI may show today's partial data
- Use same date range in both: "Last 7 days"

#### Solution 2: Verify API Response
```bash
# Check logs for API calls
sudo journalctl -u seoanalyzepro | grep -E "(total_impressions|total_clicks|start_date|end_date)"
```

#### Solution 3: Data Refresh Timing
- GSC API data is typically 24-48 hours behind
- Wait 24 hours and compare again
- Both should show same historical data

### Problem: No Data Showing

**Symptoms:**
- Connected successfully
- Properties list shows
- But "Load Analytics" shows no data

**Solutions:**

1. **Check Property URL Format:**
   - Verify property URL matches exactly (with or without trailing slash)
   - Example: `https://example.com` vs `sc-domain:example.com`

2. **Check Date Range:**
   - Try different ranges: 7 days, 30 days, 90 days
   - Some properties may not have recent data

3. **Verify Permissions:**
   - User must have "Full" or "Restricted" access to property
   - Check in Google Search Console → Settings → Users and permissions

4. **Check API Logs:**
   ```bash
   sudo journalctl -u seoanalyzepro | grep -E "(Error|Failed|insufficient)"
   ```

### Problem: Incomplete Query/Page Lists

**Symptoms:**
- Only showing 20 results
- Want to see all results

**Solution:**
- Click "Show All" button above the table
- This expands the collapsible list to show all results (up to 500)

## Session Issues

### Problem: Session Lost After OAuth Redirect

**Symptoms:**
- Redirected to login page after OAuth callback
- OAuth flow completes but session is lost

**Solutions:**

1. **Check Session Configuration:**
   ```python
   # app/web/app.py should have:
   app.config['SESSION_COOKIE_SECURE'] = True  # for HTTPS
   app.config['SESSION_COOKIE_HTTPONLY'] = True
   app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
   ```

2. **Verify SECRET_KEY:**
   ```bash
   # SECRET_KEY must be set and consistent
   sudo systemctl cat seoanalyzepro | grep SECRET_KEY
   ```

3. **Check Cookie Settings:**
   - Ensure HTTPS is used (not HTTP)
   - Check browser console for cookie errors
   - Verify SameSite cookie policy

## Performance Issues

### Problem: Slow Data Loading

**Symptoms:**
- "Load Analytics" takes too long
- Timeout errors

**Solutions:**

1. **Reduce Data Range:**
   - Use 7 days instead of 90 days
   - Less data = faster response

2. **Check API Limits:**
   - Google Search Console API has rate limits
   - Wait 1 minute between requests if hitting limits

3. **Check Server Resources:**
   ```bash
   # Monitor CPU/Memory during load
   htop
   
   # Check service logs
   sudo journalctl -u seoanalyzepro -f
   ```

### Problem: Too Many Results

**Symptoms:**
- Application slow with many queries/pages
- Browser becomes unresponsive

**Solutions:**

1. **Use Collapsible Lists:**
   - Lists show 20 items by default
   - Click "Show All" only when needed

2. **Filter in Google Search Console:**
   - Use filters in GSC before connecting
   - Only connect properties you need

## Connection Management

### Problem: Can't Disconnect

**Symptoms:**
- Disconnect button doesn't work
- Still shows as connected

**Solutions:**

1. **Check User Storage:**
   ```bash
   # Verify user data
   cat app/users.json | jq '.users.YOUR_USERNAME.gsc_tokens'
   ```

2. **Manual Disconnect:**
   ```bash
   # Edit users.json manually (backup first!)
   # Remove "gsc_tokens" key for user
   ```

3. **Reconnect:**
   - If disconnect fails, try reconnecting
   - New connection will replace old tokens

### Problem: Multiple OAuth Flows

**Symptoms:**
- Warning: "OAuth flow already in progress"

**Solutions:**

1. **Wait and Retry:**
   - Wait 30 seconds
   - Refresh page
   - Try again

2. **Clear Session:**
   - Logout and login again
   - This clears OAuth state from session

## Debugging Commands

### Check OAuth State
```bash
# View OAuth-related logs
sudo journalctl -u seoanalyzepro --since "10 minutes ago" | \
  grep -E "(OAuth|state|redirect|callback|Generated)"
```

### Check API Calls
```bash
# View Search Console API calls
sudo journalctl -u seoanalyzepro | \
  grep -E "(searchanalytics|get_performance|get_top_queries)"
```

### Check Session
```bash
# View session-related logs
sudo journalctl -u seoanalyzepro | \
  grep -E "(session|oauth_state|oauth_username)"
```

### Verify Credentials
```bash
# Check OAuth credentials file
cat configs/google_oauth_client.json | jq '.web.client_id'

# Verify file permissions
ls -la configs/google_oauth_client.json
# Should be: -rw------- (600)
```

### Test API Connection
```python
# Test API manually
python3 -c "
from app.services.gsc_oauth import GSCOAuthHandler
handler = GSCOAuthHandler()
print('✅ OAuth handler initialized')
"
```

## Common Error Messages

### "State mismatch!"
- **Fix**: Don't click Connect multiple times, wait for redirect

### "OAuth flow already in progress"
- **Fix**: Wait 30 seconds and refresh page

### "No authorization code received"
- **Fix**: User cancelled OAuth or error from Google

### "Session expired. Please try connecting again"
- **Fix**: Session timeout, reconnect (sessions last 4 hours)

### "Insufficient permissions for this property"
- **Fix**: User needs Full or Restricted access in GSC

### "Property not found or invalid"
- **Fix**: Verify property URL format and access

## Getting More Help

1. **Check Application Logs:**
   ```bash
   sudo journalctl -u seoanalyzepro -f
   ```

2. **Check Browser Console:**
   - Open Developer Tools (F12)
   - Check Console for JavaScript errors
   - Check Network tab for API errors

3. **Review Documentation:**
   - `docs/GOOGLE_SEARCH_CONSOLE_SETUP.md` - Setup guide
   - `docs/GSC_ADMIN_SETUP.md` - Admin setup
   - `/search-console/help` - In-app help (Persian & English)

4. **Google Resources:**
   - [Search Console API Documentation](https://developers.google.com/webmaster-tools/search-console-api-original/v3/)
   - [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)

## Prevention Tips

1. **Single Click**: Always click "Connect" only once
2. **Wait for Redirect**: Don't refresh during OAuth flow
3. **Stable Connection**: Ensure stable internet during OAuth
4. **Regular Updates**: Keep credentials file up to date
5. **Monitor Logs**: Regularly check logs for errors
6. **Test Regularly**: Test connection after server restarts

