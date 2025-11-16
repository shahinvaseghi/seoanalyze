"""
E-E-A-T (Expertise, Experience, Authoritativeness, Trustworthiness) Analysis Module
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import requests
from bs4 import BeautifulSoup

from app.core.eeat_analyzer import EEATAnalyzer

eeat_analysis_bp = Blueprint('eeat_analysis', __name__, url_prefix='/eeat-analysis')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


@eeat_analysis_bp.route('/')
@login_required
def eeat_analysis_page():
    """E-E-A-T Analysis main page"""
    return render_template('eeat_analysis.html')


@eeat_analysis_bp.route('/api/analyze', methods=['POST'])
@login_required
def analyze_eeat():
    """Analyze E-E-A-T for a URL"""
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
        
        eeat_analyzer = EEATAnalyzer()
        eeat_report = eeat_analyzer.analyze_eeat(soup, url)
        
        return jsonify({
            'success': True,
            'url': url,
            'overall_score': eeat_report['overall_score'],
            'overall_grade': eeat_report['overall_grade'],
            'expertise': eeat_report['expertise'],
            'experience': eeat_report['experience'],
            'authoritativeness': eeat_report['authoritativeness'],
            'trustworthiness': eeat_report['trustworthiness'],
            'recommendations': eeat_report.get('recommendations', [])
        })
        
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'E-E-A-T analysis failed: {str(e)}'}), 500

