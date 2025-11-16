#!/bin/bash

# SSL Certificate Setup Script for SEO Analyze Pro
# This script helps setup SSL certificate using Let's Encrypt

set -e

DOMAIN="seoanalyze.shahinvaseghi.ir"
EMAIL="your-email@example.com"  # Change this to your email

echo "======================================"
echo "SSL Certificate Setup for SEO Analyze Pro"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
else
    echo "Certbot is already installed."
fi

# Create directory for certbot challenges
mkdir -p /var/www/certbot

# Copy the nginx configuration
echo "Copying nginx configuration..."
cp /home/shahin/seoanalyzepro/configs/nginx/seoanalyzepro /etc/nginx/sites-available/seoanalyzepro

# Enable the site if not already enabled
if [ ! -L /etc/nginx/sites-enabled/seoanalyzepro ]; then
    ln -s /etc/nginx/sites-available/seoanalyzepro /etc/nginx/sites-enabled/
    echo "Site enabled."
fi

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

# If nginx test fails, exit
if [ $? -ne 0 ]; then
    echo "Nginx configuration test failed. Please fix the errors above."
    exit 1
fi

# Reload nginx
echo "Reloading nginx..."
systemctl reload nginx

# Check if certificate already exists
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo ""
    echo "SSL certificate already exists for $DOMAIN"
    echo "To renew, run: sudo certbot renew"
    exit 0
fi

# Obtain SSL certificate
echo ""
echo "Obtaining SSL certificate for $DOMAIN..."
echo "Make sure DNS is pointing to this server!"
echo ""
read -p "Enter your email address for Let's Encrypt notifications: " EMAIL

certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    -d $DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email

# If certificate was obtained successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "SSL Certificate obtained successfully!"
    echo "======================================"
    echo ""
    
    # Reload nginx to use the new certificate
    echo "Reloading nginx with SSL configuration..."
    systemctl reload nginx
    
    echo ""
    echo "Setup complete! Your site should now be accessible via HTTPS."
    echo ""
    echo "Next steps:"
    echo "1. Test your site: https://$DOMAIN"
    echo "2. After confirming everything works, uncomment HSTS header in nginx config"
    echo "3. Setup auto-renewal: certbot renew --dry-run"
    echo ""
    echo "Certbot will automatically renew certificates before they expire."
    
else
    echo ""
    echo "Failed to obtain SSL certificate."
    echo "Please check:"
    echo "1. DNS is properly configured and pointing to this server"
    echo "2. Port 80 is accessible from the internet"
    echo "3. Nginx is running and configuration is correct"
fi

