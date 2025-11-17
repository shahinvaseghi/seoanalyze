"""
Local SEO Analysis Module
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import requests
from bs4 import BeautifulSoup
import re

from app.core.local_seo_analyzer import LocalSEOAnalyzer
from app.core.google_custom_search import GoogleCustomSearch

local_seo_bp = Blueprint('local_seo', __name__, url_prefix='/local-seo')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def _check_city_keywords(soup: BeautifulSoup, city: str) -> dict:
    """Check if city keywords are present in page"""
    page_text = soup.get_text().lower()
    city_lower = city.lower()
    
    # Check in different locations
    title = soup.find('title')
    title_text = title.get_text().lower() if title else ''
    
    h1_tags = soup.find_all('h1')
    h1_text = ' '.join([h.get_text().lower() for h in h1_tags])
    
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    meta_text = meta_desc.get('content', '').lower() if meta_desc else ''
    
    return {
        'in_title': city_lower in title_text,
        'in_h1': city_lower in h1_text,
        'in_meta_description': city_lower in meta_text,
        'in_content': city_lower in page_text,
        'count_in_content': page_text.count(city_lower)
    }


def _calculate_city_optimization(soup: BeautifulSoup, city: str) -> float:
    """Calculate city-specific optimization score"""
    score = 0.0
    city_keywords = _check_city_keywords(soup, city)
    
    # Title (30 points)
    if city_keywords['in_title']:
        score += 30
    
    # H1 (25 points)
    if city_keywords['in_h1']:
        score += 25
    
    # Meta description (20 points)
    if city_keywords['in_meta_description']:
        score += 20
    
    # Content mentions (25 points, max 25)
    content_score = min(25, city_keywords['count_in_content'] * 2)
    score += content_score
    
    return round(score, 1)


def _generate_city_recommendations(soup: BeautifulSoup, city: str, province: str = None) -> list:
    """Generate city-specific recommendations"""
    recommendations = []
    city_keywords = _check_city_keywords(soup, city)
    
    if not city_keywords['in_title']:
        recommendations.append(f"Add '{city}' to page title for better local SEO")
    
    if not city_keywords['in_h1']:
        recommendations.append(f"Include '{city}' in H1 heading")
    
    if not city_keywords['in_meta_description']:
        recommendations.append(f"Add '{city}' to meta description")
    
    if city_keywords['count_in_content'] < 3:
        recommendations.append(f"Mention '{city}' at least 3-5 times in page content")
    
    if province and province not in soup.get_text().lower():
        recommendations.append(f"Consider mentioning '{province}' in content")
    
    return recommendations


@local_seo_bp.route('/')
@login_required
def local_seo_page():
    """Local SEO Analysis main page"""
    return render_template('local_seo.html')


@local_seo_bp.route('/api/analyze', methods=['POST'])
@login_required
def analyze_local_seo():
    """Analyze Local SEO for a URL"""
    data = request.json or {}
    url = data.get('url')
    business_name = data.get('business_name')
    province = data.get('province')
    city = data.get('city')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        local_seo_analyzer = LocalSEOAnalyzer()
        local_seo_report = local_seo_analyzer.analyze_local_seo(soup, url, business_name)
        
        # City-specific analysis
        city_analysis = {}
        if city:
            city_analysis = {
                'target_city': city,
                'province': province,
                'city_keywords_found': _check_city_keywords(soup, city),
                'city_optimization_score': _calculate_city_optimization(soup, city),
                'recommendations': _generate_city_recommendations(soup, city, province)
            }
        
        return jsonify({
            'success': True,
            'url': url,
            'nap_consistency': {
                'name': local_seo_report.nap_consistency.name,
                'address': local_seo_report.nap_consistency.address,
                'phone': local_seo_report.nap_consistency.phone,
                'email': local_seo_report.nap_consistency.email,
                'consistent': local_seo_report.nap_consistency.consistent,
                'score': local_seo_report.nap_consistency.score,
                'issues': local_seo_report.nap_consistency.issues
            },
            'google_maps': {
                'has_embedded_map': local_seo_report.google_maps.has_embedded_map,
                'place_id': local_seo_report.google_maps.place_id,
                'maps_url': local_seo_report.google_maps.maps_url,
                'has_utm_tracking': local_seo_report.google_maps.has_utm_tracking,
                'recommendations': local_seo_report.google_maps.recommendations
            },
            'geo_schema': {
                'has_geo_coordinates': local_seo_report.geo_schema.has_geo_coordinates,
                'latitude': local_seo_report.geo_schema.latitude,
                'longitude': local_seo_report.geo_schema.longitude,
                'has_area_served': local_seo_report.geo_schema.has_area_served,
                'areas_served': local_seo_report.geo_schema.areas_served if hasattr(local_seo_report.geo_schema, 'areas_served') else [],
                'has_service_area': local_seo_report.geo_schema.has_service_area if hasattr(local_seo_report.geo_schema, 'has_service_area') else False,
                'service_radius': local_seo_report.geo_schema.service_radius if hasattr(local_seo_report.geo_schema, 'service_radius') else None,
                'recommendations': local_seo_report.geo_schema.recommendations if hasattr(local_seo_report.geo_schema, 'recommendations') else []
            },
            'local_keywords': local_seo_report.local_keywords if hasattr(local_seo_report, 'local_keywords') else [],
            'citations': [
                {
                    'platform': c.platform,
                    'url': c.url,
                    'priority': c.priority,
                    'category': c.category
                } for c in (local_seo_report.citations_needed if hasattr(local_seo_report, 'citations_needed') else [])
            ],
            'overall_score': local_seo_report.overall_score,
            'grade': local_seo_report.grade,
            'priority_actions': local_seo_report.priority_actions if hasattr(local_seo_report, 'priority_actions') else [],
            'city_analysis': city_analysis if city_analysis else None
        })
        
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Local SEO analysis failed: {str(e)}'}), 500


@local_seo_bp.route('/api/find-competitors', methods=['POST'])
@login_required
def find_competitors():
    """Find competitors in a specific city"""
    data = request.json or {}
    business_type = data.get('business_type')  # e.g., "دندانپزشک", "کلینیک", "مطب"
    city = data.get('city')
    province = data.get('province')
    max_results = int(data.get('max_results', 10))
    
    if not business_type or not city:
        return jsonify({'error': 'Business type and city are required'}), 400
    
    try:
        # Build search query
        query = f"{business_type} {city}"
        if province:
            query += f" {province}"
        
        # Use Google Custom Search to find competitors
        search_client = GoogleCustomSearch()
        search_results = search_client.search(
            query=query,
            num_results=min(max_results, 10),
            country='ir',
            language='fa'
        )
        
        if not search_results.get('success'):
            return jsonify({
                'error': search_results.get('error', 'Failed to search for competitors'),
                'success': False
            }), 500
        
        competitors = []
        for item in search_results.get('items', []):
            competitors.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'position': item.get('position', 0)
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'city': city,
            'province': province,
            'competitors_found': len(competitors),
            'competitors': competitors,
            'daily_queries_used': search_results.get('daily_queries_used', 0)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to find competitors: {str(e)}'}), 500


@local_seo_bp.route('/api/compare-competitors', methods=['POST'])
@login_required
def compare_competitors():
    """Compare Local SEO with competitors in a city"""
    data = request.json or {}
    url = data.get('url')
    business_type = data.get('business_type')
    city = data.get('city')
    province = data.get('province')
    competitor_urls = data.get('competitor_urls', [])
    
    if not url or not city:
        return jsonify({'error': 'URL and city are required'}), 400
    
    try:
        # If competitor URLs not provided, find them using Google Custom Search
        if not competitor_urls and business_type:
            query = f"{business_type} {city}"
            if province:
                query += f" {province}"
            
            search_client = GoogleCustomSearch()
            search_results = search_client.search(
                query=query,
                num_results=10,
                country='ir',
                language='fa'
            )
            
            if search_results.get('success'):
                competitor_urls = [item.get('link', '') for item in search_results.get('items', [])[:5] if item.get('link')]
        
        # Analyze target URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        local_seo_analyzer = LocalSEOAnalyzer()
        target_report = local_seo_analyzer.analyze_local_seo(soup, url)
        target_city_score = _calculate_city_optimization(soup, city) if city else 0
        
        # Analyze competitors
        competitor_reports = []
        for comp_url in competitor_urls[:5]:  # Limit to 5 competitors
            try:
                comp_response = requests.get(comp_url, headers=headers, timeout=10)
                comp_response.raise_for_status()
                comp_soup = BeautifulSoup(comp_response.content, 'html.parser')
                comp_report = local_seo_analyzer.analyze_local_seo(comp_soup, comp_url)
                comp_city_score = _calculate_city_optimization(comp_soup, city) if city else 0
                
                competitor_reports.append({
                    'url': comp_url,
                    'overall_score': comp_report.overall_score,
                    'city_score': comp_city_score,
                    'has_google_maps': comp_report.google_maps.has_embedded_map,
                    'has_geo_schema': comp_report.geo_schema.has_geo_coordinates,
                    'nap_score': comp_report.nap_consistency.score
                })
            except:
                continue
        
        # Calculate comparison
        avg_competitor_score = sum(c['overall_score'] for c in competitor_reports) / len(competitor_reports) if competitor_reports else 0
        avg_city_score = sum(c['city_score'] for c in competitor_reports) / len(competitor_reports) if competitor_reports else 0
        
        comparison = {
            'target': {
                'url': url,
                'overall_score': target_report.overall_score,
                'city_score': target_city_score
            },
            'competitors': competitor_reports,
            'average_competitor_score': round(avg_competitor_score, 1),
            'average_city_score': round(avg_city_score, 1),
            'target_vs_competitors': {
                'score_difference': round(target_report.overall_score - avg_competitor_score, 1),
                'city_score_difference': round(target_city_score - avg_city_score, 1),
                'position': 'above' if target_report.overall_score > avg_competitor_score else 'below'
            }
        }
        
        return jsonify({
            'success': True,
            'city': city,
            'province': province,
            'comparison': comparison
        })
        
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Comparison failed: {str(e)}'}), 500
