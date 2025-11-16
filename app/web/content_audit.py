"""
Content Audit Module
Analyze content quality, duplicates, and gaps
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set
import hashlib
from datetime import datetime

content_audit_bp = Blueprint('content_audit', __name__, url_prefix='/content-audit')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def extract_main_content(soup: BeautifulSoup) -> str:
    """Extract main content from page"""
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
    
    # Get text
    text = soup.get_text()
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text


def calculate_content_hash(content: str) -> str:
    """Calculate hash for content similarity"""
    # Normalize content
    normalized = content.lower().strip()
    # Remove extra whitespace
    normalized = ' '.join(normalized.split())
    return hashlib.md5(normalized.encode()).hexdigest()


@content_audit_bp.route('/')
@login_required
def content_audit_page():
    """Content Audit main page"""
    return render_template('content_audit.html')


@content_audit_bp.route('/api/analyze', methods=['POST'])
@login_required
def analyze_content():
    """Analyze content for a URL"""
    data = request.json or {}
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract content
        main_content = extract_main_content(soup)
        content_hash = calculate_content_hash(main_content)
        
        # Analyze content
        word_count = len(main_content.split())
        char_count = len(main_content)
        
        # Check for common issues
        issues = []
        if word_count < 300:
            issues.append('Content is too short (less than 300 words)')
        elif word_count > 3000:
            issues.append('Content is very long (may need to be split)')
        
        # Check headings
        h1_count = len(soup.find_all('h1'))
        h2_count = len(soup.find_all('h2'))
        h3_count = len(soup.find_all('h3'))
        
        if h1_count == 0:
            issues.append('No H1 heading found')
        elif h1_count > 1:
            issues.append(f'Multiple H1 headings found ({h1_count})')
        
        if h2_count == 0 and word_count > 500:
            issues.append('No H2 headings found (consider adding structure)')
        
        # Check images
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        if images_without_alt:
            issues.append(f'{len(images_without_alt)} images without alt text')
        
        # Check internal links
        internal_links = []
        external_links = []
        domain = urlparse(url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            absolute_url = urljoin(url, href)
            parsed = urlparse(absolute_url)
            if parsed.netloc == domain or not parsed.netloc:
                internal_links.append(absolute_url)
            else:
                external_links.append(absolute_url)
        
        if len(internal_links) == 0:
            issues.append('No internal links found')
        
        # Content quality score
        quality_score = 100
        quality_score -= max(0, (300 - word_count) / 10) if word_count < 300 else 0
        quality_score -= len(images_without_alt) * 2
        quality_score -= max(0, (1 - h1_count) * 10)
        quality_score = max(0, quality_score)
        
        return jsonify({
            'success': True,
            'url': url,
            'content_analysis': {
                'word_count': word_count,
                'char_count': char_count,
                'content_hash': content_hash,
                'quality_score': round(quality_score, 1)
            },
            'structure': {
                'h1_count': h1_count,
                'h2_count': h2_count,
                'h3_count': h3_count
            },
            'links': {
                'internal_links_count': len(internal_links),
                'external_links_count': len(external_links)
            },
            'images': {
                'total_images': len(images),
                'images_without_alt': len(images_without_alt)
            },
            'issues': issues,
            'recommendations': [
                'Add more internal links to related content' if len(internal_links) < 3 else None,
                'Add alt text to images' if images_without_alt else None,
                'Add H2 headings for better structure' if h2_count == 0 and word_count > 500 else None
            ]
        })
        
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Content audit failed: {str(e)}'}), 500


@content_audit_bp.route('/api/duplicates', methods=['POST'])
@login_required
def find_duplicates():
    """Find duplicate content across multiple URLs"""
    data = request.json or {}
    urls = data.get('urls', [])
    
    if not urls or len(urls) < 2:
        return jsonify({'error': 'At least 2 URLs are required'}), 400
    
    try:
        content_hashes = {}
        duplicates = []
        
        for url in urls[:20]:  # Limit to 20 URLs
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                content = extract_main_content(soup)
                content_hash = calculate_content_hash(content)
                
                if content_hash in content_hashes:
                    duplicates.append({
                        'url1': content_hashes[content_hash],
                        'url2': url,
                        'similarity': 'High (identical content)'
                    })
                else:
                    content_hashes[content_hash] = url
                    
            except:
                continue
        
        return jsonify({
            'success': True,
            'total_urls_checked': len(urls),
            'duplicates_found': len(duplicates),
            'duplicates': duplicates
        })
        
    except Exception as e:
        return jsonify({'error': f'Duplicate detection failed: {str(e)}'}), 500

