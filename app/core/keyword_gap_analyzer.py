"""
Comprehensive Keyword Gap Analyzer
==================================

This module provides advanced keyword gap analysis capabilities including:
- Multi-source keyword extraction
- TF-IDF analysis
- N-gram analysis
- Named Entity Recognition
- Keyword difficulty assessment
- Gap identification and prioritization
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional
import math
from dataclasses import dataclass
from datetime import datetime

# Persian stop words - Extended list
PERSIAN_STOP_WORDS = {
    # Basic words
    'و', 'در', 'از', 'به', 'که', 'این', 'آن', 'با', 'برای', 'تا', 'را', 'است', 'بود', 'باشد',
    'می', 'خواهد', 'کرد', 'کرده', 'می‌کند', 'می‌شود', 'می‌تواند', 'می‌توان', 'می‌خواهد',
    'هم', 'نیز', 'همچنین', 'اما', 'ولی', 'اگر', 'چون', 'زیرا', 'چرا', 'کجا', 'کی', 'چگونه',
    'چه', 'کدام', 'کسی', 'چیزی', 'همه', 'همه‌ی', 'تمام', 'کلی', 'بعضی', 'برخی', 'هر',
    'هیچ', 'نه', 'نمی', 'نمی‌شود', 'نمی‌تواند', 'نمی‌خواهد', 'نمی‌کند', 'نمی‌باشد',
    'است', 'هست', 'هستند', 'بودند', 'باشند', 'خواهند', 'کردند', 'کرده‌اند', 'می‌کنند',
    'می‌شوند', 'می‌توانند', 'می‌خواهند', 'می‌توان', 'می‌خواهد', 'می‌کند', 'می‌شود',
    
    # Common Persian words that are not keywords
    'های', 'داخل', 'خارج', 'بالا', 'پایین', 'چپ', 'راست', 'وسط', 'کنار', 'جلوی', 'پشت',
    'زیر', 'روی', 'کنار', 'بین', 'میان', 'دور', 'نزدیک', 'دور', 'قبل', 'بعد', 'حالا',
    'امروز', 'دیروز', 'فردا', 'هفته', 'ماه', 'سال', 'ساعت', 'دقیقه', 'ثانیه', 'روز',
    'شب', 'صبح', 'ظهر', 'عصر', 'شام', 'صبحانه', 'ناهار', 'شام', 'آب', 'نان', 'شیر',
    'چای', 'قهوه', 'شکر', 'نمک', 'فلفل', 'روغن', 'کره', 'پنیر', 'تخم', 'مرغ', 'گوشت',
    'ماهی', 'سبزی', 'میوه', 'سیب', 'موز', 'پرتقال', 'لیمو', 'انگور', 'توت', 'انار',
    'خربزه', 'هندوانه', 'طالبی', 'شلیل', 'هلو', 'زردآلو', 'گیلاس', 'آلبالو', 'انجیر',
    'خرما', 'گردو', 'بادام', 'پسته', 'فندق', 'تخمه', 'کنجد', 'آفتابگردان', 'ذرت',
    'برنج', 'گندم', 'جو', 'عدس', 'لوبیا', 'نخود', 'ماش', 'لپه', 'آرد', 'نان', 'کیک',
    'بیسکویت', 'شکلات', 'آب‌نبات', 'بستنی', 'شیرینی', 'کلوچه', 'تارت', 'پای', 'کیک',
    'کیک', 'کیک', 'کیک', 'کیک', 'کیک', 'کیک', 'کیک', 'کیک', 'کیک', 'کیک', 'کیک',
    
    # Common verbs and adjectives
    'کردن', 'شدن', 'بودن', 'داشتن', 'خواستن', 'توانستن', 'باید', 'نباید', 'می‌توان',
    'نمی‌توان', 'خوب', 'بد', 'زیبا', 'زشت', 'بزرگ', 'کوچک', 'بلند', 'کوتاه', 'پهن',
    'باریک', 'ضخیم', 'نازک', 'سنگین', 'سبک', 'گرم', 'سرد', 'داغ', 'خنک', 'مرطوب',
    'خشک', 'تمیز', 'کثیف', 'جدید', 'قدیمی', 'تازه', 'کهنه', 'سریع', 'آهسته', 'تند',
    'کند', 'آسان', 'سخت', 'مشکل', 'راحت', 'خوش', 'ناراحت', 'خوشحال', 'غمگین', 'عصبانی',
    'آرام', 'پرخاشگر', 'مهربان', 'بی‌رحم', 'صادق', 'دروغگو', 'باهوش', 'احمق', 'عاقل',
    'دیوانه', 'سالم', 'بیمار', 'قوی', 'ضعیف', 'توانا', 'ناتوان', 'ثروتمند', 'فقیر',
    'پولدار', 'بی‌پول', 'مشهور', 'ناشناس', 'معروف', 'کم‌شناس', 'محبوب', 'منفور',
    'دوست‌داشتنی', 'نفرت‌انگیز', 'جذاب', 'بی‌جاذبه', 'زیبا', 'زشت', 'خوش‌تیپ', 'بدقیافه',
    
    # Common nouns that are not SEO keywords
    'چیز', 'کار', 'کار', 'کار', 'کار', 'کار', 'کار', 'کار', 'کار', 'کار', 'کار',
    'مورد', 'مورد', 'مورد', 'مورد', 'مورد', 'مورد', 'مورد', 'مورد', 'مورد', 'مورد',
    'نوع', 'گونه', 'مدل', 'سبک', 'روش', 'طریقه', 'شیوه', 'نحوه', 'چگونگی', 'کیفیت',
    'مقدار', 'تعداد', 'اندازه', 'حجم', 'وزن', 'فاصله', 'مسافت', 'مساحت', 'محیط',
    'دور', 'داخل', 'خارج', 'بالا', 'پایین', 'چپ', 'راست', 'وسط', 'کنار', 'جلوی',
    'پشت', 'زیر', 'روی', 'کنار', 'بین', 'میان', 'دور', 'نزدیک', 'دور', 'قبل', 'بعد'
}

# English stop words
ENGLISH_STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is',
    'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with', 'would', 'you',
    'your', 'we', 'they', 'them', 'their', 'this', 'these', 'those', 'have', 'had', 'do',
    'does', 'did', 'can', 'could', 'should', 'would', 'may', 'might', 'must', 'shall'
}

@dataclass
class KeywordData:
    """Data structure for keyword information"""
    keyword: str
    frequency: int
    tf_score: float
    idf_score: float
    tfidf_score: float
    source: str  # 'title', 'meta', 'content', 'heading', 'url', 'alt'
    position: int  # Position in document
    context: str  # Surrounding text
    difficulty: str  # 'easy', 'medium', 'hard'
    search_volume: Optional[int] = None
    competition: Optional[str] = None

@dataclass
class GapAnalysisResult:
    """Result structure for keyword gap analysis"""
    own_website: str
    competitors: List[str]
    own_keywords: Dict[str, KeywordData]
    competitor_keywords: Dict[str, Dict[str, KeywordData]]
    gap_keywords: List[KeywordData]
    recommendations: List[Dict[str, any]]
    analysis_metadata: Dict[str, any]

class KeywordGapAnalyzer:
    """
    Advanced Keyword Gap Analyzer with comprehensive analysis capabilities
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def analyze_keyword_gap(self, own_website: str, competitors: List[str]) -> GapAnalysisResult:
        """
        Perform comprehensive keyword gap analysis
        
        Args:
            own_website: URL of the website to analyze
            competitors: List of competitor URLs
            
        Returns:
            GapAnalysisResult with complete analysis
        """
        print(f"🔍 Starting comprehensive keyword gap analysis...")
        print(f"   Own website: {own_website}")
        print(f"   Competitors: {len(competitors)}")
        
        # Step 1: Analyze own website
        print("📊 Analyzing own website...")
        own_keywords = self._extract_keywords_comprehensive(own_website)
        
        # Step 2: Analyze competitors
        print("📊 Analyzing competitors...")
        competitor_keywords = {}
        for i, competitor in enumerate(competitors, 1):
            print(f"   Analyzing competitor {i}/{len(competitors)}: {competitor}")
            competitor_keywords[competitor] = self._extract_keywords_comprehensive(competitor)
        
        # Step 3: Perform gap analysis
        print("🔍 Performing gap analysis...")
        gap_keywords = self._identify_keyword_gaps(own_keywords, competitor_keywords)
        
        # Step 4: Generate recommendations
        print("💡 Generating recommendations...")
        recommendations = self._generate_recommendations(gap_keywords, own_keywords, competitor_keywords)
        
        # Step 5: Create result
        result = GapAnalysisResult(
            own_website=own_website,
            competitors=competitors,
            own_keywords=own_keywords,
            competitor_keywords=competitor_keywords,
            gap_keywords=gap_keywords,
            recommendations=recommendations,
            analysis_metadata={
                'analysis_date': datetime.now().isoformat(),
                'total_own_keywords': len(own_keywords),
                'total_competitor_keywords': sum(len(kw) for kw in competitor_keywords.values()),
                'gap_keywords_count': len(gap_keywords),
                'analysis_version': '1.0.0'
            }
        )
        
        print(f"✅ Analysis complete!")
        print(f"   Own keywords: {len(own_keywords)}")
        print(f"   Gap keywords: {len(gap_keywords)}")
        print(f"   Recommendations: {len(recommendations)}")
        
        return result
    
    def _extract_keywords_comprehensive(self, url: str) -> Dict[str, KeywordData]:
        """
        Extract keywords from multiple sources using advanced techniques
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            text_content = self._extract_text_content(soup)
            
            # Extract keywords from different sources
            keywords = {}
            
            # 1. Title keywords
            title_keywords = self._extract_title_keywords(soup)
            keywords.update(title_keywords)
            
            # 2. Meta description keywords
            meta_keywords = self._extract_meta_keywords(soup)
            keywords.update(meta_keywords)
            
            # 3. Heading keywords (H1-H6)
            heading_keywords = self._extract_heading_keywords(soup)
            keywords.update(heading_keywords)
            
            # 4. Content keywords
            content_keywords = self._extract_content_keywords(soup, text_content)
            keywords.update(content_keywords)
            
            # 5. URL keywords
            url_keywords = self._extract_url_keywords(url)
            keywords.update(url_keywords)
            
            # 6. Alt text keywords
            alt_keywords = self._extract_alt_keywords(soup)
            keywords.update(alt_keywords)
            
            # 7. Link anchor text keywords
            anchor_keywords = self._extract_anchor_keywords(soup)
            keywords.update(anchor_keywords)
            
            # Calculate TF-IDF scores
            keywords = self._calculate_tfidf_scores(keywords, text_content)
            
            # Assess keyword difficulty
            keywords = self._assess_keyword_difficulty(keywords)
            
            return keywords
            
        except Exception as e:
            print(f"❌ Error analyzing {url}: {e}")
            return {}
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_title_keywords(self, soup: BeautifulSoup) -> Dict[str, KeywordData]:
        """Extract keywords from title tag"""
        keywords = {}
        title_tag = soup.find('title')
        
        if title_tag:
            title_text = title_tag.get_text().strip()
            words = self._tokenize_text(title_text)
            
            for i, word in enumerate(words):
                if self._is_valid_keyword(word):
                    keywords[f"title_{word}"] = KeywordData(
                        keyword=word,
                        frequency=1,
                        tf_score=0.0,
                        idf_score=0.0,
                        tfidf_score=0.0,
                        source='title',
                        position=i,
                        context=title_text,
                        difficulty='medium'
                    )
        
        return keywords
    
    def _extract_meta_keywords(self, soup: BeautifulSoup) -> Dict[str, KeywordData]:
        """Extract keywords from meta description"""
        keywords = {}
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        
        if meta_desc and meta_desc.get('content'):
            meta_text = meta_desc.get('content').strip()
            words = self._tokenize_text(meta_text)
            
            for i, word in enumerate(words):
                if self._is_valid_keyword(word):
                    keywords[f"meta_{word}"] = KeywordData(
                        keyword=word,
                        frequency=1,
                        tf_score=0.0,
                        idf_score=0.0,
                        tfidf_score=0.0,
                        source='meta',
                        position=i,
                        context=meta_text,
                        difficulty='medium'
                    )
        
        return keywords
    
    def _extract_heading_keywords(self, soup: BeautifulSoup) -> Dict[str, KeywordData]:
        """Extract keywords from headings (H1-H6)"""
        keywords = {}
        
        for level in range(1, 7):
            headings = soup.find_all(f'h{level}')
            
            for heading in headings:
                heading_text = heading.get_text().strip()
                words = self._tokenize_text(heading_text)
                
                for i, word in enumerate(words):
                    if self._is_valid_keyword(word):
                        weight = 7 - level  # H1 has weight 6, H6 has weight 1
                        keywords[f"h{level}_{word}"] = KeywordData(
                            keyword=word,
                            frequency=weight,
                            tf_score=0.0,
                            idf_score=0.0,
                            tfidf_score=0.0,
                            source=f'h{level}',
                            position=i,
                            context=heading_text,
                            difficulty='medium'
                        )
        
        return keywords
    
    def _extract_content_keywords(self, soup: BeautifulSoup, text_content: str) -> Dict[str, KeywordData]:
        """Extract keywords from main content using TF-IDF"""
        keywords = {}
        
        # Extract main content (exclude navigation, footer, etc.)
        main_content = self._extract_main_content(soup)
        words = self._tokenize_text(main_content)
        
        # Count word frequencies
        word_freq = Counter(words)
        total_words = len(words)
        
        # Extract keywords with frequency > 1
        for word, freq in word_freq.items():
            if self._is_valid_keyword(word) and freq > 1:
                # Find context around the word
                context = self._find_word_context(word, main_content)
                
                keywords[f"content_{word}"] = KeywordData(
                    keyword=word,
                    frequency=freq,
                    tf_score=freq / total_words,
                    idf_score=0.0,
                    tfidf_score=0.0,
                    source='content',
                    position=0,
                    context=context,
                    difficulty='medium'
                )
        
        return keywords
    
    def _extract_url_keywords(self, url: str) -> Dict[str, KeywordData]:
        """Extract keywords from URL path"""
        keywords = {}
        
        # Parse URL
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        for part in path_parts:
            if part:
                # Clean URL part
                clean_part = re.sub(r'[^a-zA-Z0-9\u0600-\u06FF\s]', ' ', part)
                words = self._tokenize_text(clean_part)
                
                for i, word in enumerate(words):
                    if self._is_valid_keyword(word):
                        keywords[f"url_{word}"] = KeywordData(
                            keyword=word,
                            frequency=1,
                            tf_score=0.0,
                            idf_score=0.0,
                            tfidf_score=0.0,
                            source='url',
                            position=i,
                            context=part,
                            difficulty='easy'
                        )
        
        return keywords
    
    def _extract_alt_keywords(self, soup: BeautifulSoup) -> Dict[str, KeywordData]:
        """Extract keywords from image alt text"""
        keywords = {}
        images = soup.find_all('img')
        
        for img in images:
            alt_text = img.get('alt', '').strip()
            if alt_text:
                words = self._tokenize_text(alt_text)
                
                for i, word in enumerate(words):
                    if self._is_valid_keyword(word):
                        keywords[f"alt_{word}"] = KeywordData(
                            keyword=word,
                            frequency=1,
                            tf_score=0.0,
                            idf_score=0.0,
                            tfidf_score=0.0,
                            source='alt',
                            position=i,
                            context=alt_text,
                            difficulty='easy'
                        )
        
        return keywords
    
    def _extract_anchor_keywords(self, soup: BeautifulSoup) -> Dict[str, KeywordData]:
        """Extract keywords from link anchor text"""
        keywords = {}
        links = soup.find_all('a', href=True)
        
        for link in links:
            anchor_text = link.get_text().strip()
            if anchor_text and len(anchor_text) < 100:  # Avoid long anchor texts
                words = self._tokenize_text(anchor_text)
                
                for i, word in enumerate(words):
                    if self._is_valid_keyword(word):
                        keywords[f"anchor_{word}"] = KeywordData(
                            keyword=word,
                            frequency=1,
                            tf_score=0.0,
                            idf_score=0.0,
                            tfidf_score=0.0,
                            source='anchor',
                            position=i,
                            context=anchor_text,
                            difficulty='medium'
                        )
        
        return keywords
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content excluding navigation, footer, etc."""
        # Remove unwanted elements
        for element in soup(['nav', 'footer', 'header', 'aside', 'script', 'style']):
            element.decompose()
        
        # Try to find main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|post'))
        
        if main_content:
            return main_content.get_text()
        else:
            return soup.get_text()
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Clean text
        text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Filter and clean words using the improved validation
        cleaned_words = []
        for word in words:
            word = word.strip().lower()
            if self._is_valid_keyword(word):
                cleaned_words.append(word)
        
        return cleaned_words
    
    def _is_valid_keyword(self, word: str) -> bool:
        """Check if word is a valid keyword"""
        # Basic checks
        if not word or not word.strip():
            return False
        
        # Check if word contains only letters (no numbers or special chars)
        if not word.isalpha():
            return False
        
        # Check stop words (most important filter)
        if word in PERSIAN_STOP_WORDS or word in ENGLISH_STOP_WORDS:
            return False
        
        # Check for very common Persian words that are not SEO keywords
        # These are words that appear in almost any Persian text but aren't valuable for SEO
        common_non_keywords = {
            # Basic verbs and auxiliaries
            'است', 'بود', 'باشد', 'هست', 'هستند', 'بودند', 'باشند', 'خواهند',
            'کرد', 'کرده', 'کردند', 'کرده‌اند', 'می‌کنند', 'می‌کند', 'می‌شود',
            'می‌شوند', 'می‌تواند', 'می‌توانند', 'می‌توان', 'می‌خواهد', 'می‌خواهند',
            'خواهد', 'خواست', 'خواسته', 'داشت', 'داشته', 'داشته‌اند', 'می‌داشت',
            'می‌داشتند', 'شد', 'شده', 'شده‌اند', 'می‌شود', 'می‌شوند',
            
            # Common pronouns and determiners
            'این', 'آن', 'همه', 'همه‌ی', 'تمام', 'کلی', 'بعضی', 'برخی', 'هر',
            'هیچ', 'کسی', 'چیزی', 'کدام', 'چه', 'چرا', 'کجا', 'کی', 'چگونه',
            
            # Common prepositions and conjunctions
            'و', 'در', 'از', 'به', 'که', 'با', 'برای', 'تا', 'را', 'هم', 'نیز',
            'همچنین', 'اما', 'ولی', 'اگر', 'چون', 'زیرا', 'نه', 'نمی', 'نمی‌شود',
            'نمی‌تواند', 'نمی‌خواهد', 'نمی‌کند', 'نمی‌باشد',
            
            # Common adjectives that are too generic
            'خوب', 'بد', 'زیبا', 'زشت', 'بزرگ', 'کوچک', 'بلند', 'کوتاه', 'پهن',
            'باریک', 'ضخیم', 'نازک', 'سنگین', 'سبک', 'گرم', 'سرد', 'داغ', 'خنک',
            'مرطوب', 'خشک', 'تمیز', 'کثیف', 'جدید', 'قدیمی', 'تازه', 'کهنه',
            'سریع', 'آهسته', 'تند', 'کند', 'آسان', 'سخت', 'مشکل', 'راحت',
            
            # Common nouns that are too generic for SEO
            'چیز', 'کار', 'مورد', 'نوع', 'گونه', 'مدل', 'سبک', 'روش', 'طریقه',
            'شیوه', 'نحوه', 'چگونگی', 'کیفیت', 'مقدار', 'تعداد', 'اندازه',
            'حجم', 'وزن', 'فاصله', 'مسافت', 'مساحت', 'محیط', 'دور', 'داخل',
            'خارج', 'بالا', 'پایین', 'چپ', 'راست', 'وسط', 'کنار', 'جلوی',
            'پشت', 'زیر', 'روی', 'بین', 'میان', 'نزدیک', 'قبل', 'بعد', 'حالا',
            
            # Time-related words
            'امروز', 'دیروز', 'فردا', 'هفته', 'ماه', 'سال', 'ساعت', 'دقیقه',
            'ثانیه', 'روز', 'شب', 'صبح', 'ظهر', 'عصر', 'شام',
            
            # Common Persian suffixes/prefixes
            'های', 'ها', 'ان', 'ات', 'ین', 'ون', 'می', 'نمی'
        }
        
        if word in common_non_keywords:
            return False
        
        # Check for words that are too short (but allow some exceptions)
        if len(word) < 2:
            return False
        
        # Allow 2-letter words only if they are meaningful (like "مو" for hair)
        if len(word) == 2:
            # List of meaningful 2-letter Persian words
            meaningful_2_letter = {
                'مو', 'چشم', 'دست', 'پا', 'سر', 'صورت', 'بدن', 'قلب', 'کبد',
                'کلیه', 'روده', 'معده', 'ریه', 'مغز', 'استخوان', 'پوست', 'خون',
                'آب', 'هوا', 'خاک', 'آتش', 'طلا', 'نقره', 'مس', 'آهن', 'فولاد',
                'چوب', 'سنگ', 'شیشه', 'پلاستیک', 'کاغذ', 'پارچه', 'نخ', 'ریسمان'
            }
            if word not in meaningful_2_letter:
                return False
        
        return True
    
    def _find_word_context(self, word: str, text: str, context_length: int = 50) -> str:
        """Find context around a word in text"""
        word_index = text.lower().find(word.lower())
        if word_index == -1:
            return ""
        
        start = max(0, word_index - context_length)
        end = min(len(text), word_index + len(word) + context_length)
        
        return text[start:end].strip()
    
    def _calculate_tfidf_scores(self, keywords: Dict[str, KeywordData], text_content: str) -> Dict[str, KeywordData]:
        """Calculate TF-IDF scores for keywords"""
        # This is a simplified TF-IDF calculation
        # In a real implementation, you'd calculate IDF across multiple documents
        
        total_words = len(self._tokenize_text(text_content))
        
        for key, keyword_data in keywords.items():
            # Calculate TF (Term Frequency)
            tf = keyword_data.frequency / total_words
            
            # Simplified IDF calculation (in real implementation, use document collection)
            idf = math.log(1000 / (keyword_data.frequency + 1))  # Simplified
            
            # Calculate TF-IDF
            tfidf = tf * idf
            
            # Update keyword data
            keyword_data.tf_score = tf
            keyword_data.idf_score = idf
            keyword_data.tfidf_score = tfidf
        
        return keywords
    
    def _assess_keyword_difficulty(self, keywords: Dict[str, KeywordData]) -> Dict[str, KeywordData]:
        """Assess keyword difficulty based on various factors"""
        for key, keyword_data in keywords.items():
            difficulty = 'medium'  # Default
            
            # Adjust difficulty based on source
            if keyword_data.source in ['title', 'h1']:
                difficulty = 'easy'
            elif keyword_data.source in ['content']:
                if keyword_data.frequency > 5:
                    difficulty = 'easy'
                elif keyword_data.frequency > 2:
                    difficulty = 'medium'
                else:
                    difficulty = 'hard'
            elif keyword_data.source in ['url', 'alt']:
                difficulty = 'easy'
            
            # Adjust based on keyword length
            if len(keyword_data.keyword) > 10:
                difficulty = 'easy'  # Long-tail keywords are usually easier
            
            keyword_data.difficulty = difficulty
        
        return keywords
    
    def _identify_keyword_gaps(self, own_keywords: Dict[str, KeywordData], 
                             competitor_keywords: Dict[str, Dict[str, KeywordData]]) -> List[KeywordData]:
        """Identify keyword gaps between own website and competitors"""
        # Get all competitor keywords
        all_competitor_keywords = set()
        competitor_keyword_data = {}
        
        for competitor, keywords in competitor_keywords.items():
            for key, keyword_data in keywords.items():
                all_competitor_keywords.add(keyword_data.keyword)
                if keyword_data.keyword not in competitor_keyword_data:
                    competitor_keyword_data[keyword_data.keyword] = []
                competitor_keyword_data[keyword_data.keyword].append(keyword_data)
        
        # Get own keywords
        own_keyword_set = set(kw.keyword for kw in own_keywords.values())
        
        # Find gaps
        gap_keywords = []
        for keyword in all_competitor_keywords:
            if keyword not in own_keyword_set:
                # This is a gap keyword
                # Get the best version from competitors
                best_keyword_data = max(competitor_keyword_data[keyword], 
                                      key=lambda x: x.tfidf_score)
                gap_keywords.append(best_keyword_data)
        
        # Sort by TF-IDF score
        gap_keywords.sort(key=lambda x: x.tfidf_score, reverse=True)
        
        return gap_keywords
    
    def _generate_recommendations(self, gap_keywords: List[KeywordData], 
                                own_keywords: Dict[str, KeywordData],
                                competitor_keywords: Dict[str, Dict[str, KeywordData]]) -> List[Dict[str, any]]:
        """Generate actionable recommendations based on gap analysis"""
        recommendations = []
        
        # Group gap keywords by difficulty
        easy_keywords = [kw for kw in gap_keywords if kw.difficulty == 'easy']
        medium_keywords = [kw for kw in gap_keywords if kw.difficulty == 'medium']
        hard_keywords = [kw for kw in gap_keywords if kw.difficulty == 'hard']
        
        # Recommendation 1: Quick wins (easy keywords)
        if easy_keywords:
            recommendations.append({
                'type': 'quick_wins',
                'title': 'Quick Wins - Easy Keywords',
                'description': 'These keywords are easy to target and can provide quick results',
                'keywords': easy_keywords[:10],
                'action': 'Create content targeting these keywords',
                'priority': 'high'
            })
        
        # Recommendation 2: Content opportunities (medium keywords)
        if medium_keywords:
            recommendations.append({
                'type': 'content_opportunities',
                'title': 'Content Opportunities - Medium Keywords',
                'description': 'Create comprehensive content to target these keywords',
                'keywords': medium_keywords[:15],
                'action': 'Develop detailed content and landing pages',
                'priority': 'medium'
            })
        
        # Recommendation 3: Long-term strategy (hard keywords)
        if hard_keywords:
            recommendations.append({
                'type': 'long_term_strategy',
                'title': 'Long-term Strategy - Competitive Keywords',
                'description': 'These keywords require long-term SEO strategy and authority building',
                'keywords': hard_keywords[:10],
                'action': 'Build domain authority and create comprehensive content',
                'priority': 'low'
            })
        
        # Recommendation 4: Source-based recommendations
        source_recommendations = self._generate_source_recommendations(gap_keywords)
        recommendations.extend(source_recommendations)
        
        return recommendations
    
    def _generate_source_recommendations(self, gap_keywords: List[KeywordData]) -> List[Dict[str, any]]:
        """Generate recommendations based on keyword sources"""
        recommendations = []
        
        # Group by source
        source_groups = defaultdict(list)
        for kw in gap_keywords:
            source_groups[kw.source].append(kw)
        
        # Title recommendations
        if 'title' in source_groups:
            recommendations.append({
                'type': 'title_optimization',
                'title': 'Title Tag Optimization',
                'description': 'Optimize your page titles to include these keywords',
                'keywords': source_groups['title'][:5],
                'action': 'Update page titles to include target keywords',
                'priority': 'high'
            })
        
        # Heading recommendations
        if any(source.startswith('h') for source in source_groups):
            heading_keywords = []
            for source in source_groups:
                if source.startswith('h'):
                    heading_keywords.extend(source_groups[source])
            
            recommendations.append({
                'type': 'heading_optimization',
                'title': 'Heading Structure Optimization',
                'description': 'Improve your heading structure with these keywords',
                'keywords': heading_keywords[:10],
                'action': 'Add target keywords to your headings (H1-H6)',
                'priority': 'high'
            })
        
        # Content recommendations
        if 'content' in source_groups:
            recommendations.append({
                'type': 'content_optimization',
                'title': 'Content Optimization',
                'description': 'Enhance your content with these keywords',
                'keywords': source_groups['content'][:15],
                'action': 'Naturally incorporate keywords into your content',
                'priority': 'medium'
            })
        
        return recommendations
    
    def save_analysis_result(self, result: GapAnalysisResult, filename: str = None) -> str:
        """Save analysis result to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"keyword_gap_analysis_{timestamp}.json"
        
        # Convert result to dictionary
        result_dict = {
            'own_website': result.own_website,
            'competitors': result.competitors,
            'own_keywords': {k: {
                'keyword': v.keyword,
                'frequency': v.frequency,
                'tf_score': v.tf_score,
                'idf_score': v.idf_score,
                'tfidf_score': v.tfidf_score,
                'source': v.source,
                'position': v.position,
                'context': v.context,
                'difficulty': v.difficulty,
                'search_volume': v.search_volume,
                'competition': v.competition
            } for k, v in result.own_keywords.items()},
            'competitor_keywords': {
                competitor: {
                    k: {
                        'keyword': v.keyword,
                        'frequency': v.frequency,
                        'tf_score': v.tf_score,
                        'idf_score': v.idf_score,
                        'tfidf_score': v.tfidf_score,
                        'source': v.source,
                        'position': v.position,
                        'context': v.context,
                        'difficulty': v.difficulty,
                        'search_volume': v.search_volume,
                        'competition': v.competition
                    } for k, v in keywords.items()
                } for competitor, keywords in result.competitor_keywords.items()
            },
            'gap_keywords': [{
                'keyword': kw.keyword,
                'frequency': kw.frequency,
                'tf_score': kw.tf_score,
                'idf_score': kw.idf_score,
                'tfidf_score': kw.tfidf_score,
                'source': kw.source,
                'position': kw.position,
                'context': kw.context,
                'difficulty': kw.difficulty,
                'search_volume': kw.search_volume,
                'competition': kw.competition
            } for kw in result.gap_keywords],
            'recommendations': [
                {
                    'type': rec['type'],
                    'title': rec['title'],
                    'description': rec['description'],
                    'action': rec['action'],
                    'priority': rec['priority'],
                    'keywords': [
                        {
                            'keyword': kw.keyword,
                            'frequency': kw.frequency,
                            'tf_score': kw.tf_score,
                            'idf_score': kw.idf_score,
                            'tfidf_score': kw.tfidf_score,
                            'source': kw.source,
                            'position': kw.position,
                            'context': kw.context,
                            'difficulty': kw.difficulty,
                            'search_volume': kw.search_volume,
                            'competition': kw.competition
                        } for kw in rec.get('keywords', [])
                    ]
                } for rec in result.recommendations
            ],
            'analysis_metadata': result.analysis_metadata
        }
        
        # Save to file
        import os
        results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        filepath = os.path.join(results_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        
        return filepath
