# Google Search Console - Admin Setup Guide

## Overview

This feature allows administrators to upload Google OAuth credentials through a user-friendly web interface, without needing terminal/SSH access.

## Features

✅ **Web-based Upload**: Simple drag-and-drop interface for uploading `google_oauth_client.json`  
✅ **Automatic Validation**: Validates JSON structure and required OAuth fields  
✅ **Auto Restart**: Automatically restarts the application service after upload  
✅ **Admin Only**: Restricted to admin users for security  
✅ **Status Display**: Shows current configuration status  
✅ **File Security**: Automatically sets correct file permissions (600)  

## Access

**URL:** `http://seoanalyze.shahinvaseghi.ir/search-console/admin/setup`

**Requirements:**
- Must be logged in as admin user
- OAuth credentials file from Google Cloud Console

## How It Works

### Step 1: Get OAuth Credentials

1. Follow the complete guide at `/search-console/help`
2. Download `google_oauth_client.json` from Google Cloud Console

### Step 2: Upload via Web Interface

1. Login as admin
2. Go to Dashboard → "⚙️ GSC Admin Setup (Upload OAuth)"
3. Drag and drop the JSON file or click to browse
4. Click "آپلود و راه‌اندازی سرویس" (Upload and Start Service)
5. Wait for confirmation (5 seconds)
6. Service automatically restarts

### Step 3: Verify

1. Go to Google Search Console page
2. Click "Connect Google Search Console"
3. Complete OAuth flow

## File Validation

The system validates:
- ✅ File is valid JSON
- ✅ Contains `web` key
- ✅ Has all required OAuth fields:
  - `client_id`
  - `client_secret`
  - `redirect_uris`
  - `auth_uri`
  - `token_uri`

## Security

1. **Admin Only**: Only users with admin role can access
2. **File Permissions**: Automatically set to `600` (owner read/write only)
3. **Location**: Stored in `configs/google_oauth_client.json`
4. **Git Ignored**: Already in `.gitignore` to prevent commits
5. **No Password Required**: Sudoers configured for passwordless restart

## Sudoers Configuration

The following sudoers file has been configured:

```
# /etc/sudoers.d/seoanalyze
shahin ALL=(ALL) NOPASSWD: /bin/systemctl restart seoanalyzepro
shahin ALL=(ALL) NOPASSWD: /bin/systemctl start seoanalyzepro
shahin ALL=(ALL) NOPASSWD: /bin/systemctl stop seoanalyzepro
shahin ALL=(ALL) NOPASSWD: /bin/systemctl status seoanalyzepro
```

This allows the application to restart the service without password prompt.

## Troubleshooting

### "Admin access required" Error

**Problem:** User is not logged in as admin.

**Solution:**
1. Login with admin account
2. Default admin: `admin` / `admin123`
3. Or promote user to admin via Users page

### "Invalid OAuth credentials file structure"

**Problem:** JSON file doesn't have correct structure.

**Solution:**
1. Make sure you downloaded the file from Google Cloud Console
2. File should start with `{"web": {...}}`
3. Don't edit the file manually

### Service Restart Failed

**Problem:** Sudoers not configured or systemd service name wrong.

**Solution:**
1. Check sudoers: `sudo cat /etc/sudoers.d/seoanalyze`
2. Test manually: `sudo -n systemctl restart seoanalyzepro`
3. Check service name: `systemctl list-units | grep seo`

### Upload Successful but Can't Connect

**Problem:** OAuth redirect URIs might not be configured correctly in Google Cloud Console.

**Solution:**
1. Go to Google Cloud Console → Credentials
2. Edit OAuth 2.0 Client ID
3. Make sure redirect URI is exactly:
   ```
   http://seoanalyze.shahinvaseghi.ir/search-console/oauth2callback
   ```
4. No trailing slash!

## Alternative: Manual Upload via Terminal

If web upload doesn't work, you can still upload manually:

```bash
# Upload via SCP
scp ~/Downloads/google_oauth_client.json shahin@seoanalyze.shahinvaseghi.ir:/home/shahin/seoanalyzepro/configs/

# SSH to server
ssh shahin@seoanalyze.shahinvaseghi.ir

# Set permissions
cd /home/shahin/seoanalyzepro/configs
chmod 600 google_oauth_client.json

# Restart service
sudo systemctl restart seoanalyzepro
```

## Technical Details

### File Upload Process

1. Frontend: `gsc_admin_setup.html` with drag-and-drop
2. Backend: `/search-console/admin/upload-credentials` endpoint
3. Validation: JSON structure and OAuth fields
4. Storage: `configs/google_oauth_client.json` with 600 permissions
5. Restart: `subprocess.run(['sudo', 'systemctl', 'restart', 'seoanalyzepro'])`

### Routes

- **`GET /search-console/admin/setup`**: Admin upload page
- **`POST /search-console/admin/upload-credentials`**: File upload API

### Decorators

- `@admin_required`: Ensures only admin users can access
- `@login_required`: Ensures user is authenticated

## Benefits for Non-Technical Users

❌ **Before**: Required SSH access, terminal commands, file permissions knowledge  
✅ **After**: Simple web interface, drag-and-drop, automatic everything

## Related Documentation

- Complete Setup Guide: `docs/GOOGLE_SEARCH_CONSOLE_SETUP.md`
- In-App Guide: `/search-console/help` (Persian & English)
- Main README: `README.md`

