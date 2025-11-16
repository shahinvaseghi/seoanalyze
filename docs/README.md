SEOAnalyzePro - Comprehensive SEO Analysis Platform
===================================================

## Overview

SEOAnalyzePro is a comprehensive SEO analysis platform designed to provide detailed insights into competitor websites. Built with Python Flask and modern web technologies, it offers professional-grade SEO analysis tools with an intuitive user interface.

## Features

### Core Functionality
- **User Authentication**: Secure login system with role-based access
- **Dashboard**: Centralized control panel for all features
- **User Management**: Admin-only user creation and management
- **Competitors Analysis**: Comprehensive SEO analysis tool
- **Google Search Console**: Full integration with GSC API for analytics
- **GSC Reports**: Advanced reporting and analytics module with export, filtering, and email
- **SMTP Email System**: Admin-configured email sending for reports

### SEO Analysis Capabilities
- **Basic SEO**: Title, meta description, headings (H1-H4), word count
- **Technical SEO**: Schema markup, page speed, mobile optimization
- **Content Analysis**: Images, links, keywords, content structure
- **Performance Metrics**: Page speed, mobile UX/UI analysis
- **Advanced Features**: Schema suggestions, content gap analysis
- **Interactive Results**: Collapsible sections, color-coded metrics
- **Export Functionality**: JSON data export with timestamps
- **Multi-competitor Analysis**: Analyze multiple competitors simultaneously

### User Interface
- **Dark Theme**: Professional dark interface design
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive Elements**: Collapsible sections, dynamic forms
- **Real-time Feedback**: Loading states and progress indicators
- **Error Handling**: User-friendly error messages and validation

## Technology Stack

### Backend
- **Python 3.12**: Core programming language
- **Flask**: Web framework with blueprint architecture
- **Werkzeug**: Security utilities for password hashing
- **Gunicorn**: WSGI HTTP server for production deployment
- **Requests**: HTTP library for web scraping
- **BeautifulSoup4**: HTML parsing and data extraction
- **LXML**: XML/HTML parser for improved performance

### Frontend
- **HTML5**: Semantic markup structure
- **CSS3**: Modern styling with dark theme
- **JavaScript (Vanilla)**: Interactive functionality
- **Jinja2**: Template engine for dynamic content

### Infrastructure
- **Systemd**: Service management and auto-start
- **Nginx**: Reverse proxy and static file serving
- **JSON**: Data storage and configuration
- **Linux**: Operating system support

## Installation

### Prerequisites
- Ubuntu 20.04+ or compatible Linux distribution
- Python 3.12+
- Nginx web server
- Systemd service manager

### Quick Start
1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd seoanalyzepro
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Service**
   ```bash
   sudo cp configs/systemd/seoanalyzepro.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable seoanalyzepro
   sudo systemctl start seoanalyzepro
   ```

4. **Configure Nginx**
   ```bash
   sudo cp configs/nginx/seoanalyzepro /etc/nginx/sites-available/
   sudo ln -s /etc/nginx/sites-available/seoanalyzepro /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

5. **Access Application**
   - URL: `https://seoanalyze.shahinvaseghi.ir`
   - Default login: `admin` / `admin123`

## Project Structure

```
seoanalyzepro/
├── app/                    # Main application directory
│   ├── core/              # Core analysis modules
│   │   ├── seo_analyzer.py    # Main SEO analysis engine
│   │   ├── models.py          # Data models and enums
│   │   ├── cro_analyzer.py    # Conversion rate optimization
│   │   ├── cwv_analyzer.py    # Core web vitals analysis
│   │   ├── eeat_analyzer.py   # E-E-A-T analysis
│   │   ├── intent_analyzer.py # Search intent analysis
│   │   └── local_seo_analyzer.py # Local SEO analysis
│   ├── services/          # Service layer
│   │   └── storage.py         # User data storage
│   ├── web/               # Web application
│   │   ├── app.py             # Flask application factory
│   │   ├── auth.py            # Authentication routes
│   │   ├── routes.py          # Main application routes
│   │   ├── users.py           # User management routes
│   │   ├── competitors.py     # Competitors analysis routes
│   │   └── templates/         # HTML templates
│   ├── results/           # Analysis results storage
│   └── users.json         # User data file
├── configs/               # Configuration files
│   ├── systemd/           # Systemd service configuration
│   └── nginx/             # Nginx configuration
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Usage

### Getting Started
1. **Login**: Use admin credentials to access the system
2. **Dashboard**: Navigate through available features
3. **User Management**: Create and manage user accounts (Admin only)
4. **Competitors Analysis**: Analyze competitor websites

### Competitors Analysis
1. **Add Competitors**: Enter competitor URLs (one per input field)
2. **Add Keywords**: Optionally add keywords to track
3. **Analyze**: Click "Analyze" to start comprehensive analysis
4. **Review Results**: View detailed metrics and insights
5. **Export Data**: Download JSON results for further analysis

### User Management (Admin)
1. **View Users**: See all system users
2. **Create User**: Add new users with roles
3. **Edit User**: Modify user credentials and roles
4. **Delete User**: Remove users from system

## Analysis Metrics

### Basic SEO
- Title tag content and length
- Meta description content and length
- Heading structure (H1-H4)
- Word count and content analysis
- Image analysis with alt text

### Technical SEO
- Schema markup detection and suggestions
- Page speed analysis (desktop and mobile)
- Mobile UX/UI evaluation
- Internal and external link analysis
- Page type detection

### Performance Analysis
- Desktop loading time
- Mobile loading time
- Performance rating and score
- Mobile friendliness assessment
- UI/UX quality evaluation

### Content Analysis
- Keyword density and tracking
- Content structure analysis
- Image optimization assessment
- Link structure evaluation
- Reading level analysis

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `FLASK_ENV`: Environment (development/production)
- `DEBUG`: Debug mode flag

### Service Configuration
- **Port**: 5000 (configurable)
- **Workers**: 3 (configurable)
- **Timeout**: 30 seconds
- **Auto-restart**: Enabled

### Nginx Configuration
- **Domain**: seoanalyze.shahinvaseghi.ir
- **SSL**: Supported
- **Proxy**: HTTP to Flask application
- **Static Files**: Served directly by Nginx

## Security

### Authentication
- **Session Management**: Secure session handling
- **Password Hashing**: Werkzeug security utilities
- **Role-based Access**: Admin and user roles
- **Session Timeout**: 30-minute inactivity timeout

### Data Protection
- **Secure Storage**: JSON-based user data storage
- **Input Validation**: Form validation and sanitization
- **Error Handling**: Secure error messages
- **Access Control**: Route protection and authorization

## Monitoring and Logging

### Service Monitoring
- **Systemd**: Service status and health monitoring
- **Logs**: Comprehensive logging via journalctl
- **Health Check**: `/health` endpoint for monitoring
- **Auto-restart**: Automatic service recovery

### Application Logging
- **Analysis Progress**: Real-time analysis tracking
- **Error Logging**: Detailed error information
- **Performance Metrics**: Analysis timing and results
- **User Activity**: Login and action tracking

## Troubleshooting

### Common Issues
- **Service Not Starting**: Check systemd status and logs
- **Analysis Failures**: Review error logs and network connectivity
- **Template Errors**: Clear Python cache and restart service
- **Performance Issues**: Monitor system resources

### Debug Commands
```bash
# Check service status
sudo systemctl status seoanalyzepro

# View service logs
sudo journalctl -u seoanalyzepro -f

# Test application
curl http://127.0.0.1:5000/health

# Check Nginx configuration
sudo nginx -t
```

## Development

### Code Structure
- **Modular Design**: Blueprint-based Flask architecture
- **Separation of Concerns**: Clear separation between layers
- **Error Handling**: Comprehensive error handling throughout
- **Documentation**: Extensive inline and external documentation

### Testing
- **Manual Testing**: Comprehensive manual testing procedures
- **Error Scenarios**: Tested error handling and edge cases
- **Performance Testing**: Load testing and optimization
- **Browser Compatibility**: Cross-browser testing

### Contributing
1. **Code Style**: Follow Python PEP 8 guidelines
2. **Documentation**: Update documentation for new features
3. **Testing**: Test all changes thoroughly
4. **Security**: Review security implications of changes

## Roadmap

### Current Version: 1.0.0
- ✅ Complete competitors analysis functionality
- ✅ User management system
- ✅ Interactive results display
- ✅ Export functionality
- ✅ Mobile optimization

### Planned Features
- **Batch Processing**: Queue-based analysis for large datasets
- **Real-time Monitoring**: Live competitor tracking
- **Advanced Reporting**: Custom report generation
- **API Integration**: Third-party tool connections
- **Machine Learning**: AI-powered insights and recommendations

## Support

### Documentation
- **User Guide**: Comprehensive user documentation
- **API Documentation**: Technical integration details
- **Troubleshooting Guide**: Common issues and solutions
- **Best Practices**: Optimization recommendations

### Contact
- **Technical Support**: For system issues and bugs
- **Training Support**: For user education and best practices
- **Feature Requests**: For new functionality suggestions

## License

This project is proprietary software. All rights reserved.

## Changelog

### Version 1.0.0 (Current)
- Initial release with complete competitors analysis functionality
- User authentication and role-based access control
- Comprehensive SEO analysis with 40+ metrics
- Interactive results display with collapsible sections
- Export functionality with JSON data format
- Mobile-responsive design and mobile analysis
- Systemd service integration and Nginx configuration
- Extensive documentation and troubleshooting guides

---

For detailed information about specific features, please refer to the individual documentation files in the `docs/` directory.
