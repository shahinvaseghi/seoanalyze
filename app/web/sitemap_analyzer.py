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


def parse_sitemap(sitemap_url: str, headers: Dict = None) -> Dict[str, any]:
    """Parse XML sitemap"""
    try:
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        
        response = requests.get(sitemap_url, timeout=30, headers=headers)
        response.raise_for_status()
        
        # Try to parse XML
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            # Try to handle namespaces more flexibly
            content = response.content
            # Remove namespace declarations if they cause issues
            content = re.sub(b'xmlns="[^"]*"', b'', content)
            content = re.sub(b'xmlns:sitemap="[^"]*"', b'', content)
            root = ET.fromstring(content)
        
        # Handle sitemap index - check both with and without namespace
        namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        
        # Try with namespace first
        sitemap_elements = root.findall(f'.//{namespace}sitemap')
        if not sitemap_elements:
            # Try without namespace
            sitemap_elements = root.findall('.//sitemap')
        
        if sitemap_elements:
            # This is a sitemap index
            sitemaps = []
            for sitemap in sitemap_elements:
                # Try with namespace
                loc = sitemap.find(f'{namespace}loc')
                if loc is None:
                    # Try without namespace
                    loc = sitemap.find('loc')
                
                lastmod = sitemap.find(f'{namespace}lastmod')
                if lastmod is None:
                    lastmod = sitemap.find('lastmod')
                
                if loc is not None and loc.text:
                    sitemaps.append({
                        'url': loc.text,
                        'lastmod': lastmod.text if lastmod is not None else None
                    })
            
            return {'type': 'index', 'sitemaps': sitemaps, 'total': len(sitemaps)}
        
        # Handle regular sitemap - try with namespace first
        url_elements = root.findall(f'.//{namespace}url')
        if not url_elements:
            # Try without namespace
            url_elements = root.findall('.//url')
        
        if url_elements:
            urls = []
            for url_elem in url_elements:
                # Try with namespace
                loc = url_elem.find(f'{namespace}loc')
                if loc is None:
                    loc = url_elem.find('loc')
                
                lastmod = url_elem.find(f'{namespace}lastmod')
                if lastmod is None:
                    lastmod = url_elem.find('lastmod')
                
                changefreq = url_elem.find(f'{namespace}changefreq')
                if changefreq is None:
                    changefreq = url_elem.find('changefreq')
                
                priority = url_elem.find(f'{namespace}priority')
                if priority is None:
                    priority = url_elem.find('priority')
                
                if loc is not None and loc.text:
                    url_data = {
                        'url': loc.text,
                        'lastmod': lastmod.text if lastmod is not None else None,
                        'changefreq': changefreq.text if changefreq is not None else None,
                        'priority': priority.text if priority is not None else None
                    }
                    urls.append(url_data)
            
            return {'type': 'urlset', 'urls': urls, 'total': len(urls)}
        
        # If we get here, couldn't parse
        return {'error': 'Unknown sitemap format'}
        
    except requests.RequestException as e:
        return {'error': f'Failed to fetch sitemap: {str(e)}'}
    except Exception as e:
        return {'error': f'Failed to parse sitemap: {str(e)}'}


@sitemap_analyzer_bp.route('/')
@login_required
def sitemap_analyzer_page():
    """Sitemap Analyzer main page"""
    return render_template('sitemap_analyzer.html')


def parse_all_sitemaps(sitemap_url: str, headers: Dict = None, max_depth: int = 3, visited: Set = None) -> Dict[str, any]:
    """Recursively parse sitemap and all nested sitemaps"""
    if visited is None:
        visited = set()
    
    if sitemap_url in visited or max_depth <= 0:
        return {'sitemaps': [], 'urls': []}
    
    visited.add(sitemap_url)
    
    result = parse_sitemap(sitemap_url, headers)
    
    if 'error' in result:
        return {'sitemaps': [], 'urls': [], 'errors': [f'{sitemap_url}: {result["error"]}']}
    
    all_sitemaps = [{'url': sitemap_url, 'type': result.get('type'), 'total': result.get('total', 0)}]
    all_urls = []
    
    if result.get('type') == 'index':
        # Parse all sitemaps in the index
        for sitemap_info in result.get('sitemaps', []):
            nested_url = sitemap_info.get('url') if isinstance(sitemap_info, dict) else sitemap_info
            if nested_url:
                nested_result = parse_all_sitemaps(nested_url, headers, max_depth - 1, visited)
                all_sitemaps.extend(nested_result.get('sitemaps', []))
                all_urls.extend(nested_result.get('urls', []))
    elif result.get('type') == 'urlset':
        # This is a regular sitemap with URLs
        all_urls.extend(result.get('urls', []))
    
    return {'sitemaps': all_sitemaps, 'urls': all_urls}


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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Find sitemap URLs
        if sitemap_url:
            sitemap_urls = [sitemap_url]
        else:
            sitemap_urls = find_sitemap_urls(url)
        
        found_sitemaps = []
        all_urls = []
        errors = []
        
        # Try each potential sitemap URL
        for potential_url in sitemap_urls:
            try:
                # First check if it exists
                response = requests.head(potential_url, timeout=10, headers=headers, allow_redirects=True)
                if response.status_code == 200:
                    # Parse this sitemap and all nested ones
                    result = parse_all_sitemaps(potential_url, headers)
                    if result.get('sitemaps'):
                        found_sitemaps.extend(result.get('sitemaps', []))
                        all_urls.extend(result.get('urls', []))
                        break  # Found a valid sitemap, no need to check others
            except requests.RequestException:
                continue
            except Exception as e:
                errors.append(f'Error checking {potential_url}: {str(e)}')
                continue
        
        # If no sitemap found, try to parse the first URL anyway (might be a sitemap)
        if not found_sitemaps and sitemap_urls:
            try:
                result = parse_all_sitemaps(sitemap_urls[0], headers)
                if result.get('sitemaps'):
                    found_sitemaps.extend(result.get('sitemaps', []))
                    all_urls.extend(result.get('urls', []))
            except Exception as e:
                errors.append(f'Error parsing {sitemap_urls[0]}: {str(e)}')
        
        # Analyze sitemap
        issues = []
        if not found_sitemaps:
            issues.append('No sitemap found. Checked: ' + ', '.join(sitemap_urls[:3]))
        
        # Check for common issues
        total_urls = len(all_urls)
        if total_urls > 0:
            if total_urls > 50000:
                issues.append(f'Sitemap has {total_urls} URLs (Google recommends max 50,000)')
            
            urls_without_lastmod = [u for u in all_urls if not u.get('lastmod')]
            if len(urls_without_lastmod) > total_urls * 0.5:
                issues.append(f'{len(urls_without_lastmod)} URLs missing lastmod date ({round(len(urls_without_lastmod)/total_urls*100, 1)}%)')
        
        # Limit URLs in response for performance
        limited_urls = all_urls[:500]  # Show first 500 URLs
        
        return jsonify({
            'success': True,
            'base_url': url,
            'sitemaps_found': len(found_sitemaps),
            'sitemaps': found_sitemaps,
            'total_urls': total_urls,
            'urls': limited_urls,
            'issues': issues,
            'errors': errors if errors else None,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': f'Sitemap analysis failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


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

