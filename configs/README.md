# Configuration Files

## API Keys Configuration

### Setup Instructions:

1. **Copy the example file:**
   ```bash
   cp api_keys.json.example api_keys.json
   ```

2. **Edit api_keys.json:**
   - Replace `YOUR_API_KEY_HERE` with your actual Google PageSpeed Insights API key
   - Never commit this file to version control

3. **Get Google PageSpeed Insights API Key:**
   - See: `../docs/GOOGLE_PAGESPEED_API_SETUP.md` for detailed instructions
   - Free tier: 25,000 requests per day

### Alternative: Environment Variable

You can also set the API key as an environment variable:

```bash
export GOOGLE_PAGESPEED_API_KEY="your-api-key-here"
```

Or add to systemd service:
```bash
sudo systemctl edit seoanalyzepro
```

Add:
```ini
[Service]
Environment="GOOGLE_PAGESPEED_API_KEY=your-api-key-here"
```

### Security Notes:

- ✅ `api_keys.json` is in `.gitignore` (not committed)
- ✅ Use environment variables in production
- ✅ Restrict API key to PageSpeed Insights API only
- ✅ Monitor usage in Google Cloud Console

### Without API Key:

The system will fallback to static analysis (less accurate but still functional).

