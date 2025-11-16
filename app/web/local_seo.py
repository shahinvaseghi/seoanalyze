"""
Local SEO Analysis Module
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import requests
from bs4 import BeautifulSoup

from app.core.local_seo_analyzer import LocalSEOAnalyzer

local_seo_bp = Blueprint('local_seo', __name__, url_prefix='/local-seo')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


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
                'area_served': local_seo_report.geo_schema.area_served
            },
            'local_keywords': local_seo_report.local_keywords,
            'citations': [
                {
                    'platform': c.platform,
                    'url': c.url,
                    'priority': c.priority,
                    'category': c.category
                } for c in local_seo_report.citations
            ],
            'overall_score': local_seo_report.overall_score,
            'grade': local_seo_report.grade,
            'recommendations': local_seo_report.recommendations
        })
        
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Local SEO analysis failed: {str(e)}'}), 500

