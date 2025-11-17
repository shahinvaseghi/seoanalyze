"""
Content Audit Module
Comprehensive content quality analysis, duplicates detection, and optimization recommendations
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set, Tuple
import hashlib
from datetime import datetime
import re
from collections import Counter

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
    for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
        script.decompose()
    
    # Get text
    text = soup.get_text()
    
    # Clean up whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text


def calculate_readability(text: str) -> Dict[str, float]:
    """Calculate readability metrics (Flesch Reading Ease approximation)"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    words = text.split()
    words_count = len(words)
    sentences_count = len(sentences) if sentences else 1
    
    # Count syllables (approximation: count vowel groups)
    syllables = 0
    for word in words:
        word_lower = word.lower()
        vowels = re.findall(r'[aeiouy]+', word_lower)
        syllables += max(1, len(vowels))
    
    avg_sentence_length = words_count / sentences_count if sentences_count > 0 else 0
    avg_syllables_per_word = syllables / words_count if words_count > 0 else 0
    
    # Simplified Flesch Reading Ease
    # Score: 0-100 (higher = easier to read)
    readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    readability_score = max(0, min(100, readability_score))
    
    return {
        'score': round(readability_score, 1),
        'avg_sentence_length': round(avg_sentence_length, 1),
        'avg_syllables_per_word': round(avg_syllables_per_word, 2),
        'level': 'Very Easy' if readability_score >= 80 else 
                 'Easy' if readability_score >= 70 else
                 'Fairly Easy' if readability_score >= 60 else
                 'Standard' if readability_score >= 50 else
                 'Fairly Difficult' if readability_score >= 30 else
                 'Difficult' if readability_score >= 0 else 'Very Difficult'
    }


def analyze_keywords(text: str, min_length: int = 3) -> Dict[str, any]:
    """Analyze keyword frequency and density"""
    # Remove common stop words (Persian and English)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'از', 'به', 'در', 'با', 'برای', 'که', 'این', 'آن', 'است', 'بود', 'شود', 'می', 'را', 'یا'
    }
    
    # Extract words
    words = re.findall(r'\b\w+\b', text.lower())
    words = [w for w in words if len(w) >= min_length and w not in stop_words]
    
    word_freq = Counter(words)
    total_words = len(words)
    
    # Get top keywords
    top_keywords = word_freq.most_common(20)
    
    # Calculate keyword density
    keyword_density = {}
    for word, count in top_keywords:
        density = (count / total_words * 100) if total_words > 0 else 0
        keyword_density[word] = round(density, 2)
    
    return {
        'total_unique_words': len(word_freq),
        'top_keywords': [{'word': word, 'count': count, 'density': keyword_density[word]} 
                        for word, count in top_keywords],
        'keyword_density_warnings': [
            word for word, density in keyword_density.items() 
            if density > 3  # Over-optimization warning
        ]
    }


def analyze_content_structure(soup: BeautifulSoup) -> Dict[str, any]:
    """Analyze content structure and hierarchy"""
    h1_tags = soup.find_all('h1')
    h2_tags = soup.find_all('h2')
    h3_tags = soup.find_all('h3')
    h4_tags = soup.find_all('h4')
    h5_tags = soup.find_all('h5')
    h6_tags = soup.find_all('h6')
    
    # Extract heading text
    h1_texts = [h.get_text().strip() for h in h1_tags]
    h2_texts = [h.get_text().strip() for h in h2_tags]
    h3_texts = [h.get_text().strip() for h in h3_tags]
    
    # Check heading hierarchy
    structure_issues = []
    if len(h1_tags) == 0:
        structure_issues.append('No H1 heading found - essential for SEO')
    elif len(h1_tags) > 1:
        structure_issues.append(f'Multiple H1 headings ({len(h1_tags)}) - should have only one')
    
    if len(h2_tags) == 0:
        structure_issues.append('No H2 headings - content lacks structure')
    
    # Check if headings are in order
    if len(h3_tags) > 0 and len(h2_tags) == 0:
        structure_issues.append('H3 headings found without H2 headings - improper hierarchy')
    
    return {
        'h1_count': len(h1_tags),
        'h2_count': len(h2_tags),
        'h3_count': len(h3_tags),
        'h4_count': len(h4_tags),
        'h5_count': len(h5_tags),
        'h6_count': len(h6_tags),
        'h1_texts': h1_texts,
        'h2_texts': h2_texts[:10],  # Limit to first 10
        'h3_texts': h3_texts[:10],
        'structure_issues': structure_issues,
        'structure_score': 100 - (len(structure_issues) * 15)
    }


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
        paragraph_count = len(soup.find_all('p'))
        
        # Readability analysis
        readability = calculate_readability(main_content)
        
        # Keyword analysis
        keyword_analysis = analyze_keywords(main_content)
        
        # Structure analysis
        structure_analysis = analyze_content_structure(soup)
        
        # Check images
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        images_with_alt = [img for img in images if img.get('alt')]
        
        # Analyze images
        image_analysis = {
            'total_images': len(images),
            'images_with_alt': len(images_with_alt),
            'images_without_alt': len(images_without_alt),
            'alt_text_coverage': round((len(images_with_alt) / len(images) * 100) if images else 0, 1),
            'large_images': len([img for img in images if img.get('width') and int(img.get('width', 0)) > 1920]),
            'missing_dimensions': len([img for img in images if not (img.get('width') and img.get('height'))])
        }
        
        # Check internal/external links
        internal_links = []
        external_links = []
        nofollow_links = []
        domain = urlparse(url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            absolute_url = urljoin(url, href)
            parsed = urlparse(absolute_url)
            
            if 'nofollow' in link.get('rel', []):
                nofollow_links.append(absolute_url)
            
            if parsed.netloc == domain or not parsed.netloc:
                internal_links.append({
                    'url': absolute_url,
                    'text': link.get_text().strip()[:50],
                    'nofollow': 'nofollow' in link.get('rel', [])
                })
            else:
                external_links.append({
                    'url': absolute_url,
                    'text': link.get_text().strip()[:50],
                    'nofollow': 'nofollow' in link.get('rel', [])
                })
        
        # Check for multimedia
        videos = soup.find_all(['video', 'iframe'])
        video_count = len([v for v in videos if 'youtube' in v.get('src', '').lower() or 'vimeo' in v.get('src', '').lower()])
        
        # Check for lists
        ul_lists = soup.find_all('ul')
        ol_lists = soup.find_all('ol')
        
        # Check for tables
        tables = soup.find_all('table')
        
        # Check for forms
        forms = soup.find_all('form')
        
        # Content freshness (check for dates)
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'تاریخ.*?\d{4}',
            r'published|updated|date'
        ]
        has_date = any(re.search(pattern, main_content, re.I) for pattern in date_patterns)
        
        # Check for meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_desc_text = meta_desc.get('content', '') if meta_desc else ''
        meta_desc_length = len(meta_desc_text)
        
        # Generate comprehensive issues
        issues = []
        recommendations = []
        
        # Content length issues
        if word_count < 300:
            issues.append({
                'type': 'warning',
                'category': 'Content Length',
                'message': f'Content is too short ({word_count} words). Recommended: 300-2000 words for better SEO.',
                'impact': 'High'
            })
            recommendations.append('Expand content to at least 300 words with valuable, relevant information')
        elif word_count < 500:
            issues.append({
                'type': 'info',
                'category': 'Content Length',
                'message': f'Content length is acceptable ({word_count} words) but could be expanded for better SEO.',
                'impact': 'Medium'
            })
        elif word_count > 3000:
            issues.append({
                'type': 'warning',
                'category': 'Content Length',
                'message': f'Content is very long ({word_count} words). Consider splitting into multiple pages.',
                'impact': 'Medium'
            })
            recommendations.append('Consider breaking long content into multiple pages or using pagination')
        
        # Structure issues
        issues.extend([{
            'type': 'error' if 'essential' in issue.lower() else 'warning',
            'category': 'Structure',
            'message': issue,
            'impact': 'High' if 'essential' in issue.lower() else 'Medium'
        } for issue in structure_analysis.get('structure_issues', [])])
        
        # Image issues
        if image_analysis['images_without_alt'] > 0:
            issues.append({
                'type': 'warning',
                'category': 'Images',
                'message': f"{image_analysis['images_without_alt']} images without alt text ({image_analysis['alt_text_coverage']}% coverage)",
                'impact': 'High'
            })
            recommendations.append(f"Add descriptive alt text to {image_analysis['images_without_alt']} images for accessibility and SEO")
        
        if image_analysis['large_images'] > 0:
            issues.append({
                'type': 'info',
                'category': 'Images',
                'message': f"{image_analysis['large_images']} images may be too large (over 1920px width)",
                'impact': 'Medium'
            })
            recommendations.append('Optimize large images to improve page load speed')
        
        # Link issues
        if len(internal_links) == 0:
            issues.append({
                'type': 'warning',
                'category': 'Internal Linking',
                'message': 'No internal links found - important for SEO and user navigation',
                'impact': 'High'
            })
            recommendations.append('Add 3-5 internal links to related content on your site')
        elif len(internal_links) < 3:
            issues.append({
                'type': 'info',
                'category': 'Internal Linking',
                'message': f'Only {len(internal_links)} internal links found - consider adding more',
                'impact': 'Medium'
            })
        
        if len(external_links) == 0:
            issues.append({
                'type': 'info',
                'category': 'External Linking',
                'message': 'No external links found - consider linking to authoritative sources',
                'impact': 'Low'
            })
        
        # Readability issues
        if readability['score'] < 50:
            issues.append({
                'type': 'warning',
                'category': 'Readability',
                'message': f'Readability score is {readability["score"]} ({readability["level"]}) - content may be difficult to read',
                'impact': 'Medium'
            })
            recommendations.append('Simplify sentence structure and use shorter words to improve readability')
        
        # Keyword over-optimization
        if keyword_analysis.get('keyword_density_warnings'):
            issues.append({
                'type': 'warning',
                'category': 'Keyword Optimization',
                'message': f'Potential keyword stuffing detected: {", ".join(keyword_analysis["keyword_density_warnings"][:3])}',
                'impact': 'High'
            })
            recommendations.append('Reduce keyword density to avoid over-optimization penalties')
        
        # Meta description
        if not meta_desc_text:
            issues.append({
                'type': 'error',
                'category': 'Meta Tags',
                'message': 'Meta description is missing',
                'impact': 'High'
            })
            recommendations.append('Add a compelling meta description (150-160 characters)')
        elif meta_desc_length < 120:
            issues.append({
                'type': 'warning',
                'category': 'Meta Tags',
                'message': f'Meta description is too short ({meta_desc_length} characters). Recommended: 120-160 characters.',
                'impact': 'Medium'
            })
        elif meta_desc_length > 160:
            issues.append({
                'type': 'info',
                'category': 'Meta Tags',
                'message': f'Meta description may be truncated ({meta_desc_length} characters). Recommended: 120-160 characters.',
                'impact': 'Low'
            })
        
        # Content freshness
        if not has_date:
            issues.append({
                'type': 'info',
                'category': 'Content Freshness',
                'message': 'No publication or update date found',
                'impact': 'Low'
            })
            recommendations.append('Add publication date and last updated date to show content freshness')
        
        # Calculate comprehensive quality score
        quality_score = 100
        quality_score -= max(0, (300 - word_count) / 10) if word_count < 300 else 0
        quality_score -= image_analysis['images_without_alt'] * 2
        quality_score -= max(0, (1 - structure_analysis['h1_count']) * 10)
        quality_score -= max(0, (3 - len(internal_links)) * 5) if len(internal_links) < 3 else 0
        quality_score -= (50 - readability['score']) / 5 if readability['score'] < 50 else 0
        quality_score -= 10 if not meta_desc_text else 0
        quality_score = max(0, min(100, quality_score))
        
        # Generate grade
        grade = 'A' if quality_score >= 90 else 'B' if quality_score >= 80 else 'C' if quality_score >= 70 else 'D' if quality_score >= 60 else 'F'
        
        return jsonify({
            'success': True,
            'url': url,
            'content_analysis': {
                'word_count': word_count,
                'char_count': char_count,
                'paragraph_count': paragraph_count,
                'content_hash': content_hash,
                'quality_score': round(quality_score, 1),
                'grade': grade,
                'readability': readability,
                'keyword_analysis': keyword_analysis
            },
            'structure': structure_analysis,
            'links': {
                'internal_links_count': len(internal_links),
                'external_links_count': len(external_links),
                'nofollow_links_count': len(nofollow_links),
                'internal_links': internal_links[:20],  # Limit for response
                'external_links': external_links[:10]
            },
            'images': image_analysis,
            'multimedia': {
                'videos': video_count,
                'lists': len(ul_lists) + len(ol_lists),
                'tables': len(tables),
                'forms': len(forms)
            },
            'meta': {
                'meta_description': meta_desc_text,
                'meta_description_length': meta_desc_length,
                'has_publication_date': has_date
            },
            'issues': issues,
            'recommendations': [r for r in recommendations if r],  # Remove None values
            'timestamp': datetime.now().isoformat()
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

