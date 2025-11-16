"""
CRO (Conversion Rate Optimization) Analysis Module
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import requests
from bs4 import BeautifulSoup

from app.core.cro_analyzer import CROAnalyzer

cro_analysis_bp = Blueprint('cro_analysis', __name__, url_prefix='/cro-analysis')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


@cro_analysis_bp.route('/')
@login_required
def cro_analysis_page():
    """CRO Analysis main page"""
    return render_template('cro_analysis.html')


@cro_analysis_bp.route('/api/analyze', methods=['POST'])
@login_required
def analyze_cro():
    """Analyze CRO for a URL"""
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
        
        cro_analyzer = CROAnalyzer()
        cro_report = cro_analyzer.analyze_cro(soup, url)
        
        return jsonify({
            'success': True,
            'url': url,
            'cta_analysis': {
                'total_ctas': cro_report.cta_analysis.total_ctas,
                'cta_types': cro_report.cta_analysis.cta_types,
                'above_fold_ctas': cro_report.cta_analysis.above_fold_ctas,
                'optimal_placement': cro_report.cta_analysis.optimal_placement,
                'recommendations': cro_report.cta_analysis.recommendations
            },
            'form_analysis': {
                'total_forms': cro_report.form_analysis.total_forms,
                'avg_fields': cro_report.form_analysis.avg_fields,
                'forms': cro_report.form_analysis.forms,
                'recommendations': cro_report.form_analysis.recommendations
            },
            'trust_signals': {
                'has_phone': cro_report.trust_signals.has_phone,
                'has_address': cro_report.trust_signals.has_address,
                'has_email': cro_report.trust_signals.has_email,
                'has_social_proof': cro_report.trust_signals.has_social_proof,
                'has_credentials': cro_report.trust_signals.has_credentials,
                'has_certifications': cro_report.trust_signals.has_certifications,
                'has_reviews': cro_report.trust_signals.has_reviews,
                'has_testimonials': cro_report.trust_signals.has_testimonials,
                'has_secure_badges': cro_report.trust_signals.has_secure_badges,
                'trust_score': cro_report.trust_signals.trust_score,
                'elements': cro_report.trust_signals.elements
            },
            'accessibility': {
                'score': cro_report.accessibility.score,
                'has_alt_text': cro_report.accessibility.has_alt_text,
                'has_aria_labels': cro_report.accessibility.has_aria_labels,
                'has_keyboard_navigation': cro_report.accessibility.has_keyboard_navigation,
                'has_contrast': cro_report.accessibility.has_contrast,
                'issues': cro_report.accessibility.issues,
                'recommendations': cro_report.accessibility.recommendations
            },
            'overall_score': cro_report.overall_score,
            'grade': cro_report.grade
        })
        
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'CRO analysis failed: {str(e)}'}), 500

