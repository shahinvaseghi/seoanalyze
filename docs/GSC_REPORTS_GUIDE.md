# Google Search Console Reports - Complete Guide

## Overview

The GSC Reports module provides advanced analytics and reporting capabilities for Google Search Console data. This module allows you to generate comprehensive reports, analyze page performance, track internal links, and search for pages by specific queries.

## Features

### 1. Comprehensive Analytics Reports
- **Position Changes**: Track average position changes between date ranges
- **High Impressions, Low Clicks**: Identify pages with high visibility but low engagement
- **Zero Click Pages**: Find pages with impressions but no clicks
- **Click Decreases**: Monitor pages with significant click drops (>25%)
- **Top Performers**: Identify best and worst performing pages
- **CTR Analysis**: Find pages with highest and lowest click-through rates

### 2. Internal Links Analysis
- **Highest Internal Links**: Pages with most internal links
- **Lowest Internal Links**: Pages that need more internal linking
- Automatic page scraping to count internal links

### 3. Query-Based Page Search
- **Exact Match**: Pages that rank for exact query
- **Contain Match**: Pages where URL contains the query
- Top 5 and Bottom 5 results for each category

## Accessing the Reports Module

1. **Navigate to Dashboard**
   - Log in to your account
   - Click on "📈 گزارشات سرچ کنسول (GSC Reports)" from the dashboard

2. **Prerequisites**
   - You must have connected your Google Search Console account
   - At least one property must be available in your GSC account

## Generating Reports

### Step 1: Select Property and Date Range

1. **Select Property**: Choose the Search Console property you want to analyze
2. **Select Date Range Type**: 
   - **Preset Range**: Choose from 7, 14, 30, or 90 days
   - **Custom Range**: Select custom start and end dates using date picker
3. **Date Range Options**:
   - Last 7 days
   - Last 14 days
   - Last 30 days (default)
   - Last 90 days
   - **Custom dates**: Any date range you specify

### Step 2: Generate Reports

Click the **"تولید گزارشات"** (Generate Reports) button to generate all analytics reports.

## Report Types

### 1. Summary Statistics

**Average Position Change**
- Shows the average change in position between the previous period and current period
- Negative values indicate improvement (lower position = better)
- Positive values indicate decline

**Period Comparison**
- Previous Period: The date range before your selected period
- Current Period: Your selected date range

### 2. High Impressions, Low Clicks (Non-Zero)

**Purpose**: Identify pages with high visibility but low engagement

**What it shows**:
- Top 5 pages with highest impressions
- These pages have clicks > 0 but relatively low click rates
- Useful for identifying optimization opportunities

**Action Items**:
- Review page titles and meta descriptions
- Improve content relevance
- Optimize for better CTR

### 3. High Impressions, Zero Clicks

**Purpose**: Find pages that appear in search but never get clicked

**What it shows**:
- Top 5 pages with highest impressions but 0 clicks
- These pages are visible but not attractive to searchers

**Action Items**:
- Rewrite titles to be more compelling
- Improve meta descriptions
- Check if content matches search intent
- Consider if page should be indexed

### 4. Clicks Decreased > 25%

**Purpose**: Monitor pages with significant traffic drops

**What it shows**:
- Top 5 pages with clicks decreased by more than 25%
- Comparison between previous and current period
- Percentage change in clicks

**Action Items**:
- Investigate what changed (content, competitors, algorithm)
- Check for technical issues
- Review recent updates to the page
- Analyze competitor improvements

### 5. Highest Clicks

**Purpose**: Identify your best performing pages

**What it shows**:
- Top 5 pages with most clicks
- Complete metrics: impressions, CTR, position

**Action Items**:
- Learn from successful pages
- Apply similar strategies to other pages
- Consider creating more content like these pages

### 6. Lowest Impressions and Clicks

**Purpose**: Find pages that need more visibility

**What it shows**:
- Top 5 pages with lowest impressions and clicks (excluding zeros)
- Pages that are indexed but not performing

**Action Items**:
- Improve SEO optimization
- Add internal links to these pages
- Update content to be more relevant
- Consider if page should be removed or redirected

### 7. Highest CTR

**Purpose**: Identify pages with best click-through rates

**What it shows**:
- Top 5 pages with highest CTR
- Pages that effectively convert impressions to clicks

**Action Items**:
- Study what makes these titles/descriptions effective
- Apply similar patterns to other pages
- These are your best examples of good optimization

### 8. Lowest CTR

**Purpose**: Find pages with poor click-through rates

**What it shows**:
- Top 5 pages with lowest CTR (excluding zero clicks)
- Pages that get clicks but have poor CTR

**Action Items**:
- Improve titles and meta descriptions
- Make content more relevant to search queries
- Test different title variations

### 9. Zero Clicks, Low CTR (< 10%)

**Purpose**: Identify pages that appear but are not attractive

**What it shows**:
- All pages with 0 clicks and CTR below 10%
- Sorted by impressions (highest first)

**Action Items**:
- These pages need immediate attention
- Rewrite titles completely
- Improve meta descriptions
- Consider if content matches search intent

### 10. Clicks with Position > 6

**Purpose**: Find pages that get clicks despite poor rankings

**What it shows**:
- Pages with clicks but average position above 6
- These pages have potential but need ranking improvement

**Action Items**:
- Improve on-page SEO
- Build more backlinks
- Optimize content quality
- These pages are getting clicks, so they have value

## Internal Links Analysis

### Purpose
Analyze internal linking structure of your top pages to identify linking opportunities.

### How to Use

1. Select property and date range
2. Click **"تحلیل Internal Links"** (Analyze Internal Links)
3. Wait for analysis (may take time as it scrapes pages)

### Results

**Highest Internal Links**
- Top 5 pages with most internal links
- These are your hub pages
- Good for distributing link equity

**Lowest Internal Links**
- Top 5 pages with fewest internal links
- These pages need more internal links
- Opportunities to improve site structure

### Technical Details

- Analyzes up to 50 top pages from GSC
- Scrapes each page to count internal links
- May take 1-2 minutes depending on number of pages
- Timeout protection: stops if page takes too long

## Query-Based Page Search

### Purpose
Find all pages that rank for a specific search query, categorized by match type.

### How to Use

1. Select property and date range
2. Enter your search query in the text field
3. Click **"جستجوی صفحات بر اساس Query"** (Search Pages by Query)

### Results Categories

#### Exact Match
- Pages that rank for the exact query in Google Search Console
- These are pages that GSC shows for this specific query
- Sorted by clicks (descending)

#### Contain Match
- Pages where the URL contains the query text
- Example: Query "seo" matches `/seo-tools/` or `/blog/seo-guide/`
- Useful for finding related content

### Display Format

For each category (Exact and Contain):
- **Top 5**: Pages with highest clicks
- **Bottom 5**: Pages with lowest clicks

### Use Cases

1. **Content Audit**: Find all pages ranking for a keyword
2. **Cannibalization Check**: See if multiple pages compete for same query
3. **Optimization**: Identify which pages to optimize for a keyword
4. **Content Planning**: See what content exists for a topic

## API Endpoints

### Generate Reports
```
POST /search-console/reports/generate
```

**Request Body**:
```json
{
  "site_url": "sc-domain:example.com",
  "days": 30
}
```

**Response**:
```json
{
  "success": true,
  "period": "2025-10-17 to 2025-11-16",
  "previous_period": "2025-09-17 to 2025-10-16",
  "current_period": "2025-10-17 to 2025-11-16",
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

### Internal Links Analysis
```
POST /search-console/reports/internal-links
```

**Request Body**:
```json
{
  "site_url": "sc-domain:example.com",
  "days": 30,
  "limit": 50
}
```

**Response**:
```json
{
  "success": true,
  "highest_internal_links": [...],
  "lowest_internal_links": [...],
  "total_pages_analyzed": 50
}
```

### Pages by Query
```
POST /search-console/reports/pages-by-query
```

**Request Body**:
```json
{
  "site_url": "sc-domain:example.com",
  "query": "seo tools",
  "days": 30
}
```

**Response**:
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

## Best Practices

### 1. Regular Monitoring
- Run reports weekly or monthly
- Compare periods to track trends
- Focus on significant changes (>25%)

### 2. Action Prioritization
1. **High Priority**: Zero clicks with high impressions
2. **Medium Priority**: Significant click decreases
3. **Low Priority**: Pages with low but stable performance

### 3. Data Interpretation
- **Position Changes**: Negative = improvement, Positive = decline
- **CTR**: Higher is better, but context matters
- **Clicks vs Impressions**: High impressions + low clicks = optimization opportunity

### 4. Internal Links Strategy
- Link from high-authority pages to important pages
- Create hub pages with many internal links
- Fix orphan pages (pages with no internal links)

### 5. Query Analysis
- Use query search to find content gaps
- Identify keyword cannibalization
- Plan content optimization based on query data

## Troubleshooting

### No Data Available
- **Check Date Range**: GSC has 1-2 day delay, use recent dates
- **Verify Property**: Ensure property is selected correctly
- **Check Permissions**: User must have access to property in GSC

### Internal Links Analysis Fails
- **Timeout**: Some pages may take too long to load
- **Access Issues**: Pages may be behind login or blocked
- **Rate Limiting**: Too many requests may cause delays

### Query Search Returns No Results
- **Query Not Found**: The query may not have any rankings in selected period
- **Try Different Period**: Expand date range
- **Check Spelling**: Ensure query is spelled correctly

### Reports Take Too Long
- **Reduce Date Range**: Use shorter periods (7-14 days)
- **Limit Pages**: Internal links analysis is limited to 50 pages
- **Check API Limits**: GSC API has rate limits

## Technical Details

### Data Sources
- **Google Search Console API**: All metrics come from GSC API
- **Page Scraping**: Internal links are counted by scraping pages
- **Date Calculations**: Accounts for GSC's 1-2 day data delay

### Performance Considerations
- **API Limits**: GSC API allows up to 25,000 rows per request
- **Scraping Limits**: Internal links analysis limited to 50 pages
- **Caching**: No caching implemented, each request fetches fresh data

### Data Accuracy
- **Matches GSC UI**: Reports use same API calls as GSC interface
- **Date Alignment**: Automatically adjusts for GSC data delay
- **Aggregation**: Uses aggregated data for accurate totals

## Advanced Features

### Export to CSV
- **Purpose**: Export any report table to CSV format for analysis in Excel/Google Sheets
- **How to Use**: Click the "📥 Export CSV" button above any report table
- **Features**:
  - UTF-8 encoding for Persian/Arabic characters
  - Includes all columns and data
  - Ready to open in Excel or Google Sheets

### Filter and Search
- **Purpose**: Quickly find specific pages in large report tables
- **How to Use**: Type in the search box above any table
- **Features**:
  - Real-time filtering as you type
  - Searches across all columns
  - Case-insensitive search

### Sortable Tables
- **Purpose**: Sort data by any column for better analysis
- **How to Use**: Click on any column header to sort
- **Features**:
  - Click once for ascending order
  - Click again for descending order
  - Visual indicators show sort direction

### Collapsible Sections
- **Purpose**: Organize reports and reduce clutter
- **How to Use**: Click on section headers to expand/collapse
- **Features**:
  - All sections collapsible
  - Smooth animations
  - Saves screen space

### Performance Insights
- **Purpose**: Get automated recommendations based on your data
- **Features**:
  - Priority levels: High, Medium, Low
  - Actionable recommendations
  - Automatic detection of issues

### Charts and Visualization
- **Purpose**: Visual representation of data trends
- **Features**:
  - Interactive bar charts
  - Top 10 pages by CTR
  - Responsive design

### Email Reports
- **Purpose**: Send reports directly to email
- **How to Use**:
  1. Generate a report
  2. Click "📧 ارسال به ایمیل" button
  3. Enter recipient email
  4. Click "ارسال"
- **Features**:
  - Beautiful HTML email format
  - Includes report summary and key metrics
  - Plain text fallback
- **Note**: SMTP must be configured by admin first

### Historical Tracking
- **Purpose**: Save and view report history
- **Features**:
  - Automatically saves reports to browser
  - View previous reports
  - Compare different periods
- **Storage**: Uses browser localStorage (client-side)

## SMTP Configuration (Admin Only)

### Setting Up SMTP
1. **Access Admin Panel**: Navigate to Dashboard > "📧 تنظیمات SMTP Server" (Admin only)
2. **Configure Settings**:
   - Enable email sending
   - Enter SMTP server details
   - Set username and password
   - Configure from email and name
3. **Test Configuration**: Use "🧪 تست ارسال ایمیل" button
4. **Save Settings**: Click "💾 ذخیره تنظیمات"

### Supported Providers
- **Gmail**: Requires App Password (not regular password)
- **Outlook/Hotmail**: Standard SMTP settings
- **SendGrid**: Use API key as password
- **Mailgun**: Use SMTP credentials
- **Any SMTP Server**: Standard SMTP configuration

### Security
- Only admins can configure SMTP
- Password is hidden in display
- Secure file permissions (600)
- All emails sent from admin-configured account

For detailed SMTP setup instructions, see: `docs/SMTP_SETUP.md`

## Related Documentation

- **Setup Guide**: `docs/GOOGLE_SEARCH_CONSOLE_SETUP.md`
- **Troubleshooting**: `docs/SEARCH_CONSOLE_TROUBLESHOOTING.md`
- **Admin Setup**: `docs/GSC_ADMIN_SETUP.md`
- **SMTP Setup**: `docs/SMTP_SETUP.md`
- **Technical Docs**: `docs/README_SEARCH_CONSOLE.md`

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review related documentation
3. Verify GSC connection and permissions
4. Check server logs for API errors

