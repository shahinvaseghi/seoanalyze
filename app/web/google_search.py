"""
Google Custom Search API Module
SERP analysis and keyword ranking tracking
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from datetime import datetime
import json
from pathlib import Path

from app.core.google_custom_search import GoogleCustomSearch
from app.core.duckduckgo_search import DuckDuckGoSearch

google_search_bp = Blueprint('google_search', __name__, url_prefix='/google-search')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


@google_search_bp.route('/')
@login_required
def google_search_page():
    """Google Custom Search main page"""
    return render_template('google_search.html')


@google_search_bp.route('/api/search', methods=['POST'])
@login_required
def search():
    """Perform search (Google Custom Search API or DuckDuckGo fallback)"""
    data = request.json or {}
    query = data.get('query')
    num_results = int(data.get('num_results', 10))
    country = data.get('country', 'us')
    language = data.get('language', 'en')
    site = data.get('site')
    use_duckduckgo = data.get('use_duckduckgo', False)  # Option to force DuckDuckGo
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        # Try DuckDuckGo if requested or if Google API fails
        if use_duckduckgo:
            search_client = DuckDuckGoSearch()
            results = search_client.search(
                query=query,
                num_results=num_results,
                country=country,
                language=language,
                site=site
            )
            return jsonify(results)
        
        # Try Google Custom Search API first
        search_client = GoogleCustomSearch()
        results = search_client.search(
            query=query,
            num_results=num_results,
            country=country,
            language=language,
            site=site
        )
        
        # If Google API fails, try DuckDuckGo as fallback
        if not results.get('success') and results.get('error_code') == 403:
            duckduckgo_client = DuckDuckGoSearch()
            duckduckgo_results = duckduckgo_client.search(
                query=query,
                num_results=num_results,
                country=country,
                language=language,
                site=site
            )
            if duckduckgo_results.get('success'):
                duckduckgo_results['fallback_message'] = 'Google API unavailable, using DuckDuckGo instead'
                return jsonify(duckduckgo_results)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({
            'error': f'Search failed: {str(e)}',
            'success': False
        }), 500


@google_search_bp.route('/api/rank', methods=['POST'])
@login_required
def find_rank():
    """Find keyword ranking for a URL"""
    data = request.json or {}
    keyword = data.get('keyword')
    target_url = data.get('url')
    country = data.get('country', 'us')
    language = data.get('language', 'en')
    max_pages = int(data.get('max_pages', 10))
    use_duckduckgo = data.get('use_duckduckgo', False)
    
    if not keyword or not target_url:
        return jsonify({'error': 'Keyword and URL are required'}), 400
    
    try:
        # Use DuckDuckGo if requested
        if use_duckduckgo:
            search_client = DuckDuckGoSearch()
            result = search_client.find_keyword_rank(
                keyword=keyword,
                target_url=target_url,
                country=country,
                language=language,
                max_pages=max_pages
            )
        else:
            # Try Google Custom Search API first
            search_client = GoogleCustomSearch()
            result = search_client.find_keyword_rank(
                keyword=keyword,
                target_url=target_url,
                country=country,
                language=language,
                max_pages=max_pages
            )
            
            # Fallback to DuckDuckGo if Google fails
            if not result.get('success'):
                duckduckgo_client = DuckDuckGoSearch()
                result = duckduckgo_client.find_keyword_rank(
                    keyword=keyword,
                    target_url=target_url,
                    country=country,
                    language=language,
                    max_pages=max_pages
                )
                if result.get('success'):
                    result['fallback_message'] = 'Google API unavailable, using DuckDuckGo instead'
        
        # If rank found, also save to rank tracker
        if result.get('success') and result.get('found'):
            # Integrate with rank tracker
            from app.web.rank_tracker import get_rankings_file, load_rankings, save_rankings
            username = session.get("user")
            rankings = load_rankings(username)
            
            if keyword not in rankings['keywords']:
                rankings['keywords'][keyword] = {
                    'url': target_url,
                    'created_at': datetime.now().isoformat(),
                    'rankings': []
                }
            
            ranking_entry = {
                'rank': result['position'],
                'url': target_url,
                'date': datetime.now().isoformat(),
                'source': 'google_custom_search'
            }
            
            rankings['keywords'][keyword]['rankings'].append(ranking_entry)
            
            # Keep last 100 entries
            if len(rankings['keywords'][keyword]['rankings']) > 100:
                rankings['keywords'][keyword]['rankings'] = rankings['keywords'][keyword]['rankings'][-100:]
            
            save_rankings(username, rankings)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Rank check failed: {str(e)}',
            'success': False
        }), 500


@google_search_bp.route('/api/serp-features', methods=['POST'])
@login_required
def serp_features():
    """Analyze SERP features for a query"""
    data = request.json or {}
    query = data.get('query')
    country = data.get('country', 'us')
    language = data.get('language', 'en')
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        search_client = GoogleCustomSearch()
        result = search_client.get_serp_features(
            query=query,
            country=country,
            language=language
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'SERP analysis failed: {str(e)}',
            'success': False
        }), 500


@google_search_bp.route('/api/compare-competitors', methods=['POST'])
@login_required
def compare_competitors():
    """Compare competitor rankings"""
    data = request.json or {}
    keyword = data.get('keyword')
    competitor_urls = data.get('competitor_urls', [])
    country = data.get('country', 'us')
    language = data.get('language', 'en')
    
    if not keyword or not competitor_urls:
        return jsonify({'error': 'Keyword and competitor URLs are required'}), 400
    
    try:
        search_client = GoogleCustomSearch()
        result = search_client.compare_competitors(
            keyword=keyword,
            competitor_urls=competitor_urls,
            country=country,
            language=language
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'Competitor comparison failed: {str(e)}',
            'success': False
        }), 500


@google_search_bp.route('/api/config', methods=['GET'])
@login_required
def get_config():
    """Get API configuration status"""
    try:
        search_client = GoogleCustomSearch()
        is_configured = bool(search_client.api_key and search_client.search_engine_id)
        
        return jsonify({
            'success': True,
            'configured': is_configured,
            'has_api_key': bool(search_client.api_key),
            'has_search_engine_id': bool(search_client.search_engine_id),
            'daily_queries_used': search_client.daily_queries,
            'daily_queries_remaining': 100 - search_client.daily_queries
        })
    except Exception as e:
        return jsonify({
            'error': f'Config check failed: {str(e)}',
            'success': False
        }), 500

