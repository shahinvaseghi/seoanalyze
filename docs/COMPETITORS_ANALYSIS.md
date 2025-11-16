Competitors Analysis Feature
============================

Overview
--------
The Competitors Analysis feature provides comprehensive SEO analysis of competitor websites with detailed metrics extraction and interactive results display.

Implementation
--------------
- **Blueprint**: `app/web/competitors.py`
- **Templates**: `app/web/templates/competitors.html`, `competitors_result.html`
- **Core Engine**: `app/core/seo_analyzer.py` (130KB, 77 functions)
- **Data Models**: `app/core/models.py`

Features
--------

### 1. Dynamic Input Interface
- **Multiple Competitor URLs**: Add unlimited competitor URLs
- **Multiple Keywords**: Track multiple keywords across competitors
- **Dynamic Form**: JavaScript-powered add/remove inputs
- **Validation**: Ensures at least one competitor URL is provided

### 2. Comprehensive Analysis
Extracts 30+ SEO metrics per competitor:

#### Basic SEO Metrics
- **Title Tag**: Page title extraction
- **Meta Description**: Meta description content
- **Meta Keywords**: Meta keywords (if present)
- **Word Count**: Content word count (excluding header/footer/nav)
- **H1-H4 Tags**: Complete heading structure analysis

#### Content Structure
- **H1 Count**: Number of H1 tags
- **H2 Count**: Number of H2 tags  
- **H3 Count**: Number of H3 tags
- **H4 Count**: Number of H4 tags
- **Content Structure**: Analysis of content organization

#### Images & Media
- **Total Images**: Count of all images
- **Images without Alt**: Missing alt text count
- **Image Details**: Complete image analysis including:
  - Source URL (src)
  - Alt text
  - Image type (JPEG, PNG, GIF, SVG, WebP, etc.)
  - Dimensions (width x height)
  - Link status (if image is wrapped in anchor tag)
  - Link URL (if applicable)

#### Links Analysis
- **Internal Links**: Count and details of internal links
- **External Links**: Count and details of external links
- **Link Analysis**: Anchor text and destination analysis

#### Technical SEO
- **Schema Markup**: JSON-LD and Microdata detection
- **Page Size**: Total page size in KB
- **Page Load Performance**: Desktop and mobile speed analysis
- **Mobile UX Score**: Mobile user experience rating

#### Advanced Features
- **Logo Detection**: Automatic logo URL extraction
- **Featured Image**: Main page image identification
- **Address Extraction**: Physical address detection
- **Google Maps Integration**: Maps URL detection
- **Page Type Detection**: Automatic page type classification
- **Schema Suggestions**: Recommended Schema.org markup

### 3. Interactive Results Display

#### Collapsible Sections
- **H1 Tags**: Expandable list with count indicator
- **H2 Tags**: Expandable list with count indicator
- **H3 Tags**: Expandable list with count indicator
- **H4 Tags**: Expandable list with count indicator
- **Images List**: Expandable detailed image analysis
- **Schema Markup Suggestions**: Expandable JSON schema recommendations
- **Content Structure Analysis**: Expandable content analysis details
- **Keywords Found**: Expandable keyword list
- **Keyword Tracking**: Expandable keyword density analysis
- **Internal Links Details**: Expandable internal links list
- **External Links Details**: Expandable external links list
- **Mobile Issues**: Expandable mobile UX issues list
- **Mobile Good Points**: Expandable mobile UX strengths list

#### Visual Design
- **Dark Theme**: Professional dark interface
- **Card Layout**: Organized metric cards
- **Color Coding**: Different colors for different metric types
- **Responsive Design**: Works on all screen sizes

#### Data Presentation
- **Vertical Lists**: Clean, readable tag lists
- **Detailed Metrics**: Comprehensive information display
- **File Information**: Results saved with timestamp
- **Export Ready**: JSON format for further analysis
- **Color-Coded Performance**: Green (excellent), Yellow (good), Red (needs improvement)
- **Progress Tracking**: Real-time analysis progress in logs
- **Error Handling**: Graceful handling of failed analyses

### 4. Data Storage
- **JSON Export**: Results saved to `results/` directory
- **Timestamped Files**: `competitors_analysis_YYYYMMDD_HHMMSS.json`
- **Complete Data**: All analysis results preserved
- **Structured Format**: Easy to parse and analyze

Usage
-----

### Access
1. Login to the system
2. Navigate to Dashboard
3. Click "Competitors Analysis"

### Input
1. Add competitor URLs (one per input field)
2. Add keywords to track (optional)
3. Click "Analyze" to start analysis
4. Button changes to "Analyzing..." during processing
5. Multiple competitors are analyzed sequentially

### Results
1. View comprehensive analysis results
2. Expand/collapse sections as needed
3. Review detailed metrics for each competitor
4. Download results file for further analysis

Technical Details
-----------------

### Core Analysis Engine
- **File**: `app/core/seo_analyzer.py`
- **Size**: 130KB, 2852 lines
- **Functions**: 77 analysis functions
- **Dependencies**: requests, BeautifulSoup4, lxml

### Specialized Analyzers
- **CWV Analyzer**: Core Web Vitals analysis
- **E-E-A-T Analyzer**: Expertise, Experience, Authoritativeness, Trustworthiness
- **CRO Analyzer**: Conversion Rate Optimization
- **Intent Analyzer**: Search Intent detection
- **Local SEO Analyzer**: Local search optimization

### Data Models
- **SearchIntent Enum**: Informational, Transactional, Local, Comparison, Navigational
- **PageType Enum**: Home, Service, Local, Article, Product, Portfolio, Video, FAQ
- **FunnelLevel Enum**: TOFU, MOFU, BOFU
- **ActionType Enum**: Create, Update, Merge, Delete, Redirect

### Performance
- **Concurrent Analysis**: Multiple competitors analyzed simultaneously
- **Error Handling**: Graceful handling of failed requests
- **Timeout Management**: 10-second timeout per request
- **Rate Limiting**: 2-second delay between requests

Security & Best Practices
-------------------------
- **User Agent Rotation**: Realistic browser headers
- **Request Timeouts**: Prevents hanging requests
- **Error Logging**: Comprehensive error tracking
- **Data Validation**: Input sanitization and validation
- **Session Management**: Secure user session handling

Future Enhancements
-------------------
- **Batch Processing**: Queue-based analysis for large datasets
- **Progress Tracking**: Real-time analysis progress
- **Export Options**: CSV, Excel, PDF export formats
- **Comparison Tools**: Side-by-side competitor comparison
- **Trend Analysis**: Historical data tracking
- **API Integration**: RESTful API for external access

Dependencies
------------
- Flask 3.0.0
- requests 2.32.5
- beautifulsoup4 4.14.2
- lxml 6.0.2
- Werkzeug 3.0.1

Files Modified
--------------
- `app/web/competitors.py` - Main blueprint and analysis logic
- `app/web/templates/competitors.html` - Input form with dynamic fields
- `app/web/templates/competitors_result.html` - Results display with collapsible sections
- `app/web/app.py` - Blueprint registration
- `app/core/seo_analyzer.py` - Core analysis engine (imported from previous project)
- `app/core/models.py` - Data structures (imported from previous project)
- `requirements.txt` - Added analysis dependencies

Notes
-----
- Analysis results are cached in JSON format for quick retrieval
- All image URLs are converted to absolute URLs for consistency
- Schema markup detection supports both JSON-LD and Microdata formats
- Mobile UX analysis includes Google's mobile-friendly test criteria
- Page speed analysis provides both desktop and mobile metrics
