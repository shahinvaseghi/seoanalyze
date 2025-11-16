#!/bin/bash

# SSL Certificate Setup using DNS Challenge
# Use this if you're behind Cloudflare or other CDN/Proxy

set -e

DOMAIN="seoanalyze.shahinvaseghi.ir"

echo "======================================"
echo "SSL Setup using DNS Challenge"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "This method is useful when:"
echo "1. You're using Cloudflare or another CDN/Proxy"
echo "2. Port 80 is not directly accessible from the internet"
echo "3. You're behind a firewall or NAT"
echo ""

# Install certbot DNS plugin for Cloudflare (if using Cloudflare)
echo "For Cloudflare users, install the DNS plugin:"
echo "  sudo apt install python3-certbot-dns-cloudflare"
echo ""
echo "Then create /root/.secrets/cloudflare.ini with:"
echo "  dns_cloudflare_api_token = YOUR_API_TOKEN"
echo ""
echo "Run:"
echo "  sudo certbot certonly --dns-cloudflare \\"
echo "    --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \\"
echo "    -d $DOMAIN"
echo ""

# Alternative: Manual DNS challenge
echo "Or use manual DNS challenge:"
echo "  sudo certbot certonly --manual --preferred-challenges dns -d $DOMAIN"
echo ""
echo "You'll need to add a TXT record to your DNS as instructed by certbot."

