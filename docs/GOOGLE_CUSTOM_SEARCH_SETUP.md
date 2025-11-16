# Google Custom Search API Setup Guide

This guide will help you set up Google Custom Search API for SERP analysis and keyword ranking tracking.

## Overview

Google Custom Search API allows you to:
- Get real Google search results
- Track keyword rankings
- Analyze SERP features
- Compare competitor rankings
- **100 queries per day FREE** (then paid)

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable billing (required, but free tier available)

## Step 2: Enable Custom Search API

1. In Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Custom Search API"
3. Click **Enable**

## Step 3: Create API Key

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **API Key**
3. Copy your API key
4. (Optional) Restrict the API key to "Custom Search API" for security

## Step 4: Create Custom Search Engine

1. Go to [Google Custom Search](https://programmablesearchengine.google.com/)
2. Click **Add** to create a new search engine
3. Enter:
   - **Sites to search**: `*` (to search entire web)
   - **Name**: Your search engine name
4. Click **Create**
5. Go to **Setup** > **Basics**
6. Copy your **Search Engine ID** (CX)

## Step 5: Configure in Application

1. Copy `configs/api_keys.json.example` to `configs/api_keys.json`:
   ```bash
   cp configs/api_keys.json.example configs/api_keys.json
   ```

2. Edit `configs/api_keys.json`:
   ```json
   {
     "google_pagespeed_api_key": "YOUR_PAGESPEED_KEY",
     "google_custom_search": {
       "api_key": "YOUR_API_KEY_HERE",
       "search_engine_id": "YOUR_SEARCH_ENGINE_ID_CX"
     }
   }
   ```

3. Replace:
   - `YOUR_API_KEY_HERE` with your API key from Step 3
   - `YOUR_SEARCH_ENGINE_ID_CX` with your Search Engine ID from Step 4

## Step 6: Test Configuration

1. Restart your application
2. Go to `/google-search/` in your dashboard
3. You should see "✓ API Configured" message
4. Try a test search

## Features

### 1. Google Search
- Perform real Google searches
- Get up to 10 results per query
- Filter by country and language
- Optionally restrict to specific site

### 2. Find Keyword Rank
- Find your URL's position for a keyword
- Automatically saves to Rank Tracker
- Checks up to 10 pages (100 results)

### 3. SERP Features Analysis
- Analyze SERP features for queries
- Identify organic results count

### 4. Compare Competitors
- Compare multiple competitor URLs
- See who ranks for specific keywords
- Track competitor positions

## Pricing

- **Free Tier**: 100 queries per day
- **Paid**: $5 per 1,000 additional queries

## Daily Limit Management

The application tracks daily query usage:
- Shows remaining queries in UI
- Resets at midnight (server time)
- Displays warning when limit reached

## Integration with Rank Tracker

When you find a keyword rank, it's automatically saved to Rank Tracker module, allowing you to:
- Track ranking changes over time
- View historical data
- Monitor keyword performance

## Troubleshooting

### "API Not Configured" Error
- Check that `configs/api_keys.json` exists
- Verify API key and Search Engine ID are correct
- Restart application after configuration

### "Daily query limit reached" Error
- Wait until next day (resets at midnight)
- Or upgrade to paid plan for more queries

### "API request failed" Error
- Check API key is valid
- Verify Custom Search API is enabled
- Check billing is enabled in Google Cloud

## Security Notes

- Never commit `configs/api_keys.json` to Git
- Restrict API key in Google Cloud Console
- Use environment variables for production (optional)

## Next Steps

After setup:
1. Test with a simple search
2. Find rank for your main keywords
3. Set up competitor monitoring
4. Integrate with Rank Tracker for long-term tracking

