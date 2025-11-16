"""
Google Search Console Integration Routes
OAuth flow and data display for Search Console
"""

from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from functools import wraps
from datetime import datetime, timedelta
from pathlib import Path
import secrets
import json
import os
import subprocess

from app.services.storage import UserStorage
from app.services.gsc_oauth import GSCOAuthHandler
from app.core.gsc_analyzer import GSCAnalyzer

search_console_bp = Blueprint('search_console', __name__, url_prefix='/search-console')

storage = UserStorage()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("auth.login"))
        
        username = session.get("user")
        if not storage.is_admin(username):
            return jsonify({'error': 'Admin access required'}), 403
        
        return view(*args, **kwargs)
    return wrapped


@search_console_bp.route('/')
@login_required
def index():
    """
    Main Search Console page
    Shows connection status and analytics if connected
    """
    username = session.get("user")
    
    # Check if user has connected Search Console
    has_connection = storage.has_gsc_connection(username)
    
    if not has_connection:
        # Show connection page
        return render_template('search_console_connect.html', username=username)
    
    # Get user's tokens and properties
    tokens = storage.get_gsc_tokens(username)
    
    # Safety check
    if not tokens:
        print(f"⚠️ WARNING: has_connection returned True but tokens is None for user {username}")
        return render_template('search_console_connect.html', username=username)
    
    properties = tokens.get('properties', [])
    
    # Show analytics dashboard
    return render_template('search_console_dashboard.html', 
                         username=username,
                         properties=properties,
                         connected=True)


@search_console_bp.route('/help')
@login_required
def help_page():
    """
    Help page with complete setup guide in Persian and English
    """
    username = session.get("user")
    return render_template('search_console_help.html', username=username)


@search_console_bp.route('/connect')
@login_required
def connect():
    """
    Initiate OAuth flow to connect Search Console
    """
    username = session.get("user")
    
    # Prevent multiple simultaneous OAuth flows for the same user
    if 'oauth_state' in session:
        existing_username = session.get('oauth_username')
        if existing_username == username:
            print(f"⚠️ OAuth flow already in progress for user {username}")
            flash("OAuth flow already in progress. Please wait or try again in a moment.", "warning")
            return redirect(url_for('search_console.index'))
    
    try:
        oauth_handler = GSCOAuthHandler()
        
        # Generate state token for security
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        session['oauth_username'] = username
        session.permanent = True  # Ensure session persists
        
        # Create authorization URL
        redirect_uri = url_for('search_console.oauth_callback', _external=True)
        print(f"🔗 Generated redirect_uri: {redirect_uri}")
        print(f"🔗 Generated state for user {username}: {state[:20]}...")
        authorization_url, returned_state = oauth_handler.create_authorization_url(redirect_uri, state)
        
        # Verify that the returned state matches what we sent
        if returned_state != state:
            print(f"⚠️ WARNING: State mismatch in create_authorization_url! Sent: {state[:20]}..., Returned: {returned_state[:20] if returned_state else None}...")
            # Use the returned state (should match if implementation is correct)
            session['oauth_state'] = returned_state
        
        print(f"🔗 Generated authorization_url: {authorization_url[:200]}...")
        print(f"🔗 Final session state: {session.get('oauth_state')[:20] if session.get('oauth_state') else None}...")
        
        # Redirect user to Google OAuth consent page
        return redirect(authorization_url)
        
    except FileNotFoundError as e:
        flash(str(e), "error")
        return redirect(url_for('search_console.index'))
    except Exception as e:
        flash(f"Error initiating OAuth: {str(e)}", "error")
        return redirect(url_for('search_console.index'))


@search_console_bp.route('/oauth2callback')
def oauth_callback():
    """
    OAuth callback - handle authorization code from Google
    Note: NO @login_required decorator here because Google redirects here and session may be lost
    """
    print(f"🔔 OAuth callback called!")
    print(f"🔔 Request URL: {request.url}")
    print(f"🔔 Request args: {dict(request.args)}")
    session_state = session.get('oauth_state')
    request_state = request.args.get('state')
    print(f"🔔 Session state: {session_state[:30] + '...' if session_state and len(session_state) > 30 else session_state}")
    print(f"🔔 Request state: {request_state[:30] + '...' if request_state and len(request_state) > 30 else request_state}")
    print(f"🔔 Session oauth_username: {session.get('oauth_username')}")
    print(f"🔔 Session user: {session.get('user')}")
    print(f"🔔 Full session keys: {list(session.keys())}")
    print(f"🔔 Session permanent: {session.permanent}")
    
    # Get username from session (might be lost, use oauth_username as backup)
    username = session.get('oauth_username')
    if not username:
        print(f"❌ No username in session! Redirecting to login.")
        flash("Session expired. Please try connecting again.", "error")
        return redirect(url_for('auth.login'))
    
    # Verify state to prevent CSRF
    state_from_session = session.get('oauth_state')
    state_from_request = request.args.get('state')
    
    if not state_from_session or state_from_session != state_from_request:
        print(f"❌ State mismatch!")
        print(f"   Session state (length {len(state_from_session) if state_from_session else 0}): {state_from_session[:50] + '...' if state_from_session and len(state_from_session) > 50 else state_from_session}")
        print(f"   Request state (length {len(state_from_request) if state_from_request else 0}): {state_from_request[:50] + '...' if state_from_request and len(state_from_request) > 50 else state_from_request}")
        print(f"   States match: {state_from_session == state_from_request}")
        print(f"   Session ID: {session.get('_id', 'N/A')}")
        flash("Invalid OAuth state. This may happen if you clicked Connect multiple times or if your session expired. Please try connecting again.", "error")
        
        # Clear the OAuth state to allow retry
        session.pop('oauth_state', None)
        session.pop('oauth_username', None)
        
        return redirect(url_for('search_console.index'))
    
    # Get authorization code
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash(f"OAuth error: {error}", "error")
        return redirect(url_for('search_console.index'))
    
    if not code:
        flash("No authorization code received", "error")
        return redirect(url_for('search_console.index'))
    
    try:
        oauth_handler = GSCOAuthHandler()
        
        # Exchange code for tokens
        redirect_uri = url_for('search_console.oauth_callback', _external=True)
        print(f"🔗 Using redirect_uri for token exchange: {redirect_uri}")
        tokens = oauth_handler.exchange_code_for_tokens(code, redirect_uri)
        
        # Debug: Check if refresh_token is present
        if not tokens.get('refresh_token'):
            print(f"⚠️ WARNING: No refresh_token received for user {username}")
            flash("Authentication successful, but no refresh token received. Please try again.", "warning")
        else:
            print(f"✅ Refresh token received for user {username}")
        
        # Save tokens to user storage
        storage.save_gsc_tokens(username, tokens)
        print(f"✅ Tokens saved for user {username}")
        
        # Get user's Search Console properties
        try:
            def save_tokens_callback(updated_tokens):
                storage.save_gsc_tokens(username, updated_tokens)
            
            credentials, _ = oauth_handler.get_valid_credentials(tokens, save_tokens_callback)
            analyzer = GSCAnalyzer(credentials)
            properties = analyzer.list_properties()
            
            # Save properties list
            property_urls = [p['url'] if isinstance(p, dict) else p for p in properties]
            storage.save_gsc_properties(username, property_urls)
            
            flash(f"Successfully connected! Found {len(property_urls)} properties.", "success")
            
        except Exception as prop_error:
            print(f"⚠️ Could not fetch properties: {prop_error}")
            flash("Connected, but could not fetch properties. You can still use the service.", "warning")
        
        # Clear OAuth session data
        session.pop('oauth_state', None)
        session.pop('oauth_username', None)
        
        return redirect(url_for('search_console.index'))
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ OAuth callback error: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        flash(f"Error completing OAuth: {str(e)}", "error")
        return redirect(url_for('search_console.index'))


@search_console_bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    """
    Disconnect Search Console for current user
    """
    username = session.get("user")
    
    try:
        storage.disconnect_gsc(username)
        flash("Search Console disconnected successfully", "success")
    except Exception as e:
        flash(f"Error disconnecting: {str(e)}", "error")
    
    return redirect(url_for('search_console.index'))


@search_console_bp.route('/api/analytics', methods=['POST'])
@login_required
def get_analytics():
    """
    API endpoint to get Search Console analytics data
    """
    username = session.get("user")
    
    # Check if connected
    if not storage.has_gsc_connection(username):
        return jsonify({'error': 'Search Console not connected'}), 401
    
    # Get request parameters
    data = request.json or {}
    site_url = data.get('site_url')
    days = int(data.get('days', 7))
    limit = int(data.get('limit', 25000))  # Max limit from Google Search Console API
    
    if not site_url:
        return jsonify({'error': 'site_url is required'}), 400
    
    try:
        # Get user's tokens
        tokens = storage.get_gsc_tokens(username)
        
        # Create analyzer with token refresh callback
        oauth_handler = GSCOAuthHandler()
        
        def save_tokens_callback(updated_tokens):
            storage.save_gsc_tokens(username, updated_tokens)
        
        credentials, _ = oauth_handler.get_valid_credentials(tokens, save_tokens_callback)
        analyzer = GSCAnalyzer(credentials)
        
        # Get analytics data
        top_queries = analyzer.get_top_queries(site_url, days, limit)
        top_pages = analyzer.get_top_pages(site_url, days, limit)
        summary = analyzer.get_performance_summary(site_url, days)
        
        return jsonify({
            'success': True,
            'summary': summary,
            'top_queries': top_queries,
            'top_pages': top_pages,
            'period': f'{days} days'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch analytics: {str(e)}'}), 500


@search_console_bp.route('/api/properties')
@login_required
def get_properties():
    """
    API endpoint to get user's Search Console properties
    """
    username = session.get("user")
    
    if not storage.has_gsc_connection(username):
        return jsonify({'connected': False, 'properties': []})
    
    try:
        tokens = storage.get_gsc_tokens(username)
        properties = tokens.get('properties', [])
        
        return jsonify({
            'connected': True,
            'properties': properties,
            'count': len(properties)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@search_console_bp.route('/admin/setup')
@login_required
def admin_setup():
    """
    Setup page for uploading OAuth credentials
    (Available to all users in MVP)
    """
    username = session.get("user")
    
    # Check if credentials file exists
    config_dir = Path(__file__).parent.parent.parent / 'configs'
    credentials_file = config_dir / 'google_oauth_client.json'
    has_credentials = credentials_file.exists()
    
    return render_template('gsc_admin_setup.html', 
                         username=username,
                         has_credentials=has_credentials)


@search_console_bp.route('/admin/upload-credentials', methods=['POST'])
@login_required
def upload_credentials():
    """
    API endpoint to upload OAuth credentials file and restart service
    (Available to all users in MVP)
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        if not file.filename.endswith('.json'):
            return jsonify({'error': 'Only JSON files are allowed'}), 400
        
        # Read and validate JSON
        try:
            file_content = file.read()
            json_data = json.loads(file_content)
            
            # Validate structure (should have 'web' key with OAuth credentials)
            if 'web' not in json_data:
                return jsonify({'error': 'Invalid OAuth credentials file structure. Missing "web" key.'}), 400
            
            required_keys = ['client_id', 'client_secret', 'redirect_uris', 'auth_uri', 'token_uri']
            web_data = json_data['web']
            
            missing_keys = [key for key in required_keys if key not in web_data]
            if missing_keys:
                return jsonify({
                    'error': f'Invalid OAuth credentials. Missing keys: {", ".join(missing_keys)}'
                }), 400
            
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON file'}), 400
        
        # Save file to configs directory
        config_dir = Path(__file__).parent.parent.parent / 'configs'
        config_dir.mkdir(exist_ok=True)
        
        credentials_file = config_dir / 'google_oauth_client.json'
        
        with open(credentials_file, 'w') as f:
            f.write(file_content.decode('utf-8'))
        
        # Set file permissions to 600 (read/write for owner only)
        os.chmod(credentials_file, 0o600)
        
        # Restart service
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', 'seoanalyzepro'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return jsonify({
                    'success': True,
                    'message': 'فایل با موفقیت آپلود شد و سرویس راه‌اندازی مجدد شد'
                })
            else:
                # File saved but service restart failed
                return jsonify({
                    'success': True,
                    'message': 'فایل ذخیره شد اما خطا در restart سرویس. لطفاً دستی restart کنید.',
                    'restart_error': result.stderr
                })
                
        except subprocess.TimeoutExpired:
            return jsonify({
                'success': True,
                'message': 'فایل ذخیره شد. Restart سرویس timeout شد. لطفاً دستی restart کنید.'
            })
        except Exception as restart_error:
            return jsonify({
                'success': True,
                'message': f'فایل ذخیره شد اما خطا در restart: {str(restart_error)}'
            })
        
    except Exception as e:
        return jsonify({'error': f'خطا در آپلود: {str(e)}'}), 500


@search_console_bp.route('/reports/')
@login_required
def gsc_reports():
    """
    Google Search Console Reports - Advanced analytics and reporting
    """
    username = session.get("user")
    
    # Check if connected
    has_connection = storage.has_gsc_connection(username)
    
    # Get user's properties if connected
    properties = []
    if has_connection:
        try:
            tokens = storage.get_gsc_tokens(username)
            oauth_handler = GSCOAuthHandler()
            
            def save_tokens_callback(updated_tokens):
                storage.save_gsc_tokens(username, updated_tokens)
            
            credentials, _ = oauth_handler.get_valid_credentials(tokens, save_tokens_callback)
            analyzer = GSCAnalyzer(credentials)
            properties_list = analyzer.list_properties()
            properties = [prop['url'] for prop in properties_list]
        except Exception as e:
            print(f"Error fetching properties: {e}")
            properties = []
    
    return render_template('gsc_reports.html', 
                         username=username,
                         has_connection=has_connection,
                         properties=properties)


@search_console_bp.route('/reports/generate', methods=['POST'])
@login_required
def generate_reports():
    """
    Generate comprehensive GSC reports based on user requirements
    """
    username = session.get("user")
    
    if not storage.has_gsc_connection(username):
        return jsonify({'error': 'Search Console not connected'}), 401
    
    data = request.json or {}
    site_url = data.get('site_url')
    
    if not site_url:
        return jsonify({'error': 'site_url is required'}), 400
    
    try:
        # Get user's tokens
        tokens = storage.get_gsc_tokens(username)
        oauth_handler = GSCOAuthHandler()
        
        def save_tokens_callback(updated_tokens):
            storage.save_gsc_tokens(username, updated_tokens)
        
        credentials, _ = oauth_handler.get_valid_credentials(tokens, save_tokens_callback)
        analyzer = GSCAnalyzer(credentials)
        
        # Calculate date ranges - support both preset days and custom date range
        from datetime import datetime, timedelta
        
        if 'start_date' in data and 'end_date' in data:
            # Custom date range
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            days = (end_date - start_date).days + 1
        else:
            # Preset days
            days = int(data.get('days', 30))
            end_date = datetime.now().date() - timedelta(days=1)  # GSC has 1-2 day delay
            start_date = end_date - timedelta(days=days-1)
        
        # Previous period for comparison
        previous_end = start_date - timedelta(days=1)
        previous_start = previous_end - timedelta(days=days-1)
        
        # Get all pages data
        current_pages = analyzer.get_pages_data(
            site_url,
            start_date.isoformat(),
            end_date.isoformat(),
            limit=25000
        )
        
        # Get comparison data
        comparison_data = analyzer.get_pages_comparison(
            site_url,
            previous_start.isoformat(),
            previous_end.isoformat(),
            start_date.isoformat(),
            end_date.isoformat(),
            limit=25000
        )
        
        # Calculate average position change
        position_changes = []
        for item in comparison_data['comparison']:
            if item['previous_position'] > 0:  # Only pages that existed in previous period
                position_changes.append({
                    'page': item['page'],
                    'previous_position': item['previous_position'],
                    'current_position': item['current_position'],
                    'position_change': item['position_change']
                })
        
        # Sort by position change (biggest improvement = negative change)
        position_changes.sort(key=lambda x: x['position_change'])
        avg_position_change = sum(item['position_change'] for item in position_changes) / len(position_changes) if position_changes else 0
        
        # 1. Pages with highest impressions, clicks > 0, but lowest clicks
        high_imp_low_clicks = [
            p for p in current_pages 
            if p['clicks'] > 0
        ]
        high_imp_low_clicks.sort(key=lambda x: (x['impressions'], -x['clicks']), reverse=True)
        top5_high_imp_low_clicks = high_imp_low_clicks[:5]
        
        # 2. Pages with highest impressions but 0 clicks
        high_imp_zero_clicks = [
            p for p in current_pages 
            if p['clicks'] == 0 and p['impressions'] > 0
        ]
        high_imp_zero_clicks.sort(key=lambda x: x['impressions'], reverse=True)
        top5_high_imp_zero_clicks = high_imp_zero_clicks[:5]
        
        # 3. Pages with clicks decreased by more than 25%
        clicks_decreased = [
            item for item in comparison_data['comparison']
            if item['previous_clicks'] > 0 and item['clicks_change_percent'] <= -25
        ]
        clicks_decreased.sort(key=lambda x: x['clicks_change_percent'])
        top5_clicks_decreased = clicks_decreased[:5]
        
        # 4. Pages with highest clicks
        high_clicks = sorted(current_pages, key=lambda x: x['clicks'], reverse=True)
        top5_high_clicks = high_clicks[:5]
        
        # 5. Pages with lowest impressions and clicks (excluding 0)
        low_imp_clicks = [
            p for p in current_pages 
            if p['impressions'] > 0 and p['clicks'] > 0
        ]
        low_imp_clicks.sort(key=lambda x: (x['impressions'], x['clicks']))
        top5_low_imp_clicks = low_imp_clicks[:5]
        
        # 6. Pages with highest CTR
        high_ctr = sorted(current_pages, key=lambda x: x['ctr'], reverse=True)
        top5_high_ctr = high_ctr[:5]
        
        # 7. Pages with lowest CTR (excluding 0 clicks)
        low_ctr = [
            p for p in current_pages 
            if p['clicks'] > 0
        ]
        low_ctr.sort(key=lambda x: x['ctr'])
        top5_low_ctr = low_ctr[:5]
        
        # 8. Pages with 0 clicks and CTR < 10% (but impressions > 0)
        zero_clicks_low_ctr = [
            p for p in current_pages 
            if p['clicks'] == 0 and p['impressions'] > 0 and p['ctr'] < 10
        ]
        zero_clicks_low_ctr.sort(key=lambda x: x['impressions'], reverse=True)
        
        # 9. Pages with clicks and position > 6
        clicks_high_position = [
            p for p in current_pages 
            if p['clicks'] > 0 and p['position'] > 6
        ]
        clicks_high_position.sort(key=lambda x: x['position'], reverse=True)
        
        return jsonify({
            'success': True,
            'period': f'{start_date.isoformat()} to {end_date.isoformat()}',
            'previous_period': comparison_data['previous_period'],
            'current_period': comparison_data['current_period'],
            'avg_position_change': round(avg_position_change, 2),
            'position_changes': position_changes[:10],  # Top 10 for display
            'reports': {
                'high_impressions_low_clicks': top5_high_imp_low_clicks,
                'high_impressions_zero_clicks': top5_high_imp_zero_clicks,
                'clicks_decreased_25pct': top5_clicks_decreased,
                'highest_clicks': top5_high_clicks,
                'lowest_impressions_clicks': top5_low_imp_clicks,
                'highest_ctr': top5_high_ctr,
                'lowest_ctr': top5_low_ctr,
                'zero_clicks_low_ctr': zero_clicks_low_ctr,
                'clicks_high_position': clicks_high_position
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate reports: {str(e)}'}), 500


@search_console_bp.route('/reports/internal-links', methods=['POST'])
@login_required
def get_internal_links_report():
    """
    Get internal links analysis for pages from GSC
    """
    username = session.get("user")
    
    if not storage.has_gsc_connection(username):
        return jsonify({'error': 'Search Console not connected'}), 401
    
    data = request.json or {}
    site_url = data.get('site_url')
    days = int(data.get('days', 30))
    limit = int(data.get('limit', 50))  # Limit number of pages to analyze
    
    if not site_url:
        return jsonify({'error': 'site_url is required'}), 400
    
    try:
        # Get user's tokens
        tokens = storage.get_gsc_tokens(username)
        oauth_handler = GSCOAuthHandler()
        
        def save_tokens_callback(updated_tokens):
            storage.save_gsc_tokens(username, updated_tokens)
        
        credentials, _ = oauth_handler.get_valid_credentials(tokens, save_tokens_callback)
        analyzer = GSCAnalyzer(credentials)
        
        # Calculate date range
        end_date = datetime.now().date() - timedelta(days=1)
        start_date = end_date - timedelta(days=days-1)
        
        # Get top pages
        pages_data = analyzer.get_pages_data(
            site_url,
            start_date.isoformat(),
            end_date.isoformat(),
            limit=limit
        )
        
        # Extract base URL from site_url
        base_url = site_url.replace('sc-domain:', 'https://').replace('https://', '').split('/')[0]
        if not base_url.startswith('http'):
            base_url = f'https://{base_url}'
        
        # Import SEOAnalyzer for scraping
        from app.core.seo_analyzer import SEOAnalyzer
        seo_analyzer = SEOAnalyzer()
        
        pages_with_links = []
        
        for page_data in pages_data[:limit]:  # Limit to avoid too many requests
            page_url = page_data['page']
            
            # Make sure URL is absolute
            if not page_url.startswith('http'):
                if page_url.startswith('/'):
                    full_url = f"{base_url}{page_url}"
                else:
                    full_url = f"{base_url}/{page_url}"
            else:
                full_url = page_url
            
            try:
                # Scrape page for internal links
                import requests
                from bs4 import BeautifulSoup
                from urllib.parse import urlparse, urljoin
                
                response = requests.get(full_url, timeout=10, headers=seo_analyzer.headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Count internal links
                    domain = urlparse(full_url).netloc
                    links = soup.find_all('a', href=True)
                    internal_count = 0
                    
                    for link in links:
                        href = link['href']
                        if domain in href or (not href.startswith('http') and not href.startswith('//')):
                            internal_count += 1
                    
                    pages_with_links.append({
                        'page': page_url,
                        'impressions': page_data['impressions'],
                        'clicks': page_data['clicks'],
                        'ctr': page_data['ctr'],
                        'position': page_data['position'],
                        'internal_links': internal_count
                    })
                else:
                    # If page can't be accessed, still include it with 0 links
                    pages_with_links.append({
                        'page': page_url,
                        'impressions': page_data['impressions'],
                        'clicks': page_data['clicks'],
                        'ctr': page_data['ctr'],
                        'position': page_data['position'],
                        'internal_links': 0
                    })
            except Exception as e:
                print(f"Error analyzing {full_url}: {e}")
                # Include page with 0 links if scraping fails
                pages_with_links.append({
                    'page': page_url,
                    'impressions': page_data['impressions'],
                    'clicks': page_data['clicks'],
                    'ctr': page_data['ctr'],
                    'position': page_data['position'],
                    'internal_links': 0
                })
        
        # Sort by internal links
        pages_with_links.sort(key=lambda x: x['internal_links'], reverse=True)
        highest_internal_links = pages_with_links[:5]
        lowest_internal_links = sorted([p for p in pages_with_links if p['internal_links'] > 0], key=lambda x: x['internal_links'])[:5]
        
        return jsonify({
            'success': True,
            'highest_internal_links': highest_internal_links,
            'lowest_internal_links': lowest_internal_links,
            'total_pages_analyzed': len(pages_with_links)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to analyze internal links: {str(e)}'}), 500


@search_console_bp.route('/reports/pages-by-query', methods=['POST'])
@login_required
def get_pages_by_query():
    """
    Get pages that rank for a specific query, categorized by exact and contain match
    """
    username = session.get("user")
    
    if not storage.has_gsc_connection(username):
        return jsonify({'error': 'Search Console not connected'}), 401
    
    data = request.json or {}
    site_url = data.get('site_url')
    query = data.get('query', '').strip()
    days = int(data.get('days', 30))
    
    if not site_url:
        return jsonify({'error': 'site_url is required'}), 400
    
    if not query:
        return jsonify({'error': 'query is required'}), 400
    
    try:
        # Get user's tokens
        tokens = storage.get_gsc_tokens(username)
        oauth_handler = GSCOAuthHandler()
        
        def save_tokens_callback(updated_tokens):
            storage.save_gsc_tokens(username, updated_tokens)
        
        credentials, _ = oauth_handler.get_valid_credentials(tokens, save_tokens_callback)
        analyzer = GSCAnalyzer(credentials)
        
        # Get pages that rank for this exact query
        pages_by_query = analyzer.get_pages_by_query(
            site_url,
            query,
            days=days,
            limit=25000
        )
        
        # Categorize pages
        exact_pages = []  # Pages that rank for exact query (from GSC)
        contain_pages = []  # Pages where URL contains the query
        
        query_lower = query.lower()
        
        for page_data in pages_by_query:
            page_url = page_data['page'].lower()
            
            # Check if URL contains the query
            if query_lower in page_url:
                contain_pages.append(page_data)
            else:
                # This is exact match (from GSC filter)
                exact_pages.append(page_data)
        
        # Sort by clicks (descending) for both categories
        exact_pages.sort(key=lambda x: x['clicks'], reverse=True)
        contain_pages.sort(key=lambda x: x['clicks'], reverse=True)
        
        # Get top 5 and bottom 5 for each category
        exact_top5 = exact_pages[:5]
        exact_bottom5 = exact_pages[-5:] if len(exact_pages) >= 5 else exact_pages
        
        contain_top5 = contain_pages[:5]
        contain_bottom5 = contain_pages[-5:] if len(contain_pages) >= 5 else contain_pages
        
        return jsonify({
            'success': True,
            'query': query,
            'exact': {
                'total': len(exact_pages),
                'top5': exact_top5,
                'bottom5': exact_bottom5
            },
            'contain': {
                'total': len(contain_pages),
                'top5': contain_top5,
                'bottom5': contain_bottom5
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get pages by query: {str(e)}'}), 500


@search_console_bp.route('/admin/smtp', methods=['GET'])
@login_required
@admin_required
def smtp_settings():
    """Admin page for SMTP configuration"""
    config_path = Path(__file__).parent.parent.parent / 'configs' / 'smtp_config.json'
    
    config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            pass
    
    # Hide password in display
    if 'password' in config:
        config['password'] = '***' if config.get('password') else ''
    
    return render_template('gsc_smtp_settings.html', config=config)


@search_console_bp.route('/admin/smtp/save', methods=['POST'])
@login_required
@admin_required
def save_smtp_settings():
    """Save SMTP configuration (Admin only)"""
    data = request.json or {}
    
    config_path = Path(__file__).parent.parent.parent / 'configs' / 'smtp_config.json'
    config_dir = config_path.parent
    config_dir.mkdir(exist_ok=True)
    
    # Load existing config to preserve password if not changed
    existing_config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
        except:
            pass
    
    # Build new config
    new_config = {
        'enabled': data.get('enabled', False),
        'smtp_server': data.get('smtp_server', ''),
        'smtp_port': int(data.get('smtp_port', 587)),
        'use_tls': data.get('use_tls', True),
        'username': data.get('username', ''),
        'password': data.get('password') if data.get('password') and data.get('password') != '***' else existing_config.get('password', ''),
        'from_email': data.get('from_email', ''),
        'from_name': data.get('from_name', 'SEO Analyze Pro')
    }
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)
        
        # Set secure permissions
        os.chmod(config_path, 0o600)
        
        return jsonify({
            'success': True,
            'message': 'تنظیمات SMTP با موفقیت ذخیره شد'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطا در ذخیره تنظیمات: {str(e)}'
        }), 500


@search_console_bp.route('/admin/smtp/test', methods=['POST'])
@login_required
@admin_required
def test_smtp_settings():
    """Test SMTP configuration (Admin only)"""
    data = request.json or {}
    test_email = data.get('test_email')
    
    if not test_email:
        return jsonify({'error': 'test_email is required'}), 400
    
    try:
        from app.core.email_sender import EmailSender
        
        email_sender = EmailSender()
        
        if not email_sender.is_enabled():
            return jsonify({
                'success': False,
                'error': 'SMTP is not enabled. Please enable it first.'
            }), 400
        
        # Create test report data
        test_report = {
            'period': 'Test Period',
            'avg_position_change': 0,
            'previous_period': 'N/A',
            'current_period': 'N/A',
            'reports': {}
        }
        
        success, message = email_sender.send_report_email(
            to_email=test_email,
            report_data=test_report,
            property_name='Test Property'
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'ایمیل تست با موفقیت به {test_email} ارسال شد'
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطا در ارسال ایمیل تست: {str(e)}'
        }), 500


@search_console_bp.route('/reports/email', methods=['POST'])
@login_required
def email_report():
    """
    Send GSC report via email
    Uses admin-configured SMTP settings
    """
    username = session.get("user")
    
    if not storage.has_gsc_connection(username):
        return jsonify({'error': 'Search Console not connected'}), 401
    
    data = request.json or {}
    report_data = data.get('report_data')
    email = data.get('email')
    
    if not report_data:
        return jsonify({'error': 'report_data is required'}), 400
    
    if not email:
        return jsonify({'error': 'email is required'}), 400
    
    try:
        from app.core.email_sender import EmailSender
        
        # Check if SMTP is configured
        email_sender = EmailSender()
        if not email_sender.is_enabled():
            return jsonify({
                'success': False,
                'error': 'ارسال ایمیل فعال نیست. لطفاً با مدیر سیستم تماس بگیرید.'
            }), 400
        
        # Get property name from report or request
        property_name = data.get('property_name', report_data.get('site_url', 'Unknown Property'))
        
        # Send email using admin-configured SMTP
        success, message = email_sender.send_report_email(
            to_email=email,
            report_data=report_data,
            property_name=property_name
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'گزارش با موفقیت به {email} ارسال شد'
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 500
            
    except ImportError:
        return jsonify({
            'success': False,
            'error': 'Email module not found'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'خطا در ارسال ایمیل: {str(e)}'
        }), 500

