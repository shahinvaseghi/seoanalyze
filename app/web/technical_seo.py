from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from datetime import datetime
from pathlib import Path
import json

from app.core.advanced_seo_tools import AdvancedSEOTools

technical_seo_bp = Blueprint('technical_seo', __name__)
advanced_tools = AdvancedSEOTools()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


@technical_seo_bp.route('/technical-seo/')
@login_required
def technical_seo_page():
    """Technical SEO analysis page"""
    return render_template('technical_seo.html')


@technical_seo_bp.route('/api/analyze/technical', methods=['POST'])
@login_required
def analyze_technical():
    """Technical SEO audit API"""
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        print(f"🔧 Starting technical audit for: {url}")
        audit = advanced_tools.technical_seo_audit(url)
        
        if audit is None:
            return jsonify({'error': 'Technical audit failed to complete. Please check the URL and try again.'}), 500
        
        print(f"✅ Technical audit completed successfully")
        
        # Format for user-friendly display
        formatted_results = format_technical_results_web(audit)
        
        # Save JSON
        results_dir = Path('results')
        results_dir.mkdir(exist_ok=True)
        output_file = results_dir / 'technical_audit.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(audit, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Results saved to: {output_file}")
        
        return jsonify({'status': 'success', 'results': formatted_results, 'raw_results': audit})
        
    except Exception as e:
        print(f"❌ Technical audit error: {str(e)}")
        return jsonify({'error': f'Technical audit failed: {str(e)}'}), 500


def format_technical_results_web(audit):
    """Format technical results for web display"""
    if not audit or 'checks' not in audit:
        return {
            'error': 'Invalid audit data',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'score': 0,
            'grade': 'F',
            'passed': [],
            'failed': [],
            'warnings': [],
            'priority_actions': []
        }
    
    passed = []
    failed = []
    warnings = []
    
    for check_name, check_data in audit['checks'].items():
        if not check_data or 'message' not in check_data:
            continue
            
        check_info = {
            'name': check_name.upper(),
            'message': check_data.get('message', ''),
            'importance': check_data.get('importance', 'MEDIUM'),
            'details': check_data  # Include full check_data for detailed display
        }
        
        # Check status
        status = check_data.get('status', False)
        exists = check_data.get('exists', False)
        optimal = check_data.get('optimal', False)
        
        if status or exists or optimal:
            passed.append(check_info)
        elif check_data.get('importance') == 'HIGH':
            failed.append(check_info)
        else:
            warnings.append(check_info)
    
    return {
        'timestamp': audit.get('timestamp', datetime.now().isoformat()),
        'score': audit['score']['score'] if 'score' in audit else 0,
        'grade': audit['score']['grade'] if 'score' in audit else 'F',
        'passed': passed,
        'failed': failed,
        'warnings': warnings,
        'priority_actions': audit.get('priority_actions', []),
        'checks': audit.get('checks', {})  # Include raw checks for detailed display
    }

