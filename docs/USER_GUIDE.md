User Guide - SEOAnalyzePro
===========================

Getting Started
---------------

### System Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Admin access for user management features

### Accessing the System
1. Open your web browser
2. Navigate to: `https://seoanalyze.shahinvaseghi.ir`
3. Login with your credentials
4. Default admin login: `admin` / `admin123`

Dashboard Overview
------------------

### Main Navigation
- **Dashboard**: Main overview page
- **Users**: User management (Admin only)
- **Competitors Analysis**: SEO analysis tool
- **Google Search Console**: Connect and view Search Console data
- **Logout**: End session

### User Roles
- **Admin**: Full access to all features including user management
- **User**: Access to analysis tools only

Competitors Analysis
--------------------

### Overview
The Competitors Analysis tool provides comprehensive SEO analysis of competitor websites with detailed metrics and insights.

### Getting Started
1. Click "Competitors Analysis" from the dashboard
2. Add competitor URLs (one per input field)
3. Optionally add keywords to track
4. Click "Analyze" to start the analysis

### Adding Competitors
1. **Single Competitor**: Enter URL in the first input field
2. **Multiple Competitors**: Click "+ Add competitor" to add more input fields
3. **Remove Competitors**: Click "Remove" button next to any input field
4. **URL Format**: Use full URLs (e.g., `https://example.com`)

### Adding Keywords
1. **Optional**: Keywords are not required for analysis
2. **Multiple Keywords**: Click "+ Add keyword" to add more
3. **Remove Keywords**: Click "Remove" button next to any keyword field
4. **Language Support**: Supports both English and Persian keywords

### Analysis Process
1. **Validation**: System checks for at least one competitor URL
2. **Processing**: Each competitor is analyzed sequentially
3. **Progress**: Button shows "Analyzing..." during processing
4. **Completion**: Results page displays when analysis is complete

Understanding Results
---------------------

### Analysis Summary
- **Competitors Analyzed**: Number of websites analyzed
- **Keywords Tracked**: Number of keywords monitored
- **Results File**: Timestamped JSON file name

### Basic SEO Metrics
- **Title Tag**: Page title content
- **Meta Description**: Meta description text
- **Word Count**: Total content word count
- **H1-H4 Count**: Number of heading tags

### Page Speed Analysis
- **Desktop Speed**: Loading time on desktop (seconds)
- **Mobile Speed**: Loading time on mobile (seconds)
- **Overall Rating**: Performance rating (عالی/خوب/نیاز به بهبود)
- **Performance Score**: Numerical score (0-100)

Google Search Console Integration
---------------------------------

### Overview
Connect your Google Search Console account to view detailed search analytics, track query performance, and monitor your site's visibility in Google Search.

### Getting Started
1. **Navigate to Search Console:**
   - Click "📊 Google Search Console" from the dashboard
   - Or go directly to: `/search-console/`

2. **Connect Your Account:**
   - Click "Connect Google Search Console" button
   - You'll be redirected to Google
   - Select your Google account
   - Review permissions and click "Allow"
   - You'll be redirected back to the application

3. **Select Property:**
   - Choose a property from the dropdown (e.g., `https://example.com`)
   - Select time range (7, 14, 30, or 90 days)
   - Click "Load Analytics"

### Viewing Data

#### Summary Metrics
- **Total Impressions**: Number of times your site appeared in search results
- **Total Clicks**: Number of clicks from search results
- **Average CTR**: Click-through rate percentage
- **Average Position**: Average position in search results

#### Top Search Queries
- View up to 500 most popular queries
- Shows first 20 queries by default
- Click "Show All" to expand full list
- Metrics include:
  - Query text
  - Impressions count
  - Clicks count
  - CTR percentage
  - Average position

#### Top Landing Pages
- View up to 500 most popular pages
- Shows first 20 pages by default
- Click "Show All" to expand full list
- Same metrics as queries

### Best Practices
1. **Single Click**: Only click "Connect" once - wait for redirect
2. **Data Refresh**: Data may be 1-2 days behind (Google's delay)
3. **Date Range**: Use longer ranges (30-90 days) for more data
4. **Property Selection**: Make sure you have access to selected property

### Troubleshooting
- **State Mismatch Error**: Refresh page and try again (click Connect only once)
- **No Data**: Check property access permissions in Google Search Console
- **Data Doesn't Match**: GSC UI shows partial today's data - compare same date ranges

For detailed troubleshooting, see: `docs/SEARCH_CONSOLE_TROUBLESHOOTING.md`

Google Search Console Reports
------------------------------

### Overview
The GSC Reports module provides advanced analytics and reporting capabilities for your Search Console data. Generate comprehensive reports, analyze page performance, and track internal links.

### Accessing Reports
1. **Navigate to Reports:**
   - Click "📈 گزارشات سرچ کنسول (GSC Reports)" from the dashboard
   - Or go directly to: `/search-console/reports/`

2. **Prerequisites:**
   - Must have connected your Google Search Console account
   - At least one property must be available

### Generating Reports

#### Step 1: Select Property and Date Range
- Choose your Search Console property from dropdown
- Select date range: 7, 14, 30, or 90 days

#### Step 2: Generate Analytics Reports
Click **"تولید گزارشات"** (Generate Reports) to generate:
- **Position Changes**: Average position change between periods
- **High Impressions, Low Clicks**: Pages with visibility but low engagement
- **Zero Click Pages**: Pages appearing in search but never clicked
- **Click Decreases**: Pages with >25% click drops
- **Top Performers**: Best and worst performing pages
- **CTR Analysis**: Highest and lowest click-through rates

### Internal Links Analysis

1. **Select Property and Date Range**
2. Click **"تحلیل Internal Links"** (Analyze Internal Links)
3. System will scrape top pages to count internal links
4. Results show:
   - **Highest Internal Links**: Hub pages with most links
   - **Lowest Internal Links**: Pages needing more internal links

**Note**: Analysis may take 1-2 minutes as it scrapes pages

### Query-Based Page Search

1. **Enter Query**: Type your search query in the text field
2. Click **"جستجوی صفحات بر اساس Query"** (Search Pages by Query)
3. Results categorized as:
   - **Exact Match**: Pages ranking for exact query
   - **Contain Match**: Pages where URL contains query
4. Each category shows:
   - **Top 5**: Highest clicks
   - **Bottom 5**: Lowest clicks

### Report Types Explained

#### High Impressions, Low Clicks
- **Purpose**: Find pages with high visibility but low engagement
- **Action**: Optimize titles and meta descriptions

#### Zero Click Pages
- **Purpose**: Find pages appearing but never clicked
- **Action**: Rewrite titles, improve descriptions, check content relevance

#### Click Decreases > 25%
- **Purpose**: Monitor significant traffic drops
- **Action**: Investigate changes, check competitors, review updates

#### Highest/Lowest CTR
- **Purpose**: Identify best and worst performing pages
- **Action**: Learn from successful pages, fix poor performers

### Best Practices
1. **Regular Monitoring**: Run reports weekly or monthly
2. **Prioritize Actions**: Focus on zero clicks and significant drops first
3. **Compare Periods**: Track trends over time
4. **Internal Links**: Link from high-authority pages to important pages

For complete documentation, see: `docs/GSC_REPORTS_GUIDE.md`

**Color Coding:**
- 🟢 **Green**: Excellent performance (≤ 1.5s desktop, ≤ 2.5s mobile)
- 🟡 **Yellow**: Good performance (1.5-3s desktop, 2.5-4s mobile)
- 🔴 **Red**: Needs improvement (> 3s desktop, > 4s mobile)

### Mobile UX/UI Analysis
- **Mobile Friendly**: Compatibility with mobile devices
- **UI Quality**: User interface quality rating
- **UX Score**: User experience score (0-100)
- **Responsive Design**: Mobile-responsive layout
- **Touch Friendly**: Touch-optimized interface

### Technical SEO
- **Schema Markup**: Structured data presence
- **Page Size**: Total page size in KB
- **Page Type**: Detected page type (Home, Service, Article, etc.)
- **Logo URL**: Website logo URL
- **Featured Image**: Main page image URL
- **Address**: Physical business address
- **Google Maps**: Google Maps integration

### Content Analysis
- **H1-H4 Tags**: Complete heading structure
- **Images**: Total images and missing alt text
- **Internal Links**: Links within the same domain
- **External Links**: Links to other domains
- **Keywords Found**: Extracted keywords from content
- **Content Structure**: Paragraphs, lists, tables, forms

### Interactive Features
- **Collapsible Sections**: Click section headers to expand/collapse
- **Detailed Views**: Expand sections for comprehensive details
- **Color Coding**: Visual indicators for performance levels
- **Export Ready**: Results saved as JSON files

User Management (Admin Only)
----------------------------

### Accessing User Management
1. Login as admin user
2. Click "Users" from the dashboard
3. View, create, edit, or delete users

### Creating Users
1. Click "Create User" button
2. Enter username and password
3. Select role (User or Admin)
4. Click "Create" to save

### Editing Users
1. Click "Edit" next to any user
2. Modify password or role
3. Click "Update" to save changes

### Deleting Users
1. Click "Delete" next to any user
2. Confirm deletion
3. User will be removed from system

### User Roles
- **Admin**: Full system access including user management
- **User**: Access to analysis tools only

Best Practices
--------------

### Competitor Analysis
1. **Start Small**: Begin with 2-3 competitors
2. **Relevant URLs**: Use specific page URLs, not just homepage
3. **Keyword Strategy**: Focus on your target keywords
4. **Regular Analysis**: Perform analysis monthly or quarterly
5. **Compare Results**: Look for patterns and opportunities

### URL Selection
- **Specific Pages**: Use landing pages, product pages, or blog posts
- **Relevant Content**: Choose pages similar to your content
- **Current Pages**: Ensure URLs are active and accessible
- **Diverse Sources**: Include different types of competitors

### Keyword Tracking
- **Target Keywords**: Focus on your primary keywords
- **Long-tail Keywords**: Include specific, longer phrases
- **Local Keywords**: Add location-based terms if relevant
- **Competitor Keywords**: Track keywords competitors rank for

### Results Interpretation
1. **Performance Comparison**: Compare speed and UX scores
2. **Content Analysis**: Review heading structure and content quality
3. **Technical Issues**: Identify missing schema, slow loading, etc.
4. **Opportunities**: Find gaps in competitor strategies
5. **Action Items**: Create improvement plans based on findings

### Data Management
1. **Export Results**: Download JSON files for further analysis
2. **Track Progress**: Compare results over time
3. **Share Insights**: Use results for team discussions
4. **Archive Old Data**: Keep historical analysis for trends

Troubleshooting
---------------

### Common Issues
1. **Analysis Not Starting**: Check if URLs are valid and accessible
2. **Partial Results**: Some competitors may fail due to access restrictions
3. **Slow Analysis**: Large websites may take longer to analyze
4. **Missing Data**: Some metrics may not be available for all sites

### Getting Help
1. **Check Logs**: Review system logs for error details
2. **Try Again**: Retry analysis if it fails
3. **Contact Admin**: Reach out to system administrator
4. **Document Issues**: Note specific error messages and steps

### Performance Tips
1. **Limit Competitors**: Analyze 5-10 competitors at a time
2. **Use Specific URLs**: Avoid analyzing entire websites
3. **Check Network**: Ensure stable internet connection
4. **Peak Hours**: Avoid analysis during high-traffic periods

Security and Privacy
--------------------

### Data Protection
- **Secure Storage**: All data is stored securely on the server
- **Access Control**: Only authorized users can access the system
- **Session Management**: Automatic logout after inactivity
- **Audit Trail**: All actions are logged for security

### Best Practices
1. **Strong Passwords**: Use complex passwords for all accounts
2. **Regular Updates**: Keep system updated with latest security patches
3. **Access Control**: Limit admin access to trusted users only
4. **Data Backup**: Regular backups of user data and analysis results

### Privacy Considerations
- **Public Data**: Analysis only uses publicly available website data
- **No Personal Data**: System doesn't collect personal information
- **Compliance**: Follow applicable data protection regulations
- **Transparency**: Clear documentation of data usage

Advanced Features
-----------------

### Schema Markup Analysis
- **Detection**: Identifies existing structured data
- **Suggestions**: Provides recommended schema markup
- **JSON Format**: Ready-to-use schema code
- **Validation**: Checks schema implementation

### Mobile Optimization
- **UX Analysis**: Comprehensive mobile user experience review
- **Performance Metrics**: Mobile-specific speed measurements
- **Issue Detection**: Identifies mobile-specific problems
- **Improvement Suggestions**: Actionable recommendations

### Content Gap Analysis
- **Keyword Comparison**: Compare keyword usage across competitors
- **Content Structure**: Analyze content organization
- **Missing Elements**: Identify gaps in competitor content
- **Opportunity Mapping**: Find areas for improvement

### Technical SEO Audit
- **Page Speed**: Desktop and mobile performance analysis
- **Image Optimization**: Alt text and image analysis
- **Link Structure**: Internal and external link analysis
- **Schema Implementation**: Structured data assessment

Export and Integration
----------------------

### Data Export
- **JSON Format**: Machine-readable analysis results
- **Timestamped Files**: Organized by analysis date and time
- **Complete Data**: All metrics and analysis details included
- **Easy Integration**: Compatible with other SEO tools

### Integration Options
1. **API Access**: RESTful API for programmatic access
2. **Webhook Support**: Real-time notifications for analysis completion
3. **Third-party Tools**: Export to popular SEO platforms
4. **Custom Reports**: Generate custom analysis reports

### Data Analysis
1. **Trend Analysis**: Track performance changes over time
2. **Competitive Benchmarking**: Compare against industry standards
3. **ROI Measurement**: Measure impact of SEO improvements
4. **Reporting**: Generate comprehensive SEO reports

Support and Resources
---------------------

### Documentation
- **User Guide**: This comprehensive guide
- **API Documentation**: Technical integration details
- **Troubleshooting**: Common issues and solutions
- **Best Practices**: Optimization recommendations

### Training Resources
1. **Video Tutorials**: Step-by-step analysis guides
2. **Webinars**: Live training sessions
3. **Case Studies**: Real-world analysis examples
4. **Community Forum**: User discussions and tips

### Contact Information
- **Technical Support**: For system issues and bugs
- **Training Support**: For user education and best practices
- **Feature Requests**: For new functionality suggestions
- **General Inquiries**: For general questions and feedback

### System Status
- **Uptime Monitoring**: 24/7 system availability tracking
- **Performance Metrics**: Real-time system performance data
- **Maintenance Windows**: Scheduled maintenance notifications
- **Status Updates**: Real-time system status information

Version History
---------------

### Current Version: 1.0.0
- **Initial Release**: Complete competitors analysis functionality
- **User Management**: Admin and user role support
- **Comprehensive Analysis**: 40+ SEO metrics per competitor
- **Interactive Interface**: Collapsible sections and detailed views
- **Export Functionality**: JSON data export
- **Mobile Optimization**: Responsive design and mobile analysis

### Planned Features
- **Batch Processing**: Queue-based analysis for large datasets
- **Real-time Monitoring**: Live competitor tracking
- **Advanced Reporting**: Custom report generation
- **API Integration**: Third-party tool connections
- **Machine Learning**: AI-powered insights and recommendations

---

For additional support or questions, please refer to the troubleshooting guide or contact your system administrator.
