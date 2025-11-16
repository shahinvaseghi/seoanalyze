SEOAnalyzePro
==============

Professional SEO analysis platform with advanced keyword gap analysis capabilities. Built with Python and Flask, featuring secure authentication, comprehensive business intelligence, and actionable SEO insights.

## 🚀 New in v2.0: Enhanced Analysis Tools

The platform now includes powerful analysis tools:

### ⚡ Core Web Vitals Analysis
A comprehensive performance analysis system that provides detailed insights into website performance and user experience:

- **Real Metrics with Google API**: Get actual Core Web Vitals from Chrome User Experience Report (25,000 free requests/day)
- **Core Web Vitals Metrics**: LCP, INP, CLS, FCP, TTFB, TTI analysis
- **Device-Specific Performance**: Mobile, Desktop, Tablet optimization analysis
- **Lighthouse-Style Audit**: Performance, Accessibility, Best Practices, SEO scores
- **Safe Optimization Recommendations**: Protects essential files while providing actionable insights
- **Comprehensive Reporting**: Detailed text reports with copy functionality
- **Priority-Based Actions**: Immediate, short-term, and long-term recommendations
- **API Fallback**: Works with or without API key (static analysis as fallback)

### 📊 Google Search Console Integration
Connect your Google Search Console account and access real search analytics data:

- **OAuth 2.0 Authentication**: Secure per-user authentication
- **Multi-Property Support**: Access all your verified properties
- **Search Analytics**: Top queries, pages, impressions, clicks, CTR
- **Performance Tracking**: Monitor trends over 7, 14, 30, or 90 days
- **Real-Time Data**: Direct access to Google's official search data
- **Privacy First**: Each user's data is isolated and secure


### 🔍 Enhanced Keyword Gap Analysis v2.0
Treats keywords as "demand units" with deep business intelligence:

- **Business Context Integration**: Industry-aware analysis
- **Intent Recognition**: Automatic search intent classification  
- **N-gram Extraction**: Complete search query analysis
- **Multi-dimensional Scoring**: Comprehensive opportunity assessment
- **Strategic Recommendations**: AI-powered content strategy guidance
- **Priority Matrix**: Visual opportunity prioritization

### Key Features
- **Keyword as Demand Unit**: Rich keyword objects with intent, volume, difficulty, and business relevance
- **Business Intelligence**: Context-aware analysis based on your industry and services
- **Competitor Analysis**: Identify gaps your competitors rank for
- **Content Strategy**: Strategic recommendations for content creation
- **Performance Tracking**: Monitor and measure SEO improvements
- **Core Web Vitals**: Comprehensive website performance analysis and optimization

Contents
--------
- Quick Start
- Project Structure
- Configuration
- Application Overview
- Development Workflow
- Deployment (systemd + Gunicorn)
- Security Notes
- Documentation Index

Quick Start
-----------
1) Create and activate virtual environment and install deps:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2) Seed default admin user (admin/admin123) if not already present:
```bash
python -c "from app.services.storage import UserStorage; UserStorage().ensure_default_admin()"
```

3) (Optional) Configure Google PageSpeed API for real Core Web Vitals:
```bash
# See docs/GOOGLE_PAGESPEED_API_SETUP.md for getting free API key
cp configs/api_keys.json.example configs/api_keys.json
nano configs/api_keys.json  # Add your API key
```

4) Run the development server:
```bash
python -c "from app.web.app import app; app.run('127.0.0.1', 5000, debug=True)"
```
Visit http://127.0.0.1:5000

Project Structure
-----------------
```text
app/
  core/                 # (future) core analysis modules
  services/
    storage.py          # JSON-backed user storage
  utils/                # (future) shared utilities
  web/
    app.py              # Flask app factory and health route
    auth.py             # Login/logout routes
    routes.py           # Index/dashboard and auth guard
    templates/
      login.html
      dashboard.html
configs/                # (future) config files
results/                # (future) analysis outputs
tests/                  # (future) tests
README.md               # this file
requirements.txt        # Python dependencies
```

Configuration
-------------
- SECRET_KEY: picked from environment variable `SECRET_KEY`, defaults to a dev value. Always set a strong value in production.
- Session lifetime: 4 hours (see `app/web/app.py`).
- Users database: JSON file at `app/users.json` created on-demand.

Application Overview
--------------------
- Authentication: session-based with secure password hashing via Werkzeug. Credentials are verified against JSON storage.
- Views: Login form, protected dashboard, admin user management, and comprehensive analysis tools.
- Health: `/health` route returns `ok` for uptime checks.
- **Competitors Analysis**: Full-featured SEO analysis with 30+ metrics per competitor, collapsible results display, and JSON export.
- **Core Web Vitals Analysis**: Comprehensive performance analysis with device-specific metrics, Lighthouse-style audit, and safe optimization recommendations.
- **Enhanced Keyword Gap Analysis v2.0**: Advanced keyword analysis with business intelligence and strategic recommendations.

Development Workflow
--------------------
- Add new analyzers in `app/core/` and expose them via new Flask routes in `app/web/`.
- Keep storage access abstracted behind service modules (e.g., `storage.py`) to allow swapping JSON with a database later.
- Write tests in `tests/` as modules grow.

Deployment (systemd + Gunicorn)
-------------------------------
The repository can be run via Gunicorn and a systemd unit. Example unit (already installed here as `seoanalyzepro.service`):
```ini
[Unit]
Description=SEOAnalyzePro - Gunicorn WSGI Server
After=network.target

[Service]
User=shahin
Group=shahin
WorkingDirectory=/home/shahin/seoanalyzepro
Environment="PATH=/home/shahin/seoanalyzepro/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=please-set-strong-secret"
ExecStart=/home/shahin/seoanalyzepro/venv/bin/gunicorn -w 3 -b 127.0.0.1:5000 --timeout 120 app.web.app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Security Notes
--------------
- Change the default admin password immediately after first login.
- Set a strong `SECRET_KEY` in production.
- Consider HTTPS termination via Nginx/Traefik in front of Gunicorn.
- Limit exposure to localhost and front with a reverse proxy for internet-facing deployments.

Documentation Index
-------------------

### Google Search Console Integration
- **Setup Guide**: `docs/GOOGLE_SEARCH_CONSOLE_SETUP.md` - Complete OAuth 2.0 setup and configuration
- **Features**: Real search analytics, top queries and pages, performance tracking
- **Security**: Per-user authentication, isolated data storage, read-only access


### Core Web Vitals Analysis
- **API Setup Guide**: `docs/GOOGLE_PAGESPEED_API_SETUP.md` - Get real metrics in 5 minutes (FREE Google API)
- **Complete Documentation**: `docs/CORE_WEB_VITALS_DOCUMENTATION.md` - Comprehensive Core Web Vitals analysis documentation
- **Technical Guide**: `docs/CORE_WEB_VITALS_TECHNICAL_GUIDE.md` - Developer reference and architecture
- **Features**: Real metrics from Google API, Core Web Vitals metrics, device-specific performance, Lighthouse-style audit
- **Safety Guidelines**: Essential files protection and safe optimization recommendations
- **API Reference**: Complete API documentation and usage guide

### Enhanced Keyword Gap Analysis v2.0
- **Main Documentation**: `docs/KEYWORD_GAP_V2.md` - Core features and architecture
- **Complete User Guide**: `docs/ENHANCED_KEYWORD_GAP_V2_COMPLETE_GUIDE.md` - Comprehensive feature overview
- **Technical Documentation**: `docs/TECHNICAL_DOCUMENTATION_V2.md` - Developer reference and API
- **User Guide**: `docs/USER_GUIDE_V2.md` - Step-by-step user instructions

### Platform Documentation
- Config & Env: `docs/CONFIG_ENV.md`
- Operations & Troubleshooting: `docs/OPERATIONS_TROUBLESHOOTING.md`
- Security: `docs/SECURITY.md`
- Systemd: `docs/SYSTEMD.md`
- HTTPS Setup: `docs/README_HTTPS.md` - Complete HTTPS configuration guide
- SSL Troubleshooting: `docs/SSL_TROUBLESHOOTING.md` - SSL/HTTPS troubleshooting
- Cloudflare SSL: `docs/CLOUDFLARE_SSL_SETUP.md` - Cloudflare-specific SSL setup
- API (current/planned): `docs/API.md`
- Roadmap: `docs/ROADMAP.md`
- Persian overview: `docs/README_FA.md`
- **Competitors Analysis**: `docs/COMPETITORS_ANALYSIS.md` - Complete feature documentation
- **Core Modules**: `docs/CORE_MODULES.md` - Analysis engine documentation
- **UI Improvements**: `docs/UI_IMPROVEMENTS.md` - User interface enhancements


