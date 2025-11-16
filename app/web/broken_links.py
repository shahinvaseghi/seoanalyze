"""
Broken Links Checker Module
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set
import concurrent.futures
from datetime import datetime

broken_links_bp = Blueprint('broken_links', __name__, url_prefix='/broken-links')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def check_link(url: str, timeout: int = 10) -> Dict[str, any]:
    """Check if a link is broken"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
        
        return {
            'url': url,
            'status_code': response.status_code,
            'is_broken': response.status_code >= 400,
            'redirects': len(response.history) > 0,
            'final_url': response.url if response.url != url else None
        }
    except requests.exceptions.Timeout:
        return {
            'url': url,
            'status_code': 0,
            'is_broken': True,
            'error': 'Timeout'
        }
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'status_code': 0,
            'is_broken': True,
            'error': str(e)
        }


def extract_links(soup: BeautifulSoup, base_url: str) -> Set[str]:
    """Extract all links from page"""
    links = set()
    domain = urlparse(base_url).netloc
    
    # Internal links
    for tag in soup.find_all(['a', 'link'], href=True):
        href = tag.get('href', '')
        if href:
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            if parsed.netloc == domain or not parsed.netloc:
                links.add(absolute_url)
    
    # External links
    for tag in soup.find_all(['a', 'link'], href=True):
        href = tag.get('href', '')
        if href:
            absolute_url = urljoin(base_url, href)
            parsed = urlparse(absolute_url)
            if parsed.netloc and parsed.netloc != domain:
                links.add(absolute_url)
    
    return links


@broken_links_bp.route('/')
@login_required
def broken_links_page():
    """Broken Links Checker main page"""
    return render_template('broken_links.html')


@broken_links_bp.route('/api/check', methods=['POST'])
@login_required
def check_broken_links():
    """Check for broken links on a page or site"""
    data = request.json or {}
    url = data.get('url')
    check_type = data.get('type', 'page')  # page, site
    max_pages = int(data.get('max_pages', 10))
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract links
        all_links = extract_links(soup, url)
        
        # Limit links if needed
        if len(all_links) > 100:
            all_links = list(all_links)[:100]
        
        # Check links in parallel
        broken_links = []
        working_links = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_link = {executor.submit(check_link, link): link for link in all_links}
            
            for future in concurrent.futures.as_completed(future_to_link):
                result = future.result()
                if result['is_broken']:
                    broken_links.append(result)
                else:
                    working_links.append(result)
        
        # Separate internal and external
        domain = urlparse(url).netloc
        internal_broken = [l for l in broken_links if urlparse(l['url']).netloc == domain or not urlparse(l['url']).netloc]
        external_broken = [l for l in broken_links if urlparse(l['url']).netloc != domain]
        
        return jsonify({
            'success': True,
            'url': url,
            'total_links_checked': len(all_links),
            'broken_links_count': len(broken_links),
            'working_links_count': len(working_links),
            'internal_broken': internal_broken,
            'external_broken': external_broken,
            'broken_links': broken_links,
            'timestamp': datetime.now().isoformat()
        })
        
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Broken links check failed: {str(e)}'}), 500

