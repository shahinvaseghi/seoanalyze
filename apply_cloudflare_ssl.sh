#!/bin/bash

# Apply Cloudflare Origin Certificate to Nginx
# Run this AFTER you have obtained the certificate from Cloudflare dashboard

set -e

echo "======================================"
echo "Cloudflare SSL Configuration Script"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Check if certificate files exist
if [ ! -f "/etc/ssl/cloudflare/cert.pem" ] || [ ! -f "/etc/ssl/cloudflare/key.pem" ]; then
    echo "Error: Certificate files not found!"
    echo ""
    echo "Please create the certificate files first:"
    echo "1. Go to Cloudflare Dashboard"
    echo "2. SSL/TLS → Origin Server → Create Certificate"
    echo "3. Save the certificate to: /etc/ssl/cloudflare/cert.pem"
    echo "4. Save the private key to: /etc/ssl/cloudflare/key.pem"
    echo ""
    echo "Quick commands:"
    echo "  sudo mkdir -p /etc/ssl/cloudflare"
    echo "  sudo nano /etc/ssl/cloudflare/cert.pem    # Paste origin certificate"
    echo "  sudo nano /etc/ssl/cloudflare/key.pem     # Paste private key"
    echo "  sudo chmod 600 /etc/ssl/cloudflare/key.pem"
    echo "  sudo chmod 644 /etc/ssl/cloudflare/cert.pem"
    exit 1
fi

echo "✓ Certificate files found"

# Create updated nginx config for Cloudflare
CONFIG_FILE="/home/shahin/seoanalyzepro/configs/nginx/seoanalyzepro"
TEMP_CONFIG="${CONFIG_FILE}.cloudflare"

cat > "$TEMP_CONFIG" << 'EOF'
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name seoanalyze.shahinvaseghi.ir;
    
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS Server with Cloudflare Origin Certificate
server {
    listen 443 ssl http2;
    server_name seoanalyze.shahinvaseghi.ir;

    # Cloudflare Origin Certificate
    ssl_certificate /etc/ssl/cloudflare/cert.pem;
    ssl_certificate_key /etc/ssl/cloudflare/key.pem;
    
    # SSL Configuration - Optimized for Cloudflare
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Cloudflare Real IP (restore visitor's real IP)
    set_real_ip_from 103.21.244.0/22;
    set_real_ip_from 103.22.200.0/22;
    set_real_ip_from 103.31.4.0/22;
    set_real_ip_from 104.16.0.0/13;
    set_real_ip_from 104.24.0.0/14;
    set_real_ip_from 108.162.192.0/18;
    set_real_ip_from 131.0.72.0/22;
    set_real_ip_from 141.101.64.0/18;
    set_real_ip_from 162.158.0.0/15;
    set_real_ip_from 172.64.0.0/13;
    set_real_ip_from 173.245.48.0/20;
    set_real_ip_from 188.114.96.0/20;
    set_real_ip_from 190.93.240.0/20;
    set_real_ip_from 197.234.240.0/22;
    set_real_ip_from 198.41.128.0/17;
    set_real_ip_from 2400:cb00::/32;
    set_real_ip_from 2606:4700::/32;
    set_real_ip_from 2803:f800::/32;
    set_real_ip_from 2405:b500::/32;
    set_real_ip_from 2405:8100::/32;
    set_real_ip_from 2a06:98c0::/29;
    set_real_ip_from 2c0f:f248::/32;
    real_ip_header CF-Connecting-IP;

    access_log /var/log/nginx/seoanalyzepro.access.log;
    error_log  /var/log/nginx/seoanalyzepro.error.log warn;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Ssl on;
        proxy_set_header CF-Connecting-IP $http_cf_connecting_ip;
        proxy_set_header CF-Ray $http_cf_ray;
        proxy_read_timeout 300;
    }

    location /health {
        proxy_pass http://127.0.0.1:5000/health;
    }
}
EOF

echo "✓ Configuration file created"

# Backup current config
if [ -f "/etc/nginx/sites-available/seoanalyzepro" ]; then
    cp /etc/nginx/sites-available/seoanalyzepro /etc/nginx/sites-available/seoanalyzepro.backup.$(date +%Y%m%d_%H%M%S)
    echo "✓ Current configuration backed up"
fi

# Copy new config
cp "$TEMP_CONFIG" /etc/nginx/sites-available/seoanalyzepro
echo "✓ New configuration installed"

# Test nginx configuration
echo ""
echo "Testing nginx configuration..."
if nginx -t; then
    echo ""
    echo "✓ Configuration test successful!"
    echo ""
    
    # Reload nginx
    echo "Reloading nginx..."
    systemctl reload nginx
    
    echo ""
    echo "======================================"
    echo "✓ SSL Configuration Applied!"
    echo "======================================"
    echo ""
    echo "Your site should now be accessible via HTTPS:"
    echo "  https://seoanalyze.shahinvaseghi.ir"
    echo ""
    echo "Next steps:"
    echo "1. Test your site in a browser"
    echo "2. In Cloudflare Dashboard, set SSL/TLS mode to 'Full (strict)'"
    echo "3. Enable 'Always Use HTTPS' in Cloudflare"
    echo ""
    echo "To verify SSL:"
    echo "  curl -I https://seoanalyze.shahinvaseghi.ir"
    
else
    echo ""
    echo "✗ Configuration test failed!"
    echo "Please check the errors above and try again."
    
    # Restore backup if it exists
    LATEST_BACKUP=$(ls -t /etc/nginx/sites-available/seoanalyzepro.backup.* 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        echo "Restoring previous configuration..."
        cp "$LATEST_BACKUP" /etc/nginx/sites-available/seoanalyzepro
        systemctl reload nginx
        echo "Previous configuration restored."
    fi
    
    exit 1
fi

