"""
DuckDuckGo Search Integration
Provides SERP results and keyword ranking tracking via DuckDuckGo
No API key required, no billing needed
"""
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse, parse_qs
import time
import random


class DuckDuckGoSearch:
    """
    DuckDuckGo Search client
    Uses web scraping (no API key needed, no billing required)
    """
    
    def __init__(self):
        self.base_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://duckduckgo.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin'
        }
        self.daily_queries = 0
        self.last_reset_date = datetime.now().date()
    
    def _check_daily_limit(self) -> bool:
        """Check if daily query limit is reached (DuckDuckGo is more lenient)"""
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.daily_queries = 0
            self.last_reset_date = today
        
        # DuckDuckGo allows more queries (estimated 200+ per day)
        return self.daily_queries < 200
    
    def search(self, query: str, num_results: int = 10, country: str = 'us', 
               language: str = 'en', site: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform a DuckDuckGo search using API v1 (no CAPTCHA)
        
        Args:
            query: Search query
            num_results: Number of results to return
            country: Country code (e.g., 'us', 'ir', 'uk')
            language: Language code (e.g., 'en', 'fa')
            site: Restrict search to specific site (optional)
            
        Returns:
            Dictionary with search results
        """
        if not self._check_daily_limit():
            return {
                'error': 'Daily query limit reached (estimated 200 queries/day)',
                'success': False,
                'daily_queries': self.daily_queries
            }
        
        try:
            # Build search query
            search_query = query
            if site:
                search_query = f"site:{site} {query}"
            
            # Try DuckDuckGo API first (no CAPTCHA)
            api_result = self._search_via_api(search_query, num_results, country, language)
            if api_result.get('success'):
                self.daily_queries += 1
                return api_result
            
            # Fallback to HTML scraping (may trigger CAPTCHA)
            return self._search_via_html(search_query, num_results, country, language)
            
        except Exception as e:
            return {
                'error': f'Search failed: {str(e)}',
                'success': False
            }
    
    def _search_via_api(self, query: str, num_results: int, country: str, language: str) -> Dict[str, Any]:
        """
        Search using DuckDuckGo Instant Answer API (limited results but no CAPTCHA)
        """
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(self.api_url, params=params, timeout=10)
            
            if response.status_code != 200:
                return {'success': False}
            
            data = response.json()
            items = []
            
            # Extract RelatedTopics (main results)
            if 'RelatedTopics' in data:
                for topic in data['RelatedTopics'][:num_results]:
                    if isinstance(topic, dict):
                        if 'FirstURL' in topic and 'Text' in topic:
                            items.append({
                                'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else topic.get('Text', '')[:50],
                                'link': topic['FirstURL'],
                                'snippet': topic.get('Text', ''),
                                'display_link': urlparse(topic['FirstURL']).netloc,
                                'position': len(items) + 1
                            })
                        elif 'Topics' in topic:
                            for subtopic in topic['Topics'][:3]:
                                if 'FirstURL' in subtopic:
                                    items.append({
                                        'title': subtopic.get('Text', '').split(' - ')[0] if ' - ' in subtopic.get('Text', '') else subtopic.get('Text', '')[:50],
                                        'link': subtopic['FirstURL'],
                                        'snippet': subtopic.get('Text', ''),
                                        'display_link': urlparse(subtopic['FirstURL']).netloc,
                                        'position': len(items) + 1
                                    })
            
            # Extract AbstractURL (if available)
            if 'AbstractURL' in data and data['AbstractURL']:
                items.insert(0, {
                    'title': data.get('Heading', query),
                    'link': data['AbstractURL'],
                    'snippet': data.get('Abstract', ''),
                    'display_link': urlparse(data['AbstractURL']).netloc,
                    'position': 1
                })
            
            if items:
                return {
                    'success': True,
                    'query': query,
                    'total_results': len(items) * 10,
                    'search_time': 0.3,
                    'items': items[:num_results],
                    'daily_queries_used': self.daily_queries + 1,
                    'daily_queries_remaining': 200 - (self.daily_queries + 1),
                    'timestamp': datetime.now().isoformat(),
                    'method': 'duckduckgo_api',
                    'source': 'DuckDuckGo API',
                    'note': 'Limited results from Instant Answer API. For full SERP, use Google Custom Search API.'
                }
            
            return {'success': False}
            
        except Exception:
            return {'success': False}
    
    def _search_via_html(self, query: str, num_results: int, country: str, language: str) -> Dict[str, Any]:
        """
        Fallback: Search via HTML scraping (may trigger CAPTCHA)
        """
        try:
            encoded_query = quote_plus(query)
            search_url = f"{self.html_url}?q={encoded_query}"
            
            if language:
                lang_map = {'fa': 'fa-IR', 'en': 'en-US', 'de': 'de-DE'}
                search_url += f"&kl={lang_map.get(language, language)}"
            
            time.sleep(random.uniform(1, 2))
            
            # First visit to get cookies
            self.session.get('https://duckduckgo.com/', timeout=10)
            time.sleep(0.5)
            
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 202 or 'anomaly-modal' in response.text.lower() or 'captcha' in response.text.lower():
                return {
                    'error': 'DuckDuckGo CAPTCHA detected. Please try again later or use Google Custom Search API.',
                    'success': False,
                    'captcha_detected': True,
                    'suggestion': 'Use Google Custom Search API or try again in a few minutes'
                }
            
            if response.status_code != 200:
                return {
                    'error': f'Search failed: HTTP {response.status_code}',
                    'success': False
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract search results
            items = []
            
            # DuckDuckGo result structure: div.result or div.web-result
            for result in soup.find_all(['div'], class_=lambda x: x and ('result' in str(x).lower() or 'web-result' in str(x).lower())):
                try:
                    # Find title and link
                    title_elem = result.find('a', class_='result__a')
                    if not title_elem:
                        continue
                    
                    # Extract URL
                    href = title_elem.get('href', '')
                    if not href or href.startswith('//'):
                        continue
                    
                    # Handle DuckDuckGo redirects
                    if href.startswith('/l/?kh='):
                        # Extract actual URL from redirect
                        parsed = urlparse(href)
                        params = parse_qs(parsed.query)
                        url = params.get('uddg', [None])[0]
                        if not url:
                            url = params.get('u', [None])[0]
                    elif href.startswith('http'):
                        url = href
                    else:
                        continue
                    
                    # Skip DuckDuckGo's own pages
                    if 'duckduckgo.com' in url:
                        continue
                    
                    # Extract title
                    title = title_elem.get_text().strip()
                    
                    # Extract snippet
                    snippet_elem = result.find('a', class_='result__snippet')
                    if not snippet_elem:
                        snippet_elem = result.find('div', class_='result__snippet')
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ''
                    
                    # Extract display link
                    display_link_elem = result.find('a', class_='result__url')
                    if display_link_elem:
                        display_link = display_link_elem.get_text().strip()
                    else:
                        display_link = urlparse(url).netloc
                    
                    items.append({
                        'title': title,
                        'link': url,
                        'snippet': snippet,
                        'display_link': display_link,
                        'position': len(items) + 1
                    })
                    
                    if len(items) >= num_results:
                        break
                except Exception:
                    continue
            
            # Alternative parsing method if first method fails
            if len(items) < 3:
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if href.startswith('/l/?kh='):
                        parsed = urlparse(href)
                        params = parse_qs(parsed.query)
                        url = params.get('uddg', [None])[0] or params.get('u', [None])[0]
                        
                        if url and 'duckduckgo.com' not in url:
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
            
            if items:
                self.daily_queries += 1
                return {
                    'success': True,
                    'query': query,
                    'total_results': len(items) * 10,  # Estimate
                    'search_time': 0.5,  # Estimate
                    'items': items[:num_results],
                    'daily_queries_used': self.daily_queries,
                    'daily_queries_remaining': 200 - self.daily_queries,
                    'timestamp': datetime.now().isoformat(),
                    'method': 'duckduckgo_html_scraping',
                    'source': 'DuckDuckGo HTML'
                }
            
            return {
                'error': 'No results found. DuckDuckGo may have changed their HTML structure or CAPTCHA is required.',
                'success': False,
                'suggestion': 'Try using Google Custom Search API or wait a few minutes and try again'
            }
            
        except Exception as e:
            return {
                'error': f'Search failed: {str(e)}',
                'success': False
            }
    
    def find_keyword_rank(self, keyword: str, target_url: str, country: str = 'us', 
                         language: str = 'en', max_pages: int = 5) -> Dict[str, Any]:
        """
        Find the ranking position of a URL for a specific keyword
        
        Args:
            keyword: Search keyword
            target_url: URL to find in results
            country: Country code
            language: Language code
            max_pages: Maximum number of result pages to check (30 results per page)
            
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
            start_index = page * 30  # DuckDuckGo shows ~30 results per page
            
            # Build search URL with pagination
            encoded_query = quote_plus(keyword)
            search_url = f"{self.base_url}?q={encoded_query}"
            
            if language:
                lang_map = {'fa': 'fa-IR', 'en': 'en-US', 'de': 'de-DE'}
                search_url += f"&kl={lang_map.get(language, language)}"
            
            if page > 0:
                search_url += f"&s={start_index}"
            
            try:
                time.sleep(random.uniform(1, 2))  # Delay between pages
                
                response = requests.get(search_url, headers=self.headers, timeout=15)
                
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract results
                page_items = []
                for result in soup.find_all('div', class_='result'):
                    try:
                        title_elem = result.find('a', class_='result__a')
                        if not title_elem:
                            continue
                        
                        href = title_elem.get('href', '')
                        if href.startswith('/l/?kh='):
                            parsed = urlparse(href)
                            params = parse_qs(parsed.query)
                            url = params.get('uddg', [None])[0] or params.get('u', [None])[0]
                        elif href.startswith('http'):
                            url = href
                        else:
                            continue
                        
                        if not url or 'duckduckgo.com' in url:
                            continue
                        
                        result_domain = url.replace('https://', '').replace('http://', '').split('/')[0]
                        
                        page_items.append({
                            'position': start_index + len(page_items) + 1,
                            'title': title_elem.get_text().strip(),
                            'url': url,
                            'snippet': ''
                        })
                        
                        # Check if this is our target URL
                        if target_url in url or target_domain in result_domain:
                            if position is None:
                                position = start_index + len(page_items)
                    except Exception:
                        continue
                
                if not page_items:
                    break  # No more results
                
                all_results.extend(page_items)
                pages_checked += 1
                self.daily_queries += 1
                
                # If we found the position, we can stop
                if position is not None:
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
            'timestamp': datetime.now().isoformat(),
            'source': 'DuckDuckGo'
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
            'timestamp': datetime.now().isoformat(),
            'source': 'DuckDuckGo'
        }

