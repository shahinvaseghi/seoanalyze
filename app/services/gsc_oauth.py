"""
Google Search Console OAuth 2.0 Handler
Manages OAuth flow for each user to connect their Search Console account
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class GSCOAuthHandler:
    """
    Handles OAuth 2.0 flow for Google Search Console API
    Each user gets their own credentials
    """
    
    # Search Console API scope (read-only)
    SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
    
    def __init__(self, client_secrets_file: Optional[str] = None):
        """
        Initialize OAuth handler
        
        Args:
            client_secrets_file: Path to client_secret JSON file from Google Cloud Console
        """
        if client_secrets_file is None:
            # Default path
            config_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'configs'
            )
            client_secrets_file = os.path.join(config_dir, 'google_oauth_client.json')
        
        self.client_secrets_file = client_secrets_file
        
        # Check if file exists
        if not os.path.exists(self.client_secrets_file):
            raise FileNotFoundError(
                f"OAuth client secrets file not found: {self.client_secrets_file}\n"
                f"Please download from Google Cloud Console and save to configs/google_oauth_client.json"
            )
    
    def create_authorization_url(self, redirect_uri: str, state: Optional[str] = None) -> tuple[str, str]:
        """
        Create authorization URL for user to grant permissions
        
        Args:
            redirect_uri: URL to redirect back after authorization
            state: Optional state parameter for security
            
        Returns:
            Tuple of (authorization_url, state)
        """
        flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        # Generate authorization URL
        # Use provided state if available, otherwise let Flow generate one
        auth_kwargs = {
            'access_type': 'offline',  # Get refresh token
            'include_granted_scopes': 'true',
            'prompt': 'consent'  # Force consent screen to get refresh token
        }
        
        if state:
            # Use the provided state (from Flask session)
            auth_kwargs['state'] = state
        
        authorization_url, generated_state = flow.authorization_url(**auth_kwargs)
        
        # Return the state we used (either provided or generated)
        return authorization_url, state if state else generated_state
    
    def exchange_code_for_tokens(self, authorization_code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token and refresh token
        
        Args:
            authorization_code: Code received from Google OAuth callback
            redirect_uri: Same redirect URI used in authorization
            
        Returns:
            Dictionary with tokens and metadata
        """
        flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )
        
        # Exchange code for tokens
        flow.fetch_token(code=authorization_code)
        
        # Get credentials
        credentials = flow.credentials
        
        # Extract token information
        tokens = {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None,
            'created_at': datetime.now().isoformat()
        }
        
        return tokens
    
    def refresh_access_token(self, tokens: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refresh expired access token using refresh token
        
        Args:
            tokens: Current token dictionary
            
        Returns:
            Updated token dictionary
        """
        credentials = Credentials(
            token=tokens.get('access_token'),
            refresh_token=tokens.get('refresh_token'),
            token_uri=tokens.get('token_uri'),
            client_id=tokens.get('client_id'),
            client_secret=tokens.get('client_secret'),
            scopes=tokens.get('scopes')
        )
        
        # Refresh the token
        credentials.refresh(Request())
        
        # Update tokens
        tokens['access_token'] = credentials.token
        tokens['expiry'] = credentials.expiry.isoformat() if credentials.expiry else None
        tokens['refreshed_at'] = datetime.now().isoformat()
        
        return tokens
    
    def get_valid_credentials(self, tokens: Dict[str, Any], update_tokens_callback=None) -> tuple[Credentials, bool]:
        """
        Get valid credentials, refreshing if necessary
        
        Args:
            tokens: Token dictionary
            update_tokens_callback: Optional callback function to save updated tokens back to storage
                Should accept updated tokens dict and save it
            
        Returns:
            Tuple of (Credentials object, was_refreshed boolean)
        """
        credentials = Credentials(
            token=tokens.get('access_token'),
            refresh_token=tokens.get('refresh_token'),
            token_uri=tokens.get('token_uri'),
            client_id=tokens.get('client_id'),
            client_secret=tokens.get('client_secret'),
            scopes=tokens.get('scopes')
        )
        
        was_refreshed = False
        
        # Check if expired
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            was_refreshed = True
            
            # Update tokens dict with new values
            tokens['access_token'] = credentials.token
            tokens['expiry'] = credentials.expiry.isoformat() if credentials.expiry else None
            tokens['refreshed_at'] = datetime.now().isoformat()
            
            # Save updated tokens if callback provided
            if update_tokens_callback:
                try:
                    update_tokens_callback(tokens)
                except Exception as e:
                    print(f"⚠️ Failed to save refreshed tokens: {e}")
        
        return credentials, was_refreshed
    
    def get_user_properties(self, tokens: Dict[str, Any]) -> list[str]:
        """
        Get list of Search Console properties the user has access to
        
        Args:
            tokens: User's OAuth tokens
            
        Returns:
            List of property URLs (e.g., ['sc-domain:example.com', 'https://example.com/'])
        """
        try:
            credentials, _ = self.get_valid_credentials(tokens)
            service = build('searchconsole', 'v1', credentials=credentials)
            
            # List sites
            site_list = service.sites().list().execute()
            
            properties = []
            if 'siteEntry' in site_list:
                for site in site_list['siteEntry']:
                    properties.append(site['siteUrl'])
            
            return properties
            
        except Exception as e:
            print(f"❌ Error getting properties: {e}")
            return []
    
    def is_token_valid(self, tokens: Dict[str, Any]) -> bool:
        """
        Check if token is still valid
        
        Args:
            tokens: Token dictionary
            
        Returns:
            True if valid, False if expired or invalid
        """
        if not tokens or not tokens.get('access_token'):
            return False
        
        # Check expiry
        expiry_str = tokens.get('expiry')
        if expiry_str:
            try:
                expiry = datetime.fromisoformat(expiry_str)
                if datetime.now() >= expiry:
                    # Expired but might have refresh token
                    return bool(tokens.get('refresh_token'))
            except:
                pass
        
        return True

