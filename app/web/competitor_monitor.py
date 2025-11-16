"""
Competitor Monitor Module
Track competitor changes over time
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import List, Dict
import hashlib

competitor_monitor_bp = Blueprint('competitor_monitor', __name__, url_prefix='/competitor-monitor')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def get_monitoring_file(username: str) -> Path:
    """Get monitoring storage file for user"""
    storage_dir = Path(__file__).parent.parent.parent / 'data' / 'monitoring'
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir / f'{username}_competitors.json'


def load_monitoring(username: str) -> Dict:
    """Load user's competitor monitoring data"""
    file_path = get_monitoring_file(username)
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'competitors': {}, 'snapshots': []}
    return {'competitors': {}, 'snapshots': []}


def save_monitoring(username: str, data: Dict):
    """Save user's monitoring data"""
    file_path = get_monitoring_file(username)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_page_snapshot(url: str) -> Dict:
    """Get snapshot of a page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract key elements
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ''
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_desc_text = meta_desc.get('content', '') if meta_desc else ''
        
        h1 = soup.find('h1')
        h1_text = h1.get_text().strip() if h1 else ''
        
        # Calculate content hash
        main_content = soup.get_text()[:1000]  # First 1000 chars
        content_hash = hashlib.md5(main_content.encode()).hexdigest()
        
        return {
            'url': url,
            'title': title_text,
            'meta_description': meta_desc_text,
            'h1': h1_text,
            'content_hash': content_hash,
            'timestamp': datetime.now().isoformat()
        }
    except:
        return None


@competitor_monitor_bp.route('/')
@login_required
def competitor_monitor_page():
    """Competitor Monitor main page"""
    username = session.get("user")
    monitoring = load_monitoring(username)
    return render_template('competitor_monitor.html',
                         competitors=monitoring.get('competitors', {}))


@competitor_monitor_bp.route('/api/competitors', methods=['GET'])
@login_required
def get_competitors():
    """Get tracked competitors"""
    username = session.get("user")
    monitoring = load_monitoring(username)
    return jsonify({
        'success': True,
        'competitors': monitoring.get('competitors', {})
    })


@competitor_monitor_bp.route('/api/competitors', methods=['POST'])
@login_required
def add_competitor():
    """Add competitor to monitor"""
    username = session.get("user")
    data = request.json or {}
    competitor_url = data.get('url')
    competitor_name = data.get('name', '')
    
    if not competitor_url:
        return jsonify({'error': 'URL is required'}), 400
    
    monitoring = load_monitoring(username)
    
    if competitor_url not in monitoring['competitors']:
        snapshot = get_page_snapshot(competitor_url)
        if snapshot:
            monitoring['competitors'][competitor_url] = {
                'name': competitor_name or competitor_url,
                'created_at': datetime.now().isoformat(),
                'last_checked': datetime.now().isoformat(),
                'snapshots': [snapshot],
                'changes': []
            }
            save_monitoring(username, monitoring)
            return jsonify({
                'success': True,
                'message': f'Competitor "{competitor_name or competitor_url}" added to monitoring'
            })
        else:
            return jsonify({'error': 'Failed to fetch competitor page'}), 500
    
    return jsonify({'error': 'Competitor already being monitored'}), 400


@competitor_monitor_bp.route('/api/competitors/<path:url>', methods=['DELETE'])
@login_required
def remove_competitor(url):
    """Remove competitor from monitoring"""
    username = session.get("user")
    monitoring = load_monitoring(username)
    
    if url in monitoring['competitors']:
        del monitoring['competitors'][url]
        save_monitoring(username, monitoring)
        return jsonify({'success': True, 'message': 'Competitor removed from monitoring'})
    
    return jsonify({'error': 'Competitor not found'}), 404


@competitor_monitor_bp.route('/api/check', methods=['POST'])
@login_required
def check_competitors():
    """Check all competitors for changes"""
    username = session.get("user")
    data = request.json or {}
    competitor_url = data.get('url')  # Optional: check specific competitor
    
    monitoring = load_monitoring(username)
    
    if competitor_url:
        competitors_to_check = {competitor_url: monitoring['competitors'].get(competitor_url)}
    else:
        competitors_to_check = monitoring['competitors']
    
    changes_found = []
    
    for url, competitor_data in competitors_to_check.items():
        if not competitor_data:
            continue
        
        current_snapshot = get_page_snapshot(url)
        if not current_snapshot:
            continue
        
        last_snapshot = competitor_data['snapshots'][-1] if competitor_data['snapshots'] else None
        
        if last_snapshot:
            changes = []
            
            if current_snapshot['title'] != last_snapshot.get('title', ''):
                changes.append({
                    'type': 'title',
                    'old': last_snapshot.get('title', ''),
                    'new': current_snapshot['title']
                })
            
            if current_snapshot['meta_description'] != last_snapshot.get('meta_description', ''):
                changes.append({
                    'type': 'meta_description',
                    'old': last_snapshot.get('meta_description', ''),
                    'new': current_snapshot['meta_description']
                })
            
            if current_snapshot['h1'] != last_snapshot.get('h1', ''):
                changes.append({
                    'type': 'h1',
                    'old': last_snapshot.get('h1', ''),
                    'new': current_snapshot['h1']
                })
            
            if current_snapshot['content_hash'] != last_snapshot.get('content_hash', ''):
                changes.append({
                    'type': 'content',
                    'message': 'Content has changed'
                })
            
            if changes:
                competitor_data['changes'].extend(changes)
                changes_found.append({
                    'url': url,
                    'name': competitor_data.get('name', url),
                    'changes': changes
                })
        
        competitor_data['snapshots'].append(current_snapshot)
        competitor_data['last_checked'] = datetime.now().isoformat()
        
        # Keep last 50 snapshots
        if len(competitor_data['snapshots']) > 50:
            competitor_data['snapshots'] = competitor_data['snapshots'][-50:]
    
    save_monitoring(username, monitoring)
    
    return jsonify({
        'success': True,
        'changes_found': len(changes_found),
        'changes': changes_found,
        'timestamp': datetime.now().isoformat()
    })

