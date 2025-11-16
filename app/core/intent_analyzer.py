"""
Search Intent Analyzer
Detects search intent from content, title, and URL patterns
"""

import re
from typing import Dict, List, Tuple
from .models import SearchIntent


class IntentAnalyzer:
    """Analyzes and detects search intent"""
    
    def __init__(self):
        # Intent signal keywords
        self.intent_signals = {
            SearchIntent.INFORMATIONAL: {
                'keywords': ['چیست', 'چگونه', 'راهنما', 'آموزش', 'نحوه', 'معرفی', 'what', 'how', 'guide', 
                            'tutorial', 'learn', 'معنی', 'تعریف', 'definition', 'مزایا', 'معایب', 'advantages'],
                'url_patterns': [r'/blog/', r'/guide/', r'/learn/', r'/راهنما/', r'/آموزش/'],
                'title_patterns': ['چیست', 'چگونه', 'راهنمای', 'آموزش', 'معرفی'],
                'weight': 1.0
            },
            SearchIntent.TRANSACTIONAL: {
                'keywords': ['خرید', 'قیمت', 'هزینه', 'buy', 'price', 'cost', 'booking', 'رزرو', 'نوبت',
                            'پکیج', 'تخفیف', 'discount', 'offer', 'پیشنهاد', 'سفارش', 'order', 'پرداخت'],
                'url_patterns': [r'/buy/', r'/price/', r'/booking/', r'/خرید/', r'/قیمت/', r'/نوبت/'],
                'title_patterns': ['خرید', 'قیمت', 'هزینه', 'رزرو', 'نوبت'],
                'weight': 1.2
            },
            SearchIntent.LOCAL: {
                'keywords': ['نزدیک', 'محله', 'منطقه', 'تهران', 'شهر', 'آدرس', 'near', 'location', 'address',
                            'شمال', 'جنوب', 'شرق', 'غرب', 'north', 'south', 'east', 'west'],
                'url_patterns': [r'/location/', r'/\w+-tehran/', r'/محله/', r'/منطقه/'],
                'title_patterns': ['تهران', 'شمال', 'جنوب', 'شرق', 'غرب', 'منطقه', 'محله'],
                'weight': 1.3
            },
            SearchIntent.COMPARISON: {
                'keywords': ['مقایسه', 'بهترین', 'برتر', 'compare', 'best', 'vs', 'versus', 'یا', 'or',
                            'تفاوت', 'difference', 'انتخاب', 'choose', 'بهتر', 'better'],
                'url_patterns': [r'/compare/', r'/vs/', r'/مقایسه/', r'/best/'],
                'title_patterns': ['مقایسه', 'بهترین', 'یا', 'vs', 'تفاوت'],
                'weight': 1.1
            },
            SearchIntent.NAVIGATIONAL: {
                'keywords': ['سایت', 'website', 'صفحه اصلی', 'home', 'login', 'ورود', 'dashboard'],
                'url_patterns': [r'^/$', r'/home/?$', r'/index'],
                'title_patterns': ['صفحه اصلی', 'home', 'خانه'],
                'weight': 0.9
            }
        }
        
        # E-commerce/medical specific transactional signals
        self.medical_transactional = ['جراحی', 'عمل', 'درمان', 'لیزر', 'surgery', 'treatment', 'procedure']
    
    def detect_intent(self, title: str, url: str, content: str = "", 
                     h1_tags: List[str] = None) -> Tuple[SearchIntent, float]:
        """
        Detect search intent from page signals
        
        Args:
            title: Page title
            url: Page URL
            content: Page content (first 1000 chars is enough)
            h1_tags: H1 tags
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        if h1_tags is None:
            h1_tags = []
        
        # Initialize scores
        scores = {intent: 0.0 for intent in SearchIntent}
        
        # Combine text sources
        text_to_analyze = f"{title} {url} {content[:1000]} {' '.join(h1_tags)}"
        text_lower = text_to_analyze.lower()
        
        # Score each intent type
        for intent, signals in self.intent_signals.items():
            score = 0.0
            
            # 1. Keyword matching
            keyword_matches = sum(1 for kw in signals['keywords'] if kw in text_lower)
            score += keyword_matches * signals['weight']
            
            # 2. URL pattern matching
            url_matches = sum(1 for pattern in signals['url_patterns'] if re.search(pattern, url, re.IGNORECASE))
            score += url_matches * 2.0 * signals['weight']  # URL is stronger signal
            
            # 3. Title pattern matching
            title_matches = sum(1 for pattern in signals['title_patterns'] if pattern in title.lower())
            score += title_matches * 1.5 * signals['weight']  # Title is important
            
            scores[intent] = score
        
        # Special case: Medical transactional
        if any(keyword in text_lower for keyword in self.medical_transactional):
            scores[SearchIntent.TRANSACTIONAL] += 2.0
        
        # Special case: Local + Transactional combination
        if scores[SearchIntent.LOCAL] > 0 and scores[SearchIntent.TRANSACTIONAL] > 0:
            scores[SearchIntent.LOCAL] += 1.5  # Local intent is often transactional in medical
        
        # Find dominant intent
        if not any(scores.values()):
            return SearchIntent.INFORMATIONAL, 0.5  # Default
        
        max_intent = max(scores.items(), key=lambda x: x[1])
        intent = max_intent[0]
        raw_score = max_intent[1]
        
        # Calculate confidence (0-1)
        total_score = sum(scores.values())
        confidence = min(raw_score / total_score if total_score > 0 else 0.5, 1.0)
        
        # Boost confidence if score is strong
        if raw_score > 3.0:
            confidence = min(confidence + 0.2, 1.0)
        
        return intent, confidence
    
    def detect_intent_from_competitor(self, competitor_data: Dict) -> Tuple[SearchIntent, float]:
        """
        Convenience method to detect intent from competitor data dict
        
        Args:
            competitor_data: Dictionary with url, title, content, h1_tags
            
        Returns:
            Tuple of (intent, confidence)
        """
        title = competitor_data.get('title', '')
        url = competitor_data.get('url', '')
        h1_tags = competitor_data.get('h1_tags', [])
        
        # Get content (from raw analysis if available)
        content = ""
        if 'raw_content' in competitor_data:
            content = competitor_data['raw_content']
        elif 'meta_description' in competitor_data:
            content = competitor_data['meta_description']
        
        return self.detect_intent(title, url, content, h1_tags)
    
    def get_intent_recommendations(self, intent: SearchIntent) -> List[str]:
        """
        Get content recommendations based on intent
        
        Args:
            intent: Detected search intent
            
        Returns:
            List of recommendations
        """
        recommendations = {
            SearchIntent.INFORMATIONAL: [
                "Focus on educational content and explanations",
                "Include 'What', 'How', 'Why' sections",
                "Add FAQ section with detailed answers",
                "Use HowTo or Article schema",
                "Include internal links to related educational content",
                "Add infographics and educational images"
            ],
            SearchIntent.TRANSACTIONAL: [
                "Add clear pricing information",
                "Include prominent CTA (booking/call)",
                "Show before/after results",
                "Add trust signals (certifications, reviews)",
                "Use Service or Product schema",
                "Include location and contact info",
                "Add urgency elements (limited offer, available slots)"
            ],
            SearchIntent.LOCAL: [
                "Highlight location and accessibility",
                "Add Google Maps embed",
                "Use LocalBusiness schema with geo coordinates",
                "Mention landmarks and nearby areas",
                "Add neighborhood-specific information",
                "Include local contact details and hours",
                "Show local reviews and testimonials"
            ],
            SearchIntent.COMPARISON: [
                "Create comparison tables",
                "List pros and cons",
                "Include criteria for choosing",
                "Add expert recommendations",
                "Use FAQ schema for common questions",
                "Be objective and comprehensive"
            ],
            SearchIntent.NAVIGATIONAL: [
                "Ensure clear site structure",
                "Add breadcrumbs",
                "Include main navigation elements",
                "Use WebSite schema with sitelinks"
            ]
        }
        
        return recommendations.get(intent, [])
    
    def detect_mixed_intent(self, title: str, url: str, content: str = "") -> Dict[SearchIntent, float]:
        """
        Detect all intent scores (for pages with mixed intent)
        
        Returns:
            Dictionary of all intents with their scores
        """
        text_to_analyze = f"{title} {url} {content[:1000]}"
        text_lower = text_to_analyze.lower()
        
        scores = {}
        for intent, signals in self.intent_signals.items():
            score = 0.0
            
            keyword_matches = sum(1 for kw in signals['keywords'] if kw in text_lower)
            score += keyword_matches * signals['weight']
            
            url_matches = sum(1 for pattern in signals['url_patterns'] if re.search(pattern, url, re.IGNORECASE))
            score += url_matches * 2.0 * signals['weight']
            
            scores[intent] = score
        
        # Normalize to percentages
        total = sum(scores.values())
        if total > 0:
            scores = {k: round(v / total * 100, 1) for k, v in scores.items()}
        
        return scores


# ==================== Example Usage ====================

if __name__ == "__main__":
    analyzer = IntentAnalyzer()
    
    # Test cases
    test_cases = [
        {
            'title': 'راهنمای کامل لیزر موهای زائد - آموزش',
            'url': 'https://example.com/blog/laser-hair-removal-guide/',
            'expected': SearchIntent.INFORMATIONAL
        },
        {
            'title': 'قیمت لیزر موهای زائد در تهران - رزرو نوبت',
            'url': 'https://example.com/laser-price/',
            'expected': SearchIntent.TRANSACTIONAL
        },
        {
            'title': 'لیزر موهای زائد در سعادت‌آباد تهران',
            'url': 'https://example.com/laser/saadat-abad/',
            'expected': SearchIntent.LOCAL
        },
        {
            'title': 'مقایسه لیزر الکساندرایت و دایود - کدام بهتر است؟',
            'url': 'https://example.com/laser/alexandrite-vs-diode/',
            'expected': SearchIntent.COMPARISON
        }
    ]
    
    print("\n" + "="*70)
    print("🧪 INTENT ANALYZER TEST")
    print("="*70 + "\n")
    
    for i, test in enumerate(test_cases, 1):
        intent, confidence = analyzer.detect_intent(test['title'], test['url'])
        
        status = "✅" if intent == test['expected'] else "❌"
        
        print(f"{status} Test {i}:")
        print(f"   Title: {test['title'][:50]}...")
        print(f"   Detected: {intent.value}")
        print(f"   Confidence: {confidence:.2%}")
        print(f"   Expected: {test['expected'].value}")
        print()
    
    # Show recommendations
    print("\n📋 Recommendations for Transactional Intent:")
    for rec in analyzer.get_intent_recommendations(SearchIntent.TRANSACTIONAL):
        print(f"   • {rec}")


