"""
Rank Tracker Module
Track keyword rankings over time
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import List, Dict, Optional

rank_tracker_bp = Blueprint('rank_tracker', __name__, url_prefix='/rank-tracker')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def get_rankings_file(username: str) -> Path:
    """Get rankings storage file for user"""
    storage_dir = Path(__file__).parent.parent.parent / 'data' / 'rankings'
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir / f'{username}_rankings.json'


def load_rankings(username: str) -> Dict:
    """Load user's rankings"""
    file_path = get_rankings_file(username)
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'keywords': {}, 'tracking_history': []}
    return {'keywords': {}, 'tracking_history': []}


def save_rankings(username: str, data: Dict):
    """Save user's rankings"""
    file_path = get_rankings_file(username)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@rank_tracker_bp.route('/')
@login_required
def rank_tracker_page():
    """Rank Tracker main page"""
    username = session.get("user")
    rankings = load_rankings(username)
    return render_template('rank_tracker.html', 
                         keywords=rankings.get('keywords', {}),
                         history=rankings.get('tracking_history', []))


@rank_tracker_bp.route('/api/keywords', methods=['GET'])
@login_required
def get_keywords():
    """Get tracked keywords"""
    username = session.get("user")
    rankings = load_rankings(username)
    return jsonify({
        'success': True,
        'keywords': rankings.get('keywords', {})
    })


@rank_tracker_bp.route('/api/keywords', methods=['POST'])
@login_required
def add_keyword():
    """Add keyword to track"""
    username = session.get("user")
    data = request.json or {}
    keyword = data.get('keyword')
    url = data.get('url')
    
    if not keyword:
        return jsonify({'error': 'Keyword is required'}), 400
    
    rankings = load_rankings(username)
    
    if keyword not in rankings['keywords']:
        rankings['keywords'][keyword] = {
            'url': url or '',
            'created_at': datetime.now().isoformat(),
            'rankings': []
        }
    
    save_rankings(username, rankings)
    
    return jsonify({
        'success': True,
        'message': f'Keyword "{keyword}" added to tracking'
    })


@rank_tracker_bp.route('/api/keywords/<keyword>', methods=['DELETE'])
@login_required
def delete_keyword(keyword):
    """Remove keyword from tracking"""
    username = session.get("user")
    rankings = load_rankings(username)
    
    if keyword in rankings['keywords']:
        del rankings['keywords'][keyword]
        save_rankings(username, rankings)
        return jsonify({'success': True, 'message': f'Keyword "{keyword}" removed'})
    
    return jsonify({'error': 'Keyword not found'}), 404


@rank_tracker_bp.route('/api/rankings', methods=['POST'])
@login_required
def add_ranking():
    """Add ranking data for a keyword"""
    username = session.get("user")
    data = request.json or {}
    keyword = data.get('keyword')
    rank = data.get('rank')
    url = data.get('url')
    
    if not keyword or rank is None:
        return jsonify({'error': 'Keyword and rank are required'}), 400
    
    rankings = load_rankings(username)
    
    if keyword not in rankings['keywords']:
        rankings['keywords'][keyword] = {
            'url': url or '',
            'created_at': datetime.now().isoformat(),
            'rankings': []
        }
    
    ranking_entry = {
        'rank': int(rank),
        'url': url or '',
        'date': datetime.now().isoformat()
    }
    
    rankings['keywords'][keyword]['rankings'].append(ranking_entry)
    
    # Keep last 100 entries per keyword
    if len(rankings['keywords'][keyword]['rankings']) > 100:
        rankings['keywords'][keyword]['rankings'] = rankings['keywords'][keyword]['rankings'][-100:]
    
    # Add to history
    rankings['tracking_history'].append({
        'keyword': keyword,
        'rank': int(rank),
        'date': datetime.now().isoformat()
    })
    
    # Keep last 1000 history entries
    if len(rankings['tracking_history']) > 1000:
        rankings['tracking_history'] = rankings['tracking_history'][-1000:]
    
    save_rankings(username, rankings)
    
    return jsonify({
        'success': True,
        'message': f'Ranking added for "{keyword}"'
    })


@rank_tracker_bp.route('/api/rankings/<keyword>', methods=['GET'])
@login_required
def get_ranking_history(keyword):
    """Get ranking history for a keyword"""
    username = session.get("user")
    rankings = load_rankings(username)
    
    if keyword not in rankings['keywords']:
        return jsonify({'error': 'Keyword not found'}), 404
    
    return jsonify({
        'success': True,
        'keyword': keyword,
        'history': rankings['keywords'][keyword]['rankings']
    })

