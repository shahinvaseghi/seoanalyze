"""
Sitemap Analyzer and Generator Module
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET
from typing import List, Dict, Set
from datetime import datetime
import re

sitemap_analyzer_bp = Blueprint('sitemap_analyzer', __name__, url_prefix='/sitemap-analyzer')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def find_sitemap_urls(base_url: str) -> List[str]:
    """Find sitemap URLs (robots.txt, common locations)"""
    sitemap_urls = []
    
    # Check robots.txt
    try:
        robots_url = urljoin(base_url, '/robots.txt')
        response = requests.get(robots_url, timeout=10)
        if response.status_code == 200:
            for line in response.text.split('\n'):
                if line.lower().startswith('sitemap:'):
                    sitemap_url = line.split(':', 1)[1].strip()
                    sitemap_urls.append(sitemap_url)
    except:
        pass
    
    # Common sitemap locations
    common_paths = [
        '/sitemap.xml',
        '/sitemap_index.xml',
        '/sitemap-index.xml',
        '/sitemaps.xml'
    ]
    
    for path in common_paths:
        sitemap_urls.append(urljoin(base_url, path))
    
    return sitemap_urls


def parse_sitemap(sitemap_url: str) -> Dict[str, any]:
    """Parse XML sitemap"""
    try:
        response = requests.get(sitemap_url, timeout=30)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        # Handle sitemap index
        if root.tag.endswith('sitemapindex'):
            sitemaps = []
            for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None:
                    sitemaps.append(loc.text)
            return {'type': 'index', 'sitemaps': sitemaps}
        
        # Handle regular sitemap
        urls = []
        for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            lastmod = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
            changefreq = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq')
            priority = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
            
            url_data = {
                'url': loc.text if loc is not None else None,
                'lastmod': lastmod.text if lastmod is not None else None,
                'changefreq': changefreq.text if changefreq is not None else None,
                'priority': priority.text if priority is not None else None
            }
            if url_data['url']:
                urls.append(url_data)
        
        return {'type': 'urlset', 'urls': urls, 'total': len(urls)}
        
    except Exception as e:
        return {'error': str(e)}


@sitemap_analyzer_bp.route('/')
@login_required
def sitemap_analyzer_page():
    """Sitemap Analyzer main page"""
    return render_template('sitemap_analyzer.html')


@sitemap_analyzer_bp.route('/api/analyze', methods=['POST'])
@login_required
def analyze_sitemap():
    """Analyze sitemap for a website"""
    data = request.json or {}
    url = data.get('url')
    sitemap_url = data.get('sitemap_url')  # Optional direct sitemap URL
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Find sitemap URLs
        if sitemap_url:
            sitemap_urls = [sitemap_url]
        else:
            sitemap_urls = find_sitemap_urls(url)
        
        found_sitemaps = []
        all_urls = []
        
        for sitemap_url in sitemap_urls:
            try:
                result = parse_sitemap(sitemap_url)
                if 'error' not in result:
                    found_sitemaps.append({
                        'url': sitemap_url,
                        'type': result.get('type'),
                        'total': result.get('total', 0),
                        'urls': result.get('urls', [])[:100]  # Limit for response
                    })
                    if result.get('type') == 'urlset':
                        all_urls.extend(result.get('urls', []))
            except:
                continue
        
        # Analyze sitemap
        issues = []
        if not found_sitemaps:
            issues.append('No sitemap found')
        
        # Check for common issues
        total_urls = len(all_urls)
        if total_urls > 50000:
            issues.append(f'Sitemap has {total_urls} URLs (Google recommends max 50,000)')
        
        urls_without_lastmod = [u for u in all_urls if not u.get('lastmod')]
        if len(urls_without_lastmod) > total_urls * 0.5:
            issues.append(f'{len(urls_without_lastmod)} URLs missing lastmod date')
        
        return jsonify({
            'success': True,
            'base_url': url,
            'sitemaps_found': len(found_sitemaps),
            'sitemaps': found_sitemaps,
            'total_urls': total_urls,
            'issues': issues,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Sitemap analysis failed: {str(e)}'}), 500


@sitemap_analyzer_bp.route('/api/generate', methods=['POST'])
@login_required
def generate_sitemap():
    """Generate sitemap by crawling website"""
    data = request.json or {}
    url = data.get('url')
    max_pages = int(data.get('max_pages', 100))
    include_images = data.get('include_images', False)
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # This would require crawling - simplified version
        return jsonify({
            'success': True,
            'message': 'Sitemap generation feature coming soon',
            'note': 'This requires website crawling functionality'
        })
        
    except Exception as e:
        return jsonify({'error': f'Sitemap generation failed: {str(e)}'}), 500

