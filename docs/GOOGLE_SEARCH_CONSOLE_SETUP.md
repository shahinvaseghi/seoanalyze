# Google Search Console Integration Setup

## Overview

This guide will help you set up OAuth 2.0 authentication for Google Search Console API integration. Each user will be able to connect their own Google Search Console account securely.

## Prerequisites

- Google Cloud Platform account
- Access to Google Search Console for your website
- Your domain must be verified in Google Search Console

---

## Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/

2. **Create a New Project:**
   - Click "Select a project" at the top
   - Click "New Project"
   - Enter project name: `SEO Analyze Pro` (or any name you prefer)
   - Click "Create"

3. **Select Your Project:**
   - Make sure your new project is selected in the top bar

---

## Step 2: Enable Google Search Console API

1. **Go to APIs & Services:**
   - In the left sidebar, click "APIs & Services" → "Library"

2. **Search for Search Console API:**
   - In the search box, type: `Search Console API`
   - Click on "Google Search Console API"

3. **Enable the API:**
   - Click the "Enable" button
   - Wait for it to be enabled (usually takes a few seconds)

---

## Step 3: Configure OAuth Consent Screen

1. **Go to OAuth Consent Screen:**
   - Left sidebar: "APIs & Services" → "OAuth consent screen"

2. **Choose User Type:**
   - Select "External" (unless you have a Google Workspace account)
   - Click "Create"

3. **Fill App Information:**
   - **App name:** `SEO Analyze Pro`
   - **User support email:** Your email address
   - **App logo:** (Optional) Upload your logo
   - **App domain:** (Optional)
   - **Authorized domains:** Add your domain (e.g., `shahinvaseghi.ir`)
   - **Developer contact information:** Your email address
   - Click "Save and Continue"

4. **Scopes:**
   - Click "Add or Remove Scopes"
   - Search for: `Google Search Console API`
   - Select: `https://www.googleapis.com/auth/webmasters.readonly`
   - Click "Update"
   - Click "Save and Continue"

5. **Test Users:**
   - Click "Add Users"
   - Add your email address and any other test users
   - Click "Save and Continue"

6. **Summary:**
   - Review your settings
   - Click "Back to Dashboard"

---

## Step 4: Create OAuth 2.0 Credentials

1. **Go to Credentials:**
   - Left sidebar: "APIs & Services" → "Credentials"

2. **Create Credentials:**
   - Click "Create Credentials" → "OAuth client ID"

3. **Configure OAuth Client:**
   - **Application type:** Web application
   - **Name:** `SEO Analyze Pro Web Client`

4. **Authorized JavaScript origins:**
   ```
   http://localhost:5000
   http://seoanalyze.shahinvaseghi.ir
   https://seoanalyze.shahinvaseghi.ir
   ```

5. **Authorized redirect URIs:**
   ```
   http://localhost:5000/search-console/oauth2callback
   http://seoanalyze.shahinvaseghi.ir/search-console/oauth2callback
   https://seoanalyze.shahinvaseghi.ir/search-console/oauth2callback
   ```

6. **Create:**
   - Click "Create"
   - A dialog will show your Client ID and Client Secret
   - Click "Download JSON" to download the credentials file

---

## Step 5: Install Credentials in Application

1. **Rename the Downloaded File:**
   - The file will be named something like: `client_secret_XXXXX.json`
   - Rename it to: `google_oauth_client.json`

2. **Move to Config Directory:**
   ```bash
   cd /home/shahin/seoanalyzepro
   mv ~/Downloads/google_oauth_client.json configs/google_oauth_client.json
   ```

3. **Set Proper Permissions:**
   ```bash
   chmod 600 configs/google_oauth_client.json
   ```

4. **Verify File Format:**
   The file should look like this:
   ```json
   {
     "web": {
       "client_id": "XXXXX.apps.googleusercontent.com",
       "project_id": "your-project-id",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
       "client_secret": "YOUR_SECRET",
       "redirect_uris": [...]
     }
   }
   ```

---

## Step 6: Restart Application

```bash
sudo systemctl restart seoanalyze
```

---

## Step 7: Test OAuth Flow

1. **Login to Application:**
   - Go to: http://seoanalyze.shahinvaseghi.ir/
   - Login with your account

2. **Navigate to Search Console:**
   - Click "Google Search Console" from dashboard

3. **Connect Your Account:**
   - Click "Connect Google Search Console"
   - You'll be redirected to Google
   - Select your Google account
   - Review permissions and click "Allow"
   - You'll be redirected back to the application

4. **Verify Connection:**
   - You should see your Search Console properties listed
   - Select a property and click "Load Analytics"
   - Data should appear

---

## Troubleshooting

### Error: "State mismatch"

**Problem:** The OAuth state token in session doesn't match the state returned from Google.

**Possible Causes:**
- Clicking "Connect" button multiple times
- Session issues with multiple Gunicorn workers
- Browser refresh during OAuth flow

**Solutions:**
1. **Wait and Retry:**
   - Refresh the page
   - Wait a few seconds
   - Click "Connect" **only once** and wait for redirect
   
2. **Check Session Configuration:**
   ```bash
   # Verify SECRET_KEY is set
   sudo systemctl cat seoanalyzepro | grep SECRET_KEY
   
   # Check session cookie settings
   grep -A 3 "SESSION_COOKIE" app/web/app.py
   ```

3. **Review Logs:**
   ```bash
   sudo journalctl -u seoanalyzepro --since "5 minutes ago" | \
     grep -E "(OAuth|state|Generated redirect)"
   ```

**Prevention:**
- Click "Connect" only once
- Don't refresh during OAuth flow
- Ensure stable session configuration

### Error: "OAuth flow already in progress"

**Problem:** An OAuth connection attempt is already in progress.

**Solution:**
1. Wait 30 seconds
2. Refresh the page
3. Try connecting again

### Error: "redirect_uri_mismatch"

**Problem:** The redirect URI in your request doesn't match what's registered in Google Cloud Console.

**Solution:**
1. Go back to Google Cloud Console → Credentials
2. Edit your OAuth 2.0 Client ID
3. Make sure the exact redirect URI is listed:
   ```
   https://seoanalyze.shahinvaseghi.ir/search-console/oauth2callback
   ```
   **Important:** No trailing slash!
4. Save and try again

### Error: "Access blocked: This app's request is invalid"

**Problem:** OAuth consent screen is not properly configured.

**Solution:**
1. Go to OAuth consent screen
2. Make sure "Publishing status" is not "In production" for testing
3. Add your email to "Test users"
4. Try again

### Error: "API has not been enabled"

**Problem:** Search Console API is not enabled for your project.

**Solution:**
1. Go to APIs & Services → Library
2. Search for "Search Console API"
3. Click "Enable"
4. Wait a few minutes and try again

### Error: "Invalid client secret"

**Problem:** The credentials file is incorrect or corrupted.

**Solution:**
1. Download fresh credentials from Google Cloud Console
2. Replace `configs/google_oauth_client.json`
3. Restart application

### No Data Showing

**Problem:** Connected successfully but no data appears.

**Possible causes:**
1. The selected property might not have enough data yet
2. You might not have the correct permissions on that property
3. Try selecting a different time range (7 days, 30 days, etc.)

---

## Security Notes

1. **Never commit credentials to Git:**
   - The `configs/google_oauth_client.json` file is already in `.gitignore`
   - Keep this file secure and private

2. **User tokens are stored separately:**
   - Each user's OAuth tokens are stored in their user data file
   - Users can only access their own Search Console data

3. **Read-only access:**
   - The application only requests read-only access to Search Console
   - It cannot modify any Search Console settings or data

4. **Token refresh:**
   - Access tokens expire after 1 hour
   - The application automatically refreshes them using the refresh token
   - Users don't need to re-authenticate unless they disconnect

---

## What Data Can Users Access?

Once connected, users can view:

- ✅ Search queries and their performance
- ✅ Top landing pages
- ✅ Click-through rates (CTR)
- ✅ Average positions in Google Search
- ✅ Impressions and clicks over time
- ✅ All verified properties in their Search Console account

---

## Need Help?

If you encounter any issues not covered in this guide, check:

1. Google Cloud Console error messages
2. Application logs: `sudo journalctl -u seoanalyze -f`
3. Browser console for JavaScript errors

For Google OAuth specific issues, refer to:
- https://developers.google.com/identity/protocols/oauth2
- https://developers.google.com/webmaster-tools/search-console-api-original/v3/
