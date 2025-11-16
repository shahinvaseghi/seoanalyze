"""
Enhanced Keyword Gap Analyzer v2.0
===================================

A professional keyword gap analysis system that treats keywords as 'demand units'
with intent, volume, relevance, and business value - not just strings.

Features:
- N-gram extraction (1-5 word queries)
- Intent analysis integration
- Business relevance scoring
- SERP features prediction
- Multi-dimensional opportunity scoring
- Priority matrix (quick wins vs long-term)
- Smart recommendations
"""

import re
import json
import requests
import time
import math
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
from dataclasses import asdict

# Import models
from .models import (
    SearchIntent, PageType, SERPFeatureType, KeywordSource, KeywordDifficulty,
    SearchQuery, KeywordGapOpportunity, KeywordGapAnalysisResult, BusinessContext
)

# Import intent analyzer
from .intent_analyzer import IntentAnalyzer


# ==================== Stop Words ====================

# Comprehensive Persian stop words
PERSIAN_STOP_WORDS = {
    # Articles and pronouns
    'و', 'در', 'از', 'به', 'که', 'این', 'آن', 'با', 'برای', 'تا', 'را', 'است', 'بود', 'باشد',
    'می', 'خواهد', 'کرد', 'کرده', 'هم', 'نیز', 'همچنین', 'اما', 'ولی', 'اگر', 'چون', 'زیرا',
    'چرا', 'کجا', 'کی', 'چگونه', 'چه', 'کدام', 'کسی', 'چیزی', 'همه', 'تمام', 'کلی', 'بعضی',
    'برخی', 'هر', 'هیچ', 'نه', 'نمی', 'های', 'ها', 'ان', 'ات', 'ین', 'ون',
    
    # Common verbs (conjugated)
    'می‌کند', 'می‌شود', 'می‌تواند', 'می‌توان', 'می‌خواهد', 'نمی‌شود', 'نمی‌تواند',
    'نمی‌خواهد', 'نمی‌کند', 'نمی‌باشد', 'هست', 'هستند', 'بودند', 'باشند', 'خواهند',
    'کردند', 'کرده‌اند', 'می‌کنند', 'می‌شوند', 'می‌توانند', 'می‌خواهند',
    
    # Time and place
    'امروز', 'دیروز', 'فردا', 'حالا', 'الان', 'هفته', 'ماه', 'سال', 'روز', 'شب',
    'صبح', 'ظهر', 'عصر', 'داخل', 'خارج', 'بالا', 'پایین', 'چپ', 'راست', 'وسط',
    'کنار', 'جلوی', 'پشت', 'زیر', 'روی', 'بین', 'میان', 'دور', 'نزدیک', 'قبل', 'بعد',
    
    # Generic words
    'چیز', 'کار', 'مورد', 'نوع', 'گونه', 'مدل', 'سبک', 'روش', 'طریقه', 'شیوه', 'نحوه',
    'چگونگی', 'کیفیت', 'مقدار', 'تعداد', 'اندازه', 'حجم', 'وزن',
    
    # Common adjectives (too generic for SEO)
    'خوب', 'بد', 'زیبا', 'بزرگ', 'کوچک', 'بلند', 'کوتاه', 'جدید', 'قدیمی', 'تازه',
    'سریع', 'آهسته', 'آسان', 'سخت', 'مشکل', 'راحت'
}

# English stop words
ENGLISH_STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is',
    'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with', 'would', 'you',
    'your', 'we', 'they', 'them', 'their', 'this', 'these', 'those', 'have', 'had', 'do',
    'does', 'did', 'can', 'could', 'should', 'may', 'might', 'must', 'shall', 'or', 'but'
}


class EnhancedKeywordGapAnalyzer:
    """
    Professional keyword gap analyzer with business intelligence.
    """
    
    def __init__(self, business_context: Optional[BusinessContext] = None):
        """
        Initialize analyzer with optional business context.
        
        Args:
            business_context: Business information for relevance scoring
        """
        self.business_context = business_context
        self.intent_analyzer = IntentAnalyzer()
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,fa;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def analyze_keyword_gap(
        self,
        own_website: str,
        competitors: List[str],
        business_context: Optional[BusinessContext] = None
    ) -> KeywordGapAnalysisResult:
        """
        Perform comprehensive keyword gap analysis.
        
        Args:
            own_website: Your website URL
            competitors: List of competitor URLs
            business_context: Business context for relevance scoring
            
        Returns:
            Complete analysis result with opportunities
        """
        start_time = time.time()
        
        # Use provided context or instance context
        context = business_context or self.business_context
        
        print(f"\n🚀 Starting Enhanced Keyword Gap Analysis v2.0")
        print(f"   Own website: {own_website}")
        print(f"   Competitors: {len(competitors)}")
        if context:
            print(f"   Business: {context.industry} - {context.niche}")
        
        # Step 1: Extract queries from own website
        print("\n📊 Analyzing your website...")
        own_queries = self._extract_queries_comprehensive(own_website, "own")
        print(f"   ✓ Extracted {len(own_queries)} unique queries")
        
        # Step 2: Extract queries from competitors
        print("\n📊 Analyzing competitors...")
        competitor_queries = {}
        for i, competitor in enumerate(competitors, 1):
            print(f"   [{i}/{len(competitors)}] {competitor}")
            queries = self._extract_queries_comprehensive(competitor, "competitor")
            competitor_queries[competitor] = queries
            print(f"   ✓ Extracted {len(queries)} queries")
            time.sleep(1)  # Rate limiting
        
        # Step 3: Identify gaps and score opportunities
        print("\n🔍 Identifying keyword gaps...")
        gap_opportunities = self._identify_gaps_and_score(
            own_queries,
            competitor_queries,
            context
        )
        print(f"   ✓ Found {len(gap_opportunities)} opportunities")
        
        # Step 4: Categorize opportunities
        print("\n📊 Categorizing opportunities...")
        categorized = self._categorize_opportunities(gap_opportunities)
        
        # Step 5: Generate strategic recommendations
        print("\n💡 Generating recommendations...")
        recommendations = self._generate_strategic_recommendations(
            gap_opportunities,
            categorized,
            context
        )
        
        # Create result
        processing_time = time.time() - start_time
        
        result = KeywordGapAnalysisResult(
            own_website_url=own_website,
            competitor_urls=competitors,
            business_context=context,
            own_queries=own_queries,
            competitor_queries=competitor_queries,
            gap_opportunities=gap_opportunities,
            quick_wins=categorized['quick_wins'],
            high_priority=categorized['high_priority'],
            medium_priority=categorized['medium'],
            long_term=categorized['long_term'],
            informational_gaps=categorized['informational'],
            transactional_gaps=categorized['transactional'],
            local_gaps=categorized['local'],
            comparison_gaps=categorized['comparison'],
            navigational_gaps=categorized['navigational'],
            strategic_recommendations=recommendations['strategic'],
            content_calendar_suggestions=recommendations['calendar'],
            total_gaps_found=len(gap_opportunities),
            total_opportunity_value=sum(opp.estimated_monthly_traffic for opp in gap_opportunities),
            avg_difficulty=sum(self._difficulty_to_score(opp.query.difficulty) for opp in gap_opportunities) / max(len(gap_opportunities), 1),
            avg_relevance=sum(opp.relevance_score for opp in gap_opportunities) / max(len(gap_opportunities), 1),
            processing_time_seconds=processing_time
        )
        
        print(f"\n✅ Analysis complete in {processing_time:.1f}s")
        print(f"   📊 Total gaps: {result.total_gaps_found}")
        print(f"   🎯 Quick wins: {len(result.quick_wins)}")
        print(f"   ⭐ High priority: {len(result.high_priority)}")
        print(f"   📈 Est. monthly traffic: {int(result.total_opportunity_value)}")
        
        return result
    
    def _extract_queries_comprehensive(self, url: str, source_type: str) -> List[SearchQuery]:
        """
        Extract search queries (not just words) from a URL.
        Uses N-gram extraction to find 1-5 word phrases.
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            queries = []
            
            # Extract from different sources
            queries.extend(self._extract_from_title(soup, url))
            queries.extend(self._extract_from_meta(soup, url))
            queries.extend(self._extract_from_headings(soup, url))
            queries.extend(self._extract_from_content(soup, url))
            queries.extend(self._extract_from_url(url))
            
            # Deduplicate by query_text
            unique_queries = {}
            for query in queries:
                if query.query_text not in unique_queries:
                    unique_queries[query.query_text] = query
                else:
                    # Merge data if duplicate
                    existing = unique_queries[query.query_text]
                    existing.frequency += query.frequency
            
            return list(unique_queries.values())
            
        except Exception as e:
            print(f"   ❌ Error analyzing {url}: {e}")
            return []
    
    def _extract_from_title(self, soup: BeautifulSoup, url: str) -> List[SearchQuery]:
        """Extract queries from title tag"""
        queries = []
        title_tag = soup.find('title')
        
        if title_tag:
            title_text = title_tag.get_text().strip()
            # Extract n-grams from title
            ngrams = self._extract_ngrams(title_text, max_n=5)
            
            for ngram_text, ngram_size in ngrams:
                query = SearchQuery(
                    query_text=ngram_text,
                    source=KeywordSource.TITLE,
                    frequency=1,
                    context_snippet=title_text[:200],
                    ngram_size=ngram_size,
                    is_long_tail=(ngram_size >= 3)
                )
                # Analyze intent
                query = self._analyze_query_intent(query, url)
                queries.append(query)
        
        return queries
    
    def _extract_from_meta(self, soup: BeautifulSoup, url: str) -> List[SearchQuery]:
        """Extract queries from meta description"""
        queries = []
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        
        if meta_desc and meta_desc.get('content'):
            meta_text = meta_desc.get('content').strip()
            ngrams = self._extract_ngrams(meta_text, max_n=4)
            
            for ngram_text, ngram_size in ngrams:
                query = SearchQuery(
                    query_text=ngram_text,
                    source=KeywordSource.META,
                    frequency=1,
                    context_snippet=meta_text[:200],
                    ngram_size=ngram_size,
                    is_long_tail=(ngram_size >= 3)
                )
                query = self._analyze_query_intent(query, url)
                queries.append(query)
        
        return queries
    
    def _extract_from_headings(self, soup: BeautifulSoup, url: str) -> List[SearchQuery]:
        """Extract queries from H1-H6 tags"""
        queries = []
        
        for level in range(1, 7):
            headings = soup.find_all(f'h{level}')
            source_map = {
                1: KeywordSource.H1, 2: KeywordSource.H2, 3: KeywordSource.H3,
                4: KeywordSource.H4, 5: KeywordSource.H5, 6: KeywordSource.H6
            }
            
            for heading in headings:
                heading_text = heading.get_text().strip()
                ngrams = self._extract_ngrams(heading_text, max_n=5)
                
                for ngram_text, ngram_size in ngrams:
                    query = SearchQuery(
                        query_text=ngram_text,
                        source=source_map[level],
                        frequency=1,
                        context_snippet=heading_text[:200],
                        ngram_size=ngram_size,
                        is_long_tail=(ngram_size >= 3)
                    )
                    query = self._analyze_query_intent(query, url)
                    queries.append(query)
        
        return queries
    
    def _extract_from_content(self, soup: BeautifulSoup, url: str) -> List[SearchQuery]:
        """Extract queries from main content"""
        queries = []
        
        # Remove unwanted elements
        for element in soup(['nav', 'footer', 'header', 'aside', 'script', 'style']):
            element.decompose()
        
        # Get main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|post'))
        
        if main_content:
            content_text = main_content.get_text()
        else:
            content_text = soup.get_text()
        
        # Extract ngrams from content
        ngrams = self._extract_ngrams(content_text, max_n=4, min_frequency=2)
        
        for ngram_text, ngram_size, frequency in ngrams:
            # Find context
            context = self._find_context(ngram_text, content_text)
            
            query = SearchQuery(
                query_text=ngram_text,
                source=KeywordSource.CONTENT,
                frequency=frequency,
                context_snippet=context,
                ngram_size=ngram_size,
                is_long_tail=(ngram_size >= 3)
            )
            query = self._analyze_query_intent(query, url)
            queries.append(query)
        
        return queries
    
    def _extract_from_url(self, url: str) -> List[SearchQuery]:
        """Extract queries from URL path"""
        queries = []
        
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        for part in path_parts:
            if part:
                # Clean URL part (replace hyphens/underscores with spaces)
                clean_part = re.sub(r'[-_]', ' ', part)
                ngrams = self._extract_ngrams(clean_part, max_n=3)
                
                for ngram_text, ngram_size in ngrams:
                    query = SearchQuery(
                        query_text=ngram_text,
                        source=KeywordSource.URL,
                        frequency=1,
                        context_snippet=part,
                        ngram_size=ngram_size,
                        is_long_tail=(ngram_size >= 3)
                    )
                    query = self._analyze_query_intent(query, url)
                    queries.append(query)
        
        return queries
    
    def _extract_ngrams(self, text: str, max_n: int = 5, min_frequency: int = 1) -> List[Tuple]:
        """
        Extract n-grams (1 to max_n words) from text.
        Returns list of (ngram_text, ngram_size) or (ngram_text, ngram_size, frequency)
        """
        # Clean and tokenize
        text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
        words = [w.strip().lower() for w in text.split() if w.strip()]
        
        # Filter stop words
        words = [w for w in words if self._is_valid_word(w)]
        
        if len(words) == 0:
            return []
        
        ngrams_dict = defaultdict(int)
        
        # Extract n-grams of different sizes
        for n in range(1, min(max_n + 1, len(words) + 1)):
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                if self._is_valid_ngram(ngram):
                    ngrams_dict[ngram] += 1
        
        # Filter by frequency
        if min_frequency > 1:
            filtered = [(ngram, len(ngram.split()), freq) 
                       for ngram, freq in ngrams_dict.items() 
                       if freq >= min_frequency]
            return filtered
        else:
            return [(ngram, len(ngram.split())) for ngram in ngrams_dict.keys()]
    
    def _is_valid_word(self, word: str) -> bool:
        """Check if word is valid (not stop word, not too short)"""
        if not word or len(word) < 2:
            return False
        if not word.isalpha():
            return False
        if word in PERSIAN_STOP_WORDS or word in ENGLISH_STOP_WORDS:
            return False
        return True
    
    def _is_valid_ngram(self, ngram: str) -> bool:
        """Check if n-gram is valid"""
        words = ngram.split()
        if len(words) == 0:
            return False
        
        # Single word: use word validation
        if len(words) == 1:
            return self._is_valid_word(words[0])
        
        # Multi-word: at least one word should be meaningful
        meaningful_count = sum(1 for w in words if self._is_valid_word(w))
        return meaningful_count >= max(1, len(words) // 2)
    
    def _find_context(self, query: str, text: str, context_length: int = 100) -> str:
        """Find context around query in text"""
        try:
            index = text.lower().find(query.lower())
            if index == -1:
                return ""
            
            start = max(0, index - context_length)
            end = min(len(text), index + len(query) + context_length)
            
            return text[start:end].strip()
        except:
            return ""
    
    def _analyze_query_intent(self, query: SearchQuery, url: str) -> SearchQuery:
        """Analyze and set intent for a query using intent analyzer"""
        try:
            # Use existing intent analyzer
            intent_result = self.intent_analyzer.analyze_intent(url)
            
            # Map intent
            query.search_intent = intent_result.get('intent', SearchIntent.INFORMATIONAL)
            
            # Set entity context based on intent
            if query.search_intent == SearchIntent.LOCAL:
                query.entity_context = "local_business"
            elif query.search_intent == SearchIntent.TRANSACTIONAL:
                query.entity_context = "product_service"
            elif query.search_intent == SearchIntent.INFORMATIONAL:
                query.entity_context = "information"
            
            # Suggest SERP features based on intent
            query.serp_features = self._suggest_serp_features(query)
            
            # Suggest content type
            query.recommended_content_type = self._suggest_content_type(query)
            
        except Exception as e:
            # Fallback to basic intent detection
            query.search_intent = self._basic_intent_detection(query.query_text)
        
        return query
    
    def _basic_intent_detection(self, query_text: str) -> SearchIntent:
        """Basic intent detection as fallback"""
        query_lower = query_text.lower()
        
        # Transactional signals
        if any(word in query_lower for word in ['خرید', 'قیمت', 'buy', 'price', 'رزرو', 'book', 'order']):
            return SearchIntent.TRANSACTIONAL
        
        # Local signals
        if any(word in query_lower for word in ['نزدیک', 'تهران', 'near', 'location', 'آدرس', 'address']):
            return SearchIntent.LOCAL
        
        # Comparison signals
        if any(word in query_lower for word in ['بهترین', 'مقایسه', 'best', 'vs', 'compare', 'چه', 'کدام']):
            return SearchIntent.COMPARISON
        
        # Default to informational
        return SearchIntent.INFORMATIONAL
    
    def _suggest_serp_features(self, query: SearchQuery) -> List[SERPFeatureType]:
        """Suggest SERP features based on query characteristics"""
        features = []
        
        query_lower = query.query_text.lower()
        
        # FAQ potential
        if any(word in query_lower for word in ['چگونه', 'چطور', 'how', 'چرا', 'why', 'چیست', 'what']):
            features.append(SERPFeatureType.FAQ)
            features.append(SERPFeatureType.PEOPLE_ALSO_ASK)
        
        # HowTo potential
        if any(word in query_lower for word in ['آموزش', 'راهنما', 'tutorial', 'guide', 'how to']):
            features.append(SERPFeatureType.HOWTO)
        
        # Video potential
        if any(word in query_lower for word in ['ویدیو', 'فیلم', 'video', 'watch']):
            features.append(SERPFeatureType.VIDEO)
        
        # Local pack potential
        if query.search_intent == SearchIntent.LOCAL:
            features.append(SERPFeatureType.LOCAL_PACK)
        
        return features
    
    def _suggest_content_type(self, query: SearchQuery) -> PageType:
        """Suggest content type based on query"""
        if query.search_intent == SearchIntent.TRANSACTIONAL:
            return PageType.SERVICE
        elif query.search_intent == SearchIntent.LOCAL:
            return PageType.LOCAL
        elif query.search_intent == SearchIntent.COMPARISON:
            return PageType.ARTICLE
        elif 'how' in query.query_text.lower() or 'چگونه' in query.query_text:
            return PageType.FAQ
        else:
            return PageType.ARTICLE
    
    def _identify_gaps_and_score(
        self,
        own_queries: List[SearchQuery],
        competitor_queries: Dict[str, List[SearchQuery]],
        context: Optional[BusinessContext]
    ) -> List[KeywordGapOpportunity]:
        """
        Identify gaps and score each opportunity.
        """
        # Create own keywords set for quick lookup
        own_keywords_set = {q.query_text.lower() for q in own_queries}
        
        # Collect all competitor queries
        all_competitor_queries = {}
        for competitor_url, queries in competitor_queries.items():
            for query in queries:
                key = query.query_text.lower()
                if key not in all_competitor_queries:
                    all_competitor_queries[key] = []
                all_competitor_queries[key].append((competitor_url, query))
        
        # Identify gaps
        gap_opportunities = []
        
        for query_text, competitor_data in all_competitor_queries.items():
            # Skip if we already have this keyword
            if query_text in own_keywords_set:
                continue
            
            # Get best version of this query from competitors
            best_query = max([q for _, q in competitor_data], 
                           key=lambda x: x.frequency)
            
            # Create opportunity
            opportunity = KeywordGapOpportunity(query=best_query)
            
            # Set gap type
            opportunity.gap_type = "missing"
            
            # Set visibility
            opportunity.own_visibility = 0.0
            opportunity.competitor_visibility = len(competitor_data) / len(competitor_queries)
            opportunity.visibility_gap = opportunity.competitor_visibility
            
            # Collect competitor URLs
            opportunity.top_competitor_urls = [url for url, _ in competitor_data[:3]]
            best_query.found_on_competitors = [url for url, _ in competitor_data]
            
            # Score the opportunity
            opportunity = self._score_opportunity(opportunity, context)
            
            gap_opportunities.append(opportunity)
        
        # Sort by opportunity score
        gap_opportunities.sort(key=lambda x: x.opportunity_score, reverse=True)
        
        return gap_opportunities
    
    def _score_opportunity(
        self,
        opportunity: KeywordGapOpportunity,
        context: Optional[BusinessContext]
    ) -> KeywordGapOpportunity:
        """
        Multi-dimensional scoring of opportunity.
        """
        query = opportunity.query
        
        # 1. Volume Score (based on frequency and presence)
        frequency_score = min(query.frequency / 10.0, 1.0)  # Normalize to 0-1
        presence_score = min(len(query.found_on_competitors) / 5.0, 1.0)
        opportunity.volume_score = (frequency_score + presence_score) / 2.0 * 100
        
        # 2. Relevance Score (business context)
        if context:
            opportunity.relevance_score = self._calculate_relevance(query, context)
        else:
            opportunity.relevance_score = 50.0  # Default moderate relevance
        
        # 3. Difficulty Score (inverse - easier = higher score)
        difficulty_map = {
            KeywordDifficulty.EASY: 100,
            KeywordDifficulty.MEDIUM: 70,
            KeywordDifficulty.HARD: 40,
            KeywordDifficulty.VERY_HARD: 20
        }
        opportunity.difficulty_score = difficulty_map.get(query.difficulty, 70)
        
        # 4. Intent Match Score
        opportunity.intent_match_score = self._calculate_intent_match(query, context)
        
        # 5. Competition Score (gap in coverage)
        opportunity.competition_score = opportunity.visibility_gap * 100
        
        # Calculate overall opportunity score (weighted average)
        weights = {
            'volume': 0.25,
            'relevance': 0.30,
            'difficulty': 0.20,
            'intent': 0.15,
            'competition': 0.10
        }
        
        opportunity.opportunity_score = (
            opportunity.volume_score * weights['volume'] +
            opportunity.relevance_score * weights['relevance'] +
            opportunity.difficulty_score * weights['difficulty'] +
            opportunity.intent_match_score * weights['intent'] +
            opportunity.competition_score * weights['competition']
        )
        
        # Estimate traffic and ROI
        opportunity.estimated_monthly_traffic = int(query.frequency * len(query.found_on_competitors) * 50)
        
        # Estimate effort
        effort_map = {
            KeywordDifficulty.EASY: 2,
            KeywordDifficulty.MEDIUM: 5,
            KeywordDifficulty.HARD: 10,
            KeywordDifficulty.VERY_HARD: 20
        }
        opportunity.effort_estimate_hours = effort_map.get(query.difficulty, 5)
        
        # Set priority tier
        opportunity = self._set_priority_tier(opportunity)
        
        # Generate recommendations
        opportunity.recommended_actions = self._generate_actions(opportunity)
        
        return opportunity
    
    def _calculate_relevance(self, query: SearchQuery, context: BusinessContext) -> float:
        """Calculate business relevance score (0-100)"""
        score = 0.0
        query_lower = query.query_text.lower()
        
        # Check services match
        for service in context.services:
            if service.lower() in query_lower:
                score += 30.0
                break
        
        # Check products match
        for product in context.products:
            if product.lower() in query_lower:
                score += 25.0
                break
        
        # Check niche match
        niche_words = context.niche.lower().split()
        niche_match = sum(1 for word in niche_words if word in query_lower)
        score += min(niche_match * 10, 30)
        
        # Check location match
        for location in context.target_locations:
            if location.lower() in query_lower:
                score += 15.0
                break
        
        return min(score, 100.0)
    
    def _calculate_intent_match(self, query: SearchQuery, context: Optional[BusinessContext]) -> float:
        """Calculate how well intent matches business model"""
        # If transactional/local and business offers services = high match
        if query.search_intent in [SearchIntent.TRANSACTIONAL, SearchIntent.LOCAL]:
            return 90.0
        elif query.search_intent == SearchIntent.INFORMATIONAL:
            return 70.0  # Good for TOFU content
        elif query.search_intent == SearchIntent.COMPARISON:
            return 80.0  # Good for MOFU
        else:
            return 60.0
    
    def _set_priority_tier(self, opportunity: KeywordGapOpportunity) -> KeywordGapOpportunity:
        """Set priority tier based on scores"""
        score = opportunity.opportunity_score
        relevance = opportunity.relevance_score
        difficulty = opportunity.difficulty_score
        
        # Quick Wins: High relevance + Easy difficulty + Good score
        if relevance >= 70 and difficulty >= 80 and score >= 70:
            opportunity.priority_tier = "quick_win"
            opportunity.priority_reasoning = "High relevance, easy to rank, good opportunity"
        
        # High Priority: High score + High relevance
        elif score >= 75 and relevance >= 60:
            opportunity.priority_tier = "high_priority"
            opportunity.priority_reasoning = "High overall value and relevance"
        
        # Long-term: Hard but valuable
        elif difficulty < 50 and relevance >= 70:
            opportunity.priority_tier = "long_term"
            opportunity.priority_reasoning = "High value but requires significant effort"
        
        # Medium: Everything else
        else:
            opportunity.priority_tier = "medium"
            opportunity.priority_reasoning = "Moderate opportunity"
        
        return opportunity
    
    def _generate_actions(self, opportunity: KeywordGapOpportunity) -> List[str]:
        """Generate actionable recommendations"""
        actions = []
        query = opportunity.query
        
        # Content creation
        if opportunity.gap_type == "missing":
            actions.append(f"Create {query.recommended_content_type.value} page targeting '{query.query_text}'")
        
        # SERP features
        if query.serp_features:
            features_str = ", ".join([f.value for f in query.serp_features[:2]])
            actions.append(f"Implement {features_str} for better visibility")
        
        # Intent-specific
        if query.search_intent == SearchIntent.LOCAL:
            actions.append("Add local SEO elements (NAP, maps, reviews)")
        elif query.search_intent == SearchIntent.TRANSACTIONAL:
            actions.append("Add clear CTAs and conversion elements")
        
        # Based on source
        if query.source in [KeywordSource.TITLE, KeywordSource.H1]:
            actions.append("Use keyword in page title and H1")
        
        return actions
    
    def _difficulty_to_score(self, difficulty: KeywordDifficulty) -> float:
        """Convert difficulty enum to numeric score"""
        map = {
            KeywordDifficulty.EASY: 1.0,
            KeywordDifficulty.MEDIUM: 2.0,
            KeywordDifficulty.HARD: 3.0,
            KeywordDifficulty.VERY_HARD: 4.0
        }
        return map.get(difficulty, 2.0)
    
    def _categorize_opportunities(
        self,
        opportunities: List[KeywordGapOpportunity]
    ) -> Dict[str, List[KeywordGapOpportunity]]:
        """Categorize opportunities by priority and intent"""
        categorized = {
            'quick_wins': [],
            'high_priority': [],
            'medium': [],
            'long_term': [],
            'informational': [],
            'transactional': [],
            'local': [],
            'comparison': [],
            'navigational': []
        }
        
        for opp in opportunities:
            # By priority
            categorized[opp.priority_tier].append(opp)
            
            # By intent
            intent_key = opp.query.search_intent.value
            if intent_key in categorized:
                categorized[intent_key].append(opp)
        
        return categorized
    
    def _generate_strategic_recommendations(
        self,
        opportunities: List[KeywordGapOpportunity],
        categorized: Dict[str, List[KeywordGapOpportunity]],
        context: Optional[BusinessContext]
    ) -> Dict[str, List[Dict]]:
        """Generate strategic recommendations and content calendar"""
        recommendations = {
            'strategic': [],
            'calendar': []
        }
        
        # Strategic recommendation 1: Focus on quick wins
        if categorized['quick_wins']:
            recommendations['strategic'].append({
                'title': 'Focus on Quick Wins First',
                'priority': 'high',
                'description': f"You have {len(categorized['quick_wins'])} quick win opportunities with high relevance and low difficulty.",
                'action': 'Start creating content for these keywords within the next 2-4 weeks',
                'keywords': [opp.query.query_text for opp in categorized['quick_wins'][:10]]
            })
        
        # Strategic recommendation 2: Build TOFU content
        if categorized['informational']:
            recommendations['strategic'].append({
                'title': 'Build Top-of-Funnel Content',
                'priority': 'medium',
                'description': f"Found {len(categorized['informational'])} informational keywords for awareness stage.",
                'action': 'Create comprehensive guides and how-to content',
                'keywords': [opp.query.query_text for opp in categorized['informational'][:10]]
            })
        
        # Strategic recommendation 3: Optimize for conversions
        if categorized['transactional']:
            recommendations['strategic'].append({
                'title': 'Capture Transactional Intent',
                'priority': 'high',
                'description': f"{len(categorized['transactional'])} transactional keywords found - direct revenue potential.",
                'action': 'Create service/product pages with strong CTAs',
                'keywords': [opp.query.query_text for opp in categorized['transactional'][:10]]
            })
        
        # Content calendar (prioritized by opportunity score)
        top_opportunities = sorted(opportunities, key=lambda x: x.opportunity_score, reverse=True)[:20]
        
        for i, opp in enumerate(top_opportunities, 1):
            recommendations['calendar'].append({
                'week': (i - 1) // 3 + 1,  # Group 3 per week
                'keyword': opp.query.query_text,
                'content_type': opp.query.recommended_content_type.value,
                'priority': opp.priority_tier,
                'effort_hours': opp.effort_estimate_hours,
                'estimated_traffic': opp.estimated_monthly_traffic,
                'actions': opp.recommended_actions
            })
        
        return recommendations
    
    def save_results(self, result: KeywordGapAnalysisResult, filename: str = None) -> str:
        """Save analysis results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"keyword_gap_analysis_v2_{timestamp}.json"
        
        # Convert to dict
        result_dict = self._result_to_dict(result)
        
        # Save to file
        import os
        results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        filepath = os.path.join(results_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Results saved to: {filepath}")
        return filepath
    
    def _result_to_dict(self, result: KeywordGapAnalysisResult) -> Dict:
        """Convert result to dictionary for JSON serialization"""
        # This is a simplified version - you'd want to properly serialize all dataclasses
        return {
            'own_website_url': result.own_website_url,
            'competitor_urls': result.competitor_urls,
            'total_gaps_found': result.total_gaps_found,
            'total_opportunity_value': result.total_opportunity_value,
            'avg_difficulty': result.avg_difficulty,
            'avg_relevance': result.avg_relevance,
            'processing_time_seconds': result.processing_time_seconds,
            'analysis_date': result.analysis_date.isoformat(),
            'analysis_version': result.analysis_version,
            # Simplified - add full serialization as needed
            'quick_wins_count': len(result.quick_wins),
            'high_priority_count': len(result.high_priority),
            'recommendations': result.strategic_recommendations
        }

