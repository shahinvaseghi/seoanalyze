"""
Google Search Console Analyzer
Fetch and analyze data from Google Search Console API
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


class GSCAnalyzer:
    """
    Google Search Console data analyzer
    Fetches search analytics, coverage, and other data
    """
    
    def __init__(self, credentials: Credentials):
        """
        Initialize with user's OAuth credentials
        
        Args:
            credentials: Google OAuth2 credentials
        """
        self.credentials = credentials
        self.service = build('searchconsole', 'v1', credentials=credentials)
    
    def get_search_analytics(
        self,
        site_url: str,
        start_date: str,
        end_date: str,
        dimensions: List[str] = None,
        row_limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get search analytics data
        
        Args:
            site_url: Search Console property URL (e.g., 'sc-domain:example.com')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            dimensions: List of dimensions ['query', 'page', 'country', 'device', 'date']
            row_limit: Maximum rows to return (default 100, max 25000)
            
        Returns:
            Search analytics data with queries, clicks, impressions, CTR, position
        """
        if dimensions is None:
            dimensions = ['query']
        
        try:
            request_body = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': dimensions,
                'rowLimit': row_limit,
                'startRow': 0
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=site_url,
                body=request_body
            ).execute()
            
            return {
                'success': True,
                'site_url': site_url,
                'start_date': start_date,
                'end_date': end_date,
                'dimensions': dimensions,
                'rows': response.get('rows', []),
                'total_rows': len(response.get('rows', []))
            }
            
        except Exception as e:
            error_msg = str(e)
            # Provide more helpful error messages
            if 'insufficient permissions' in error_msg.lower():
                error_msg = "Insufficient permissions for this property. Please verify access in Google Search Console."
            elif 'not found' in error_msg.lower() or 'invalid' in error_msg.lower():
                error_msg = f"Property '{site_url}' not found or invalid. Please verify the property URL."
            elif 'credentials' in error_msg.lower():
                error_msg = "Authentication error. Please reconnect your Google Search Console account."
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_top_queries(
        self,
        site_url: str,
        days: int = 7,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get top search queries for the last N days
        
        Args:
            site_url: Search Console property URL
            days: Number of days to look back
            limit: Number of results to return
            
        Returns:
            List of top queries with metrics
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        result = self.get_search_analytics(
            site_url,
            start_date.isoformat(),
            end_date.isoformat(),
            dimensions=['query'],
            row_limit=limit
        )
        
        if not result['success']:
            return []
        
        queries = []
        for row in result.get('rows', []):
            queries.append({
                'query': row['keys'][0],
                'impressions': row['impressions'],
                'clicks': row['clicks'],
                'ctr': round(row['ctr'] * 100, 2),  # Convert to percentage
                'position': round(row['position'], 1)
            })
        
        return queries
    
    def get_top_pages(
        self,
        site_url: str,
        days: int = 7,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get top landing pages for the last N days
        
        Args:
            site_url: Search Console property URL
            days: Number of days to look back
            limit: Number of results to return
            
        Returns:
            List of top pages with metrics
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        result = self.get_search_analytics(
            site_url,
            start_date.isoformat(),
            end_date.isoformat(),
            dimensions=['page'],
            row_limit=limit
        )
        
        if not result['success']:
            return []
        
        pages = []
        for row in result.get('rows', []):
            pages.append({
                'page': row['keys'][0],
                'impressions': row['impressions'],
                'clicks': row['clicks'],
                'ctr': round(row['ctr'] * 100, 2),
                'position': round(row['position'], 1)
            })
        
        return pages
    
    def get_performance_summary(
        self,
        site_url: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get overall performance summary
        Uses aggregated data without dimensions for accurate totals matching Google Search Console
        
        Args:
            site_url: Search Console property URL
            days: Number of days to look back (will subtract 1 day to match GSC's data availability)
            
        Returns:
            Summary with total impressions, clicks, CTR, average position
        """
        end_date = datetime.now().date() - timedelta(days=1)  # GSC has 1-2 day delay
        start_date = end_date - timedelta(days=days-1)  # Adjust to match GSC's date range
        
        try:
            # Query without dimensions to get aggregated totals (matches GSC UI)
            request_body = {
                'startDate': start_date.isoformat(),
                'endDate': end_date.isoformat(),
                'rowLimit': 1  # We only need the aggregated total
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=site_url,
                body=request_body
            ).execute()
            
            rows = response.get('rows', [])
            
            # Handle case where no data is available
            if not rows:
                return {
                    'success': True,
                    'period': f'{days} days',
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'total_impressions': 0,
                    'total_clicks': 0,
                    'average_ctr': 0,
                    'average_position': 0,
                    'days_count': 0
                }
            
            # When no dimensions specified, API returns a single row with aggregated totals
            # This matches exactly what Google Search Console UI shows
            total_row = rows[0]
            total_impressions = total_row.get('impressions', 0)
            total_clicks = total_row.get('clicks', 0)
            avg_ctr = total_row.get('ctr', 0) * 100  # Convert to percentage
            avg_position = total_row.get('position', 0)
            
            return {
                'success': True,
                'period': f'{days} days',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'average_ctr': round(avg_ctr, 2),
                'average_position': round(avg_position, 1),
                'days_count': days
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error getting performance summary: {error_msg}")
            
            # Provide more helpful error messages
            if 'insufficient permissions' in error_msg.lower():
                error_msg = "Insufficient permissions for this property. Please verify access in Google Search Console."
            elif 'not found' in error_msg.lower() or 'invalid' in error_msg.lower():
                error_msg = f"Property '{site_url}' not found or invalid. Please verify the property URL."
            elif 'credentials' in error_msg.lower():
                error_msg = "Authentication error. Please reconnect your Google Search Console account."
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_queries_by_page(
        self,
        site_url: str,
        page_url: str,
        days: int = 7,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Get search queries for a specific page
        
        Args:
            site_url: Search Console property URL
            page_url: Specific page URL
            days: Number of days to look back
            limit: Number of results
            
        Returns:
            List of queries driving traffic to the page
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        try:
            request_body = {
                'startDate': start_date.isoformat(),
                'endDate': end_date.isoformat(),
                'dimensions': ['query'],
                'dimensionFilterGroups': [{
                    'filters': [{
                        'dimension': 'page',
                        'operator': 'equals',
                        'expression': page_url
                    }]
                }],
                'rowLimit': limit
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=site_url,
                body=request_body
            ).execute()
            
            queries = []
            for row in response.get('rows', []):
                queries.append({
                    'query': row['keys'][0],
                    'impressions': row['impressions'],
                    'clicks': row['clicks'],
                    'ctr': round(row['ctr'] * 100, 2),
                    'position': round(row['position'], 1)
                })
            
            return queries
            
        except Exception as e:
            print(f"❌ Error getting queries for page: {e}")
            return []
    
    def list_properties(self) -> List[str]:
        """
        Get list of Search Console properties user has access to
        
        Returns:
            List of property URLs
        """
        try:
            site_list = self.service.sites().list().execute()
            
            properties = []
            if 'siteEntry' in site_list:
                for site in site_list['siteEntry']:
                    # Get permission level
                    permission = site.get('permissionLevel', 'unknown')
                    properties.append({
                        'url': site['siteUrl'],
                        'permission': permission
                    })
            
            return properties
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error listing properties: {error_msg}")
            
            # Provide more helpful error messages
            if 'credentials' in error_msg.lower() or 'authentication' in error_msg.lower():
                raise ValueError("Authentication error. Please reconnect your Google Search Console account.")
            elif 'insufficient permissions' in error_msg.lower():
                raise ValueError("Insufficient permissions. Please grant proper access in Google Cloud Console.")
            
            return []
    
    def get_sitemaps(self, site_url: str) -> List[Dict[str, Any]]:
        """
        Get sitemaps for a property
        
        Args:
            site_url: Search Console property URL
            
        Returns:
            List of sitemaps with status
        """
        try:
            response = self.service.sitemaps().list(siteUrl=site_url).execute()
            
            sitemaps = []
            for sitemap in response.get('sitemap', []):
                sitemaps.append({
                    'path': sitemap['path'],
                    'type': sitemap.get('type', 'unknown'),
                    'last_submitted': sitemap.get('lastSubmitted'),
                    'last_downloaded': sitemap.get('lastDownloaded'),
                    'warnings': sitemap.get('warnings', 0),
                    'errors': sitemap.get('errors', 0)
                })
            
            return sitemaps
            
        except Exception as e:
            print(f"❌ Error getting sitemaps: {e}")
            return []

