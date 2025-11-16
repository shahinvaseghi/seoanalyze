# Google PageSpeed Insights API Setup Guide

## 📋 Overview

This guide will help you set up Google PageSpeed Insights API to get real Core Web Vitals metrics for your website analysis.

## 🔑 Step 1: Get API Key (Free)

### Method 1: Google Cloud Console

1. **Go to Google Cloud Console**:
   - Visit: https://console.cloud.google.com/

2. **Create or Select a Project**:
   - Click on the project dropdown (top bar)
   - Click "New Project"
   - Name it: "SEO Analyze Pro"
   - Click "Create"

3. **Enable PageSpeed Insights API**:
   - Go to: https://console.cloud.google.com/apis/library
   - Search for: "PageSpeed Insights API"
   - Click on it
   - Click "Enable"

4. **Create API Key**:
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click "Create Credentials" → "API Key"
   - Copy the API Key (e.g., `AIzaSyBXXXXXXXXXXXXXXXXXXXXXXXX`)

5. **Restrict API Key (Recommended)**:
   - Click on your API key
   - Under "API restrictions":
     - Select "Restrict key"
     - Check "PageSpeed Insights API"
   - Click "Save"

### Method 2: Direct Link

Simply visit: https://developers.google.com/speed/docs/insights/v5/get-started

## 🔧 Step 2: Configure API Key

### Option A: Environment Variable (Recommended for Production)

```bash
# Add to your .bashrc or .zshrc
export GOOGLE_PAGESPEED_API_KEY="YOUR_API_KEY_HERE"

# Or for systemd service
sudo systemctl edit seoanalyzepro
```

Add this line:
```ini
[Service]
Environment="GOOGLE_PAGESPEED_API_KEY=YOUR_API_KEY_HERE"
```

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart seoanalyzepro
```

### Option B: Config File (Development)

Create file: `/home/shahin/seoanalyzepro/configs/api_keys.json`

```json
{
  "google_pagespeed_api_key": "YOUR_API_KEY_HERE"
}
```

**Note**: Add this file to `.gitignore` to avoid committing secrets!

### Option C: Direct in Code (Not Recommended)

Only for testing purposes.

## 📊 Step 3: Test API Key

```bash
curl "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://example.com&key=YOUR_API_KEY"
```

If successful, you'll get JSON response with Core Web Vitals data.

## 💰 Pricing & Limits

### Free Tier:
- ✅ **25,000 requests per day** - FREE
- ✅ No credit card required
- ✅ Sufficient for most use cases

### Rate Limits:
- **Quota**: 25,000 queries per day
- **Per-second limit**: ~1-2 requests per second
- **Per-user limit**: 100 requests per 100 seconds

## 🎯 API Response Format

```json
{
  "loadingExperience": {
    "metrics": {
      "LARGEST_CONTENTFUL_PAINT_MS": {
        "percentile": 2500,
        "category": "AVERAGE"
      },
      "CUMULATIVE_LAYOUT_SHIFT_SCORE": {
        "percentile": 0.05,
        "category": "FAST"
      },
      "INTERACTION_TO_NEXT_PAINT": {
        "percentile": 180,
        "category": "FAST"
      }
    },
    "overall_category": "AVERAGE"
  },
  "lighthouseResult": {
    "audits": {
      "first-contentful-paint": {
        "displayValue": "1.5 s"
      },
      "largest-contentful-paint": {
        "displayValue": "2.3 s"
      },
      "cumulative-layout-shift": {
        "displayValue": "0.08"
      }
    },
    "categories": {
      "performance": {
        "score": 0.85
      }
    }
  }
}
```

## ⚡ Available Metrics

### Core Web Vitals (Field Data - Real Users):
- **LCP** - Largest Contentful Paint
- **INP** - Interaction to Next Paint  
- **CLS** - Cumulative Layout Shift

### Lab Data (Lighthouse):
- **FCP** - First Contentful Paint
- **TTI** - Time to Interactive
- **TBT** - Total Blocking Time
- **Speed Index**

### Performance Score:
- Overall Performance (0-100)
- Accessibility Score
- Best Practices Score
- SEO Score

## 🔄 Fallback Strategy

The system uses a three-tier approach:

1. **Primary**: Google PageSpeed Insights API (real data)
2. **Secondary**: Static analysis with better algorithms
3. **Tertiary**: Basic estimation

## 🛡️ Security Best Practices

1. ✅ **Never commit API keys** to version control
2. ✅ **Use environment variables** in production
3. ✅ **Restrict API key** to specific APIs
4. ✅ **Monitor usage** in Google Cloud Console
5. ✅ **Rotate keys** periodically

## 📚 Additional Resources

- **API Documentation**: https://developers.google.com/speed/docs/insights/v5/reference
- **Web Vitals Guide**: https://web.dev/vitals/
- **Google Cloud Console**: https://console.cloud.google.com/

## ⚠️ Troubleshooting

### "API key not valid"
- Check if API is enabled in Google Cloud Console
- Verify API key is correct
- Check API restrictions

### "Quota exceeded"
- You've hit the 25,000 daily limit
- Wait 24 hours or upgrade quota
- System will fallback to static analysis

### "Invalid URL"
- URL must be publicly accessible
- Use full URL with https://
- Check if website is online

---

**Last Updated**: October 27, 2025  
**API Version**: v5  
**Status**: Production Ready

