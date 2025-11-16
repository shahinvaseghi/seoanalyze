"""
Site Audit Module
Comprehensive site audit combining all analyzers
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any
import time

from app.core.seo_analyzer import SEOAnalyzer
from app.core.cwv_analyzer import CWVAnalyzer
from app.core.cro_analyzer import CROAnalyzer
from app.core.eeat_analyzer import EEATAnalyzer
from app.core.local_seo_analyzer import LocalSEOAnalyzer
from app.core.intent_analyzer import IntentAnalyzer
from app.core.advanced_seo_tools import AdvancedSEOTools

site_audit_bp = Blueprint('site_audit', __name__, url_prefix='/site-audit')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


@site_audit_bp.route('/')
@login_required
def site_audit_page():
    """Site Audit main page"""
    return render_template('site_audit.html')


@site_audit_bp.route('/api/audit', methods=['POST'])
@login_required
def run_audit():
    """Run comprehensive site audit"""
    data = request.json or {}
    url = data.get('url')
    audit_type = data.get('type', 'full')  # full, quick, technical, content
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Fetch page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = {
            'url': url,
            'timestamp': time.time(),
            'audit_type': audit_type
        }
        
        # Basic SEO Analysis
        seo_analyzer = SEOAnalyzer()
        basic_seo = seo_analyzer.analyze_competitor(url, keywords=None)
        results['basic_seo'] = basic_seo
        
        # Technical SEO
        if audit_type in ['full', 'technical']:
            advanced_tools = AdvancedSEOTools()
            technical = advanced_tools.technical_seo_audit(url)
            results['technical_seo'] = technical
        
        # Core Web Vitals
        if audit_type in ['full', 'technical']:
            cwv_analyzer = CWVAnalyzer()
            response_time = response.elapsed.total_seconds()
            cwv = cwv_analyzer.analyze_cwv(soup, url, response_time)
            results['core_web_vitals'] = {
                'lcp': cwv.cwv_metrics.lcp if cwv.cwv_metrics else None,
                'inp': cwv.cwv_metrics.inp if cwv.cwv_metrics else None,
                'cls': cwv.cwv_metrics.cls if cwv.cwv_metrics else None,
                'fcp': cwv.cwv_metrics.fcp if cwv.cwv_metrics else None,
                'ttfb': cwv.cwv_metrics.ttfb if cwv.cwv_metrics else None,
                'overall_score': cwv.overall_score,
                'grade': cwv.grade
            }
        
        # CRO Analysis
        if audit_type in ['full', 'conversion']:
            cro_analyzer = CROAnalyzer()
            cro = cro_analyzer.analyze_cro(soup, url)
            results['cro'] = {
                'cta_analysis': {
                    'total_ctas': cro.cta_analysis.total_ctas,
                    'above_fold_ctas': cro.cta_analysis.above_fold_ctas,
                    'recommendations': cro.cta_analysis.recommendations
                },
                'form_analysis': {
                    'total_forms': cro.form_analysis.total_forms,
                    'avg_fields': cro.form_analysis.avg_fields,
                    'recommendations': cro.form_analysis.recommendations
                },
                'trust_signals': {
                    'trust_score': cro.trust_signals.trust_score,
                    'has_phone': cro.trust_signals.has_phone,
                    'has_email': cro.trust_signals.has_email,
                    'has_reviews': cro.trust_signals.has_reviews
                },
                'accessibility': {
                    'score': cro.accessibility.score,
                    'grade': cro.accessibility.grade,
                    'passed': cro.accessibility.passed,
                    'failed': cro.accessibility.failed,
                    'warnings': cro.accessibility.warnings,
                    'aria_issues': cro.accessibility.aria_issues if hasattr(cro.accessibility, 'aria_issues') else []
                }
            }
        
        # E-E-A-T Analysis
        if audit_type in ['full', 'content']:
            eeat_analyzer = EEATAnalyzer()
            eeat = eeat_analyzer.analyze_eeat(soup, url)
            results['eeat'] = {
                'overall_score': eeat['overall_score'],
                'overall_grade': eeat['overall_grade'],
                'expertise': eeat['expertise'],
                'experience': eeat['experience'],
                'authoritativeness': eeat['authoritativeness'],
                'trustworthiness': eeat['trustworthiness']
            }
        
        # Local SEO Analysis
        if audit_type in ['full', 'local']:
            local_seo_analyzer = LocalSEOAnalyzer()
            local_seo = local_seo_analyzer.analyze_local_seo(soup, url)
            results['local_seo'] = {
                'nap_consistency': {
                    'consistent': local_seo.nap_consistency.consistent,
                    'score': local_seo.nap_consistency.score,
                    'issues': local_seo.nap_consistency.issues
                },
                'google_maps': {
                    'has_embedded_map': local_seo.google_maps.has_embedded_map,
                    'has_maps_url': bool(local_seo.google_maps.maps_url)
                },
                'geo_schema': {
                    'has_geo_coordinates': local_seo.geo_schema.has_geo_coordinates,
                    'has_area_served': local_seo.geo_schema.has_area_served
                },
                'overall_score': local_seo.overall_score
            }
        
        # Intent Analysis
        if audit_type in ['full', 'content']:
            intent_analyzer = IntentAnalyzer()
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ''
            h1 = soup.find('h1')
            h1_text = h1.get_text().strip() if h1 else ''
            content_text = soup.get_text()[:1000] if soup else ''
            intent, confidence = intent_analyzer.detect_intent(title_text, url, content_text, [h1_text] if h1_text else [])
            results['intent'] = {
                'primary_intent': intent.value if hasattr(intent, 'value') else str(intent),
                'confidence': confidence,
                'signals': {}
            }
        
        # Calculate overall score
        scores = []
        if 'basic_seo' in results and results['basic_seo']:
            scores.append(70)  # Basic SEO baseline
        
        if 'core_web_vitals' in results:
            scores.append(results['core_web_vitals'].get('overall_score', 0))
        
        if 'cro' in results:
            scores.append(results['cro']['trust_signals'].get('trust_score', 0))
        
        if 'eeat' in results:
            scores.append(results['eeat'].get('overall_score', 0))
        
        if 'local_seo' in results:
            scores.append(results['local_seo'].get('overall_score', 0))
        
        results['overall_score'] = round(sum(scores) / len(scores), 1) if scores else 0
        
        # Generate priority actions
        priority_actions = []
        if 'core_web_vitals' in results and results['core_web_vitals'].get('overall_score', 0) < 70:
            priority_actions.append({
                'priority': 'high',
                'category': 'Performance',
                'action': 'Improve Core Web Vitals scores for better user experience'
            })
        
        if 'cro' in results and results['cro']['cta_analysis'].get('total_ctas', 0) == 0:
            priority_actions.append({
                'priority': 'high',
                'category': 'Conversion',
                'action': 'Add Call-to-Action buttons to improve conversions'
            })
        
        if 'eeat' in results and results['eeat'].get('overall_score', 0) < 60:
            priority_actions.append({
                'priority': 'medium',
                'category': 'Content',
                'action': 'Improve E-E-A-T signals for better content quality'
            })
        
        results['priority_actions'] = priority_actions
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except requests.RequestException as e:
        import traceback
        print(f"Request error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to fetch URL: {str(e)}', 'success': False}), 500
    except Exception as e:
        import traceback
        print(f"Audit error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Audit failed: {str(e)}', 'success': False, 'traceback': traceback.format_exc()}), 500

