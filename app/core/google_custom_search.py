"""
Google Custom Search API Integration
Provides SERP results and keyword ranking tracking
"""
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path


class GoogleCustomSearch:
    """
    Google Custom Search API client
    Documentation: https://developers.google.com/custom-search/v1/overview
    """
    
    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None):
        """
        Initialize Google Custom Search API client
        
        Args:
            api_key: Google Custom Search API key
            search_engine_id: Custom Search Engine ID (CX)
        """
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.daily_queries = 0
        self.last_reset_date = datetime.now().date()
        
        # Load config if not provided
        if not self.api_key or not self.search_engine_id:
            self._load_config()
    
    def _load_config(self):
        """Load API credentials from config file"""
        config_path = Path(__file__).parent.parent.parent / 'configs' / 'api_keys.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    google_search = config.get('google_custom_search', {})
                    self.api_key = self.api_key or google_search.get('api_key')
                    self.search_engine_id = self.search_engine_id or google_search.get('search_engine_id')
            except Exception as e:
                print(f"Error loading Google Custom Search config: {e}")
    
    def _check_daily_limit(self) -> bool:
        """Check if daily query limit is reached"""
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.daily_queries = 0
            self.last_reset_date = today
        
        # Free tier: 100 queries per day
        return self.daily_queries < 100
    
    def search(self, query: str, num_results: int = 10, country: str = 'us', 
               language: str = 'en', site: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform a Google search using Custom Search API
        
        Args:
            query: Search query
            num_results: Number of results to return (max 10 per request)
            country: Country code (e.g., 'us', 'ir', 'uk')
            language: Language code (e.g., 'en', 'fa')
            site: Restrict search to specific site (optional)
            
        Returns:
            Dictionary with search results
        """
        if not self.api_key or not self.search_engine_id:
            return {
                'error': 'Google Custom Search API key or Search Engine ID not configured',
                'success': False
            }
        
        if not self._check_daily_limit():
            return {
                'error': 'Daily query limit reached (100 queries/day)',
                'success': False,
                'daily_queries': self.daily_queries
            }
        
        # Build query string
        search_query = query
        if site:
            search_query = f"site:{site} {query}"
        
        params = {
            'key': self.api_key,
            'cx': self.search_engine_id,
            'q': search_query,
            'num': min(num_results, 10),  # Max 10 per request
            'gl': country,  # Geolocation
            'lr': f"lang_{language}",  # Language restriction
            'safe': 'active'  # Safe search
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            self.daily_queries += 1
            data = response.json()
            
            # Parse results
            results = {
                'success': True,
                'query': query,
                'total_results': int(data.get('searchInformation', {}).get('totalResults', 0)),
                'search_time': float(data.get('searchInformation', {}).get('searchTime', 0)),
                'items': [],
                'daily_queries_used': self.daily_queries,
                'daily_queries_remaining': 100 - self.daily_queries,
                'timestamp': datetime.now().isoformat()
            }
            
            # Extract search results
            for item in data.get('items', []):
                results['items'].append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'display_link': item.get('displayLink', ''),
                    'position': len(results['items']) + 1
                })
            
            return results
            
        except requests.exceptions.RequestException as e:
            return {
                'error': f'API request failed: {str(e)}',
                'success': False
            }
        except Exception as e:
            return {
                'error': f'Unexpected error: {str(e)}',
                'success': False
            }
    
    def find_keyword_rank(self, keyword: str, target_url: str, country: str = 'us', 
                         language: str = 'en', max_pages: int = 10) -> Dict[str, Any]:
        """
        Find the ranking position of a URL for a specific keyword
        
        Args:
            keyword: Search keyword
            target_url: URL to find in results
            country: Country code
            language: Language code
            max_pages: Maximum number of result pages to check (10 results per page)
            
        Returns:
            Dictionary with ranking information
        """
        if not self._check_daily_limit():
            return {
                'error': 'Daily query limit reached',
                'success': False
            }
        
        # Normalize target URL
        target_domain = target_url.replace('https://', '').replace('http://', '').split('/')[0]
        
        position = None
        all_results = []
        pages_checked = 0
        
        for page in range(max_pages):
            start_index = (page * 10) + 1
            
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': keyword,
                'num': 10,
                'start': start_index,
                'gl': country,
                'lr': f"lang_{language}",
                'safe': 'active'
            }
            
            try:
                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                
                self.daily_queries += 1
                data = response.json()
                
                items = data.get('items', [])
                if not items:
                    break  # No more results
                
                pages_checked += 1
                
                # Check each result
                for idx, item in enumerate(items):
                    result_url = item.get('link', '')
                    result_domain = result_url.replace('https://', '').replace('http://', '').split('/')[0]
                    
                    all_results.append({
                        'position': start_index + idx,
                        'title': item.get('title', ''),
                        'url': result_url,
                        'snippet': item.get('snippet', '')
                    })
                    
                    # Check if this is our target URL
                    if target_url in result_url or target_domain in result_domain:
                        if position is None:
                            position = start_index + idx
                
                # If we found the position, we can stop
                if position is not None:
                    break
                    
            except requests.exceptions.RequestException:
                break
            except Exception:
                break
        
        return {
            'success': True,
            'keyword': keyword,
            'target_url': target_url,
            'position': position,
            'found': position is not None,
            'pages_checked': pages_checked,
            'total_results_checked': len(all_results),
            'top_10_results': all_results[:10],
            'daily_queries_used': self.daily_queries,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_serp_features(self, query: str, country: str = 'us', language: str = 'en') -> Dict[str, Any]:
        """
        Analyze SERP features for a query
        
        Args:
            query: Search query
            country: Country code
            language: Language code
            
        Returns:
            Dictionary with SERP features analysis
        """
        result = self.search(query, num_results=10, country=country, language=language)
        
        if not result.get('success'):
            return result
        
        features = {
            'has_ads': False,
            'has_images': False,
            'has_videos': False,
            'has_people_also_ask': False,
            'has_related_searches': False,
            'has_featured_snippet': False,
            'organic_results_count': len(result.get('items', []))
        }
        
        # Note: Google Custom Search API doesn't return all SERP features
        # This is a basic implementation
        # For full SERP features, you'd need a service like SerpAPI
        
        return {
            'success': True,
            'query': query,
            'features': features,
            'results': result,
            'timestamp': datetime.now().isoformat()
        }
    
    def compare_competitors(self, keyword: str, competitor_urls: List[str], 
                           country: str = 'us', language: str = 'en') -> Dict[str, Any]:
        """
        Compare competitor rankings for a keyword
        
        Args:
            keyword: Search keyword
            competitor_urls: List of competitor URLs to check
            country: Country code
            language: Language code
            
        Returns:
            Dictionary with competitor rankings
        """
        rankings = {}
        
        for url in competitor_urls:
            rank_result = self.find_keyword_rank(keyword, url, country, language, max_pages=3)
            if rank_result.get('success') and rank_result.get('found'):
                rankings[url] = {
                    'position': rank_result['position'],
                    'found': True
                }
            else:
                rankings[url] = {
                    'position': None,
                    'found': False
                }
        
        return {
            'success': True,
            'keyword': keyword,
            'rankings': rankings,
            'daily_queries_used': self.daily_queries,
            'timestamp': datetime.now().isoformat()
        }

