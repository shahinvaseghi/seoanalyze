Troubleshooting Guide
====================

Common Issues and Solutions
---------------------------

### 1. Analysis Button Issues

#### Problem: Button darkens but no results shown
**Symptoms:**
- Button becomes disabled and shows "Analyzing..."
- No analysis results displayed
- Page remains on form

**Solutions:**
1. Check browser console for JavaScript errors
2. Verify form validation is working
3. Ensure at least one competitor URL is entered
4. Check server logs for analysis errors

#### Problem: Only first competitor analyzed
**Symptoms:**
- Multiple URLs entered but only first one analyzed
- Results show only one competitor

**Solutions:**
1. Verify all competitor inputs have values
2. Check form submission is working correctly
3. Review server logs for analysis progress
4. Ensure JavaScript form handling is correct

### 2. Form Submission Issues

#### Problem: Form not submitting
**Symptoms:**
- Clicking Analyze button does nothing
- No network requests in browser dev tools

**Solutions:**
1. Check JavaScript console for errors
2. Verify form validation logic
3. Ensure all required fields are filled
4. Check for JavaScript conflicts

#### Problem: Empty form data received
**Symptoms:**
- Server logs show empty competitors list
- "Please enter at least one competitor URL" error

**Solutions:**
1. Verify input field names are correct (`competitors[]`)
2. Check form structure in HTML
3. Ensure JavaScript is not preventing submission
4. Test with browser dev tools

### 3. Analysis Errors

#### Problem: Template rendering errors
**Symptoms:**
- `TypeError: '<=' not supported between instances of 'dict' and 'float'`
- Analysis completes but results page fails to load

**Solutions:**
1. Check template syntax for data structure access
2. Verify `page_speed.desktop.load_time` instead of `page_speed.desktop`
3. Clear Python cache: `find . -name "*.pyc" -delete`
4. Restart service: `sudo systemctl restart seoanalyzepro`

#### Problem: Analysis timeout
**Symptoms:**
- Analysis starts but never completes
- Long loading times

**Solutions:**
1. Check network connectivity
2. Verify target URLs are accessible
3. Review server timeout settings
4. Check for rate limiting issues

### 4. Performance Issues

#### Problem: Slow analysis
**Symptoms:**
- Analysis takes too long
- Server becomes unresponsive

**Solutions:**
1. Reduce number of competitors per analysis
2. Check server resources (CPU, memory)
3. Optimize analysis parameters
4. Consider implementing async processing

#### Problem: Memory issues
**Symptoms:**
- Server crashes during analysis
- Out of memory errors

**Solutions:**
1. Increase server memory
2. Process competitors one at a time
3. Clear cache between analyses
4. Optimize data structures

### 5. Display Issues

#### Problem: Collapsible sections not working
**Symptoms:**
- Sections don't expand/collapse
- JavaScript errors in console

**Solutions:**
1. Check JavaScript syntax
2. Verify element IDs are unique
3. Ensure DOM is loaded before script execution
4. Test JavaScript functions manually

#### Problem: Images not displaying correctly
**Symptoms:**
- "No src" for all images
- Missing image details

**Solutions:**
1. Check `images_detailed.images` structure
2. Verify image extraction logic
3. Review template data access
4. Test with different websites

### 6. Authentication Issues

#### Problem: Redirected to login page
**Symptoms:**
- Form submission redirects to `/login`
- Session expired

**Solutions:**
1. Check session timeout settings
2. Verify user is logged in
3. Clear browser cookies
4. Restart session

#### Problem: Admin features not visible
**Symptoms:**
- "Users" option not shown in dashboard
- Access denied errors

**Solutions:**
1. Verify user role is "admin"
2. Check `is_admin` flag in template
3. Review role assignment logic
4. Test with admin user

### 11. Google Search Console Issues

#### Problem: OAuth State Mismatch
**Symptoms:**
- "State mismatch" error after clicking Connect
- OAuth callback fails

**Solutions:**
1. Click "Connect" only once - don't double-click
2. Don't refresh page during OAuth flow
3. Wait a few seconds and try again
4. Check logs: `sudo journalctl -u seoanalyzepro | grep -E "(OAuth|state)"`

**See:** `docs/SEARCH_CONSOLE_TROUBLESHOOTING.md` for detailed guide

#### Problem: Data doesn't match Google Search Console
**Symptoms:**
- Numbers in app differ from GSC UI
- Different totals displayed

**Solutions:**
1. GSC has 1-2 day data delay - app shows up to yesterday
2. Ensure same date range in both (e.g., "Last 7 days")
3. Wait 24 hours and compare historical data
4. Both should match for same historical periods

#### Problem: No data showing
**Symptoms:**
- Connected successfully but no data appears

**Solutions:**
1. Check property URL format matches exactly
2. Verify user has Full/Restricted access in GSC
3. Try different date ranges (30, 90 days)
4. Check API logs for errors

### 7. Service Issues

#### Problem: Service not starting
**Symptoms:**
- `systemctl status seoanalyzepro` shows failed
- Application not accessible

**Solutions:**
1. Check service configuration: `sudo systemctl status seoanalyzepro`
2. Review service logs: `sudo journalctl -u seoanalyzepro`
3. Verify Python dependencies: `pip install -r requirements.txt`
4. Check file permissions

#### Problem: Port conflicts
**Symptoms:**
- "Address already in use" errors
- Service fails to bind to port 5000

**Solutions:**
1. Check for other services using port 5000: `sudo netstat -tlnp | grep :5000`
2. Kill conflicting processes
3. Change port in service configuration
4. Restart service

### 8. Nginx Issues

#### Problem: 502 Bad Gateway
**Symptoms:**
- Nginx returns 502 error
- Application not accessible through domain

**Solutions:**
1. Check if Flask app is running: `sudo systemctl status seoanalyzepro`
2. Verify Nginx configuration: `sudo nginx -t`
3. Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`
4. Restart Nginx: `sudo systemctl restart nginx`

#### Problem: SSL certificate issues
**Symptoms:**
- "Not secure" warning in browser
- SSL errors

**Solutions:**
1. Check SSL certificate validity
2. Verify certificate chain
3. Update certificate if expired
4. Check Nginx SSL configuration

### 9. Data Issues

#### Problem: Results not saved
**Symptoms:**
- Analysis completes but no JSON file created
- Missing results directory

**Solutions:**
1. Check `results/` directory permissions
2. Verify write access for application user
3. Create directory if missing: `mkdir -p app/results`
4. Check disk space

#### Problem: Corrupted user data
**Symptoms:**
- Login failures
- User management errors

**Solutions:**
1. Check `users.json` file integrity
2. Verify JSON syntax
3. Restore from backup if available
4. Recreate default admin user

### 10. Development Issues

#### Problem: Code changes not reflected
**Symptoms:**
- Modifications don't appear in application
- Old behavior persists

**Solutions:**
1. Clear Python cache: `find . -name "*.pyc" -delete && find . -name "__pycache__" -type d -exec rm -rf {} +`
2. Restart service: `sudo systemctl restart seoanalyzepro`
3. Check file permissions
4. Verify changes are saved

#### Problem: Import errors
**Symptoms:**
- `ModuleNotFoundError` in logs
- Missing dependencies

**Solutions:**
1. Install missing packages: `pip install -r requirements.txt`
2. Check virtual environment activation
3. Verify Python path
4. Review import statements

Debugging Commands
------------------

### Service Management
```bash
# Check service status
sudo systemctl status seoanalyzepro

# View service logs
sudo journalctl -u seoanalyzepro -f

# Restart service
sudo systemctl restart seoanalyzepro

# Check service configuration
sudo systemctl cat seoanalyzepro
```

### Application Testing
```bash
# Test application directly
cd /home/shahin/seoanalyzepro
python3 -c "from app.core.seo_analyzer import SEOAnalyzer; print('Import successful')"

# Test HTTP endpoint
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5000/health

# Check port usage
sudo netstat -tlnp | grep :5000
```

### File System
```bash
# Check file permissions
ls -la /home/shahin/seoanalyzepro/

# Check disk space
df -h

# Check directory structure
find /home/shahin/seoanalyzepro -type f -name "*.py" | head -10
```

### Nginx
```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# View Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/seoanalyzepro.access.log
```

### Database/Storage
```bash
# Check users.json
cat /home/shahin/seoanalyzepro/app/users.json

# Check results directory
ls -la /home/shahin/seoanalyzepro/app/results/

# Check file sizes
du -sh /home/shahin/seoanalyzepro/app/results/*
```

Log Analysis
------------

### Key Log Patterns
- **Analysis Start**: `Starting analysis for:`
- **Analysis Complete**: `Analysis completed for:`
- **Results Count**: `Results count:`
- **Form Data**: `Received competitors:`
- **Errors**: `Error analyzing`
- **Template Errors**: `TypeError` or `TemplateNotFound`

### Log Monitoring
```bash
# Monitor analysis logs
sudo journalctl -u seoanalyzepro -f | grep -E "(Starting|Analysis|Results|Error)"

# Monitor Nginx logs
sudo tail -f /var/log/nginx/seoanalyzepro.access.log

# Monitor system logs
sudo journalctl -f | grep seoanalyzepro
```

Performance Optimization
------------------------

### Server Resources
- **CPU**: Monitor during analysis
- **Memory**: Check for memory leaks
- **Disk**: Ensure sufficient space for results
- **Network**: Monitor bandwidth usage

### Application Optimization
- **Concurrent Analysis**: Process multiple competitors
- **Caching**: Cache analysis results
- **Rate Limiting**: Implement request throttling
- **Error Recovery**: Retry failed analyses

### Database Optimization
- **Indexing**: Add indexes for frequent queries
- **Cleanup**: Remove old analysis results
- **Backup**: Regular data backups
- **Monitoring**: Track database performance

Prevention Strategies
--------------------

### Regular Maintenance
1. **Daily**: Check service status and logs
2. **Weekly**: Review error logs and performance
3. **Monthly**: Update dependencies and security patches
4. **Quarterly**: Full system backup and testing

### Monitoring Setup
1. **Service Monitoring**: Systemd service status
2. **Application Monitoring**: Health check endpoints
3. **Performance Monitoring**: Resource usage tracking
4. **Error Monitoring**: Log analysis and alerting

### Backup Strategy
1. **Code Backup**: Version control (Git)
2. **Data Backup**: Regular user data backup
3. **Configuration Backup**: Service and Nginx configs
4. **Results Backup**: Analysis results archive

Contact Information
-------------------
For additional support or reporting issues:
- Check application logs first
- Review this troubleshooting guide
- Test with minimal configuration
- Document exact error messages and steps to reproduce
