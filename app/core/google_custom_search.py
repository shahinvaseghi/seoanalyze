"""
Google Custom Search API Integration
Provides SERP results and keyword ranking tracking
Falls back to web scraping if API is not available
"""
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse
import time
import random


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
        self.use_scraping_fallback = False  # Flag to use scraping if API fails
        
        # Load config if not provided
        if not self.api_key or not self.search_engine_id:
            self._load_config()
        
        # Headers for scraping
        self.scraping_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin'
        }
    
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
            
            # Check for specific error responses
            if response.status_code == 403:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Forbidden')
                
                # Try scraping fallback if API fails
                if not self.use_scraping_fallback:
                    self.use_scraping_fallback = True
                    scraping_result = self._search_via_scraping(query, num_results, country, language, site)
                    if scraping_result.get('success'):
                        scraping_result['warning'] = 'Using web scraping fallback (API unavailable). Results may be limited.'
                        return scraping_result
                
                return {
                    'error': f'API access denied (403): {error_message}. Please check: 1) Custom Search API is enabled, 2) API key has access to Custom Search API, 3) Billing is enabled. Trying scraping fallback...',
                    'success': False,
                    'error_code': 403,
                    'error_details': error_data.get('error', {}),
                    'fallback_attempted': True
                }
            
            if response.status_code == 400:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Bad Request')
                return {
                    'error': f'Invalid request (400): {error_message}',
                    'success': False,
                    'error_code': 400,
                    'error_details': error_data.get('error', {})
                }
            
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
            # Try scraping fallback on network errors
            if not self.use_scraping_fallback:
                self.use_scraping_fallback = True
                scraping_result = self._search_via_scraping(query, num_results, country, language, site)
                if scraping_result.get('success'):
                    scraping_result['warning'] = 'Using web scraping fallback (API unavailable). Results may be limited.'
                    return scraping_result
            
            return {
                'error': f'API request failed: {str(e)}',
                'success': False
            }
        except Exception as e:
            return {
                'error': f'Unexpected error: {str(e)}',
                'success': False
            }
    
    def _search_via_scraping(self, query: str, num_results: int = 10, country: str = 'us',
                            language: str = 'en', site: Optional[str] = None) -> Dict[str, Any]:
        """
        Fallback method: Scrape Google search results directly
        WARNING: This may trigger CAPTCHA or rate limiting
        """
        try:
            # Build search URL
            search_query = query
            if site:
                search_query = f"site:{site} {query}"
            
            encoded_query = quote_plus(search_query)
            
            # Google search URL with parameters
            search_url = f"https://www.google.com/search?q={encoded_query}&num={min(num_results, 10)}"
            
            # Add country and language parameters
            if country:
                search_url += f"&gl={country}"
            if language:
                lang_map = {'fa': 'fa-IR', 'en': 'en-US', 'de': 'de-DE'}
                search_url += f"&hl={lang_map.get(language, language)}"
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            # Make request with realistic headers
            response = requests.get(search_url, headers=self.scraping_headers, timeout=15)
            
            if response.status_code != 200:
                return {
                    'error': f'Scraping failed: HTTP {response.status_code}',
                    'success': False
                }
            
            # Check for CAPTCHA
            if 'captcha' in response.text.lower() or 'sorry' in response.text.lower():
                return {
                    'error': 'Google CAPTCHA detected. Please try again later or use VPN.',
                    'success': False,
                    'captcha_detected': True
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract search results
            items = []
            
            # Method 1: Modern Google results (div.g)
            for result in soup.find_all('div', class_='g'):
                try:
                    # Find title link
                    title_elem = result.find('h3')
                    link_elem = result.find('a', href=True)
                    
                    if not link_elem:
                        continue
                    
                    # Extract URL (handle Google redirects)
                    href = link_elem.get('href', '')
                    if href.startswith('/url?q='):
                        # Extract actual URL from Google redirect
                        from urllib.parse import parse_qs, urlparse
                        parsed = urlparse(href)
                        params = parse_qs(parsed.query)
                        url = params.get('q', [href])[0]
                    elif href.startswith('http'):
                        url = href
                    else:
                        continue
                    
                    # Skip Google's own pages
                    if 'google.com' in url or 'youtube.com' in url:
                        continue
                    
                    # Extract title
                    title = title_elem.get_text() if title_elem else link_elem.get_text()
                    
                    # Extract snippet
                    snippet_elem = result.find('span', class_=['aCOpRe', 'st'])
                    if not snippet_elem:
                        snippet_elem = result.find('div', class_='VwiC3b')
                    snippet = snippet_elem.get_text() if snippet_elem else ''
                    
                    # Extract display link
                    display_link = urlparse(url).netloc
                    
                    items.append({
                        'title': title.strip(),
                        'link': url,
                        'snippet': snippet.strip(),
                        'display_link': display_link,
                        'position': len(items) + 1
                    })
                    
                    if len(items) >= num_results:
                        break
                except Exception:
                    continue
            
            # Method 2: Alternative parsing (backup)
            if len(items) < 3:
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if href.startswith('/url?q='):
                        from urllib.parse import parse_qs, urlparse
                        parsed = urlparse(href)
                        params = parse_qs(parsed.query)
                        url = params.get('q', [None])[0]
                        
                        if url and 'google.com' not in url and 'youtube.com' not in url:
                            title = link.get_text().strip()
                            if title and len(title) > 5:
                                items.append({
                                    'title': title,
                                    'link': url,
                                    'snippet': '',
                                    'display_link': urlparse(url).netloc,
                                    'position': len(items) + 1
                                })
                                
                                if len(items) >= num_results:
                                    break
            
            return {
                'success': True,
                'query': query,
                'total_results': len(items) * 10,  # Estimate
                'search_time': 0.5,  # Estimate
                'items': items[:num_results],
                'daily_queries_used': self.daily_queries,
                'daily_queries_remaining': 100 - self.daily_queries,
                'timestamp': datetime.now().isoformat(),
                'method': 'scraping',
                'warning': 'Results obtained via web scraping. May be limited or blocked by Google.'
            }
            
        except Exception as e:
            return {
                'error': f'Scraping failed: {str(e)}',
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

