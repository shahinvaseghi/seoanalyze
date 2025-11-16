"""
Core Web Vitals (CWV) Analyzer
Advanced analysis of page speed, CWV metrics, and performance optimization
Now with Google PageSpeed Insights API integration for real metrics
"""

from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import time
import requests
import os
import json


@dataclass
class CWVMetrics:
    """Core Web Vitals metrics"""
    lcp: Optional[float] = None  # Largest Contentful Paint (seconds)
    inp: Optional[float] = None  # Interaction to Next Paint (ms)
    cls: Optional[float] = None  # Cumulative Layout Shift
    fcp: Optional[float] = None  # First Contentful Paint (seconds)
    ttfb: Optional[float] = None  # Time to First Byte (seconds)
    tti: Optional[float] = None  # Time to Interactive (seconds)


@dataclass
class RenderBlockingResource:
    """Render-blocking resource details"""
    url: str
    type: str  # 'css' or 'js'
    size_kb: Optional[float] = None
    is_external: bool = False
    recommendation: str = ""


@dataclass
class ImageOptimization:
    """Image optimization recommendations"""
    total_images: int
    total_size_kb: float
    images_without_dimensions: int
    images_without_lazy: int
    oversized_images: List[Dict[str, Any]] = field(default_factory=list)
    recommended_formats: Dict[str, str] = field(default_factory=dict)
    recommended_sizes: Dict[str, Dict[str, int]] = field(default_factory=dict)


@dataclass
class CLSAnalysis:
    """CLS (Cumulative Layout Shift) element-level analysis"""
    cls_score: float
    rating: str  # 'good', 'needs-improvement', 'poor'
    potential_causes: List[Dict[str, str]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class CachePolicy:
    """Cache policy analysis"""
    has_cache_control: bool
    cache_duration: Optional[int] = None  # seconds
    static_resources_cached: int = 0
    static_resources_total: int = 0
    recommendations: List[str] = field(default_factory=list)


@dataclass
class FontOptimization:
    """Font optimization analysis"""
    total_fonts: int
    font_files: List[Dict[str, Any]] = field(default_factory=list)
    has_font_display: bool = False
    font_display_value: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)


@dataclass
class CWVReport:
    """Complete Core Web Vitals report"""
    url: str
    timestamp: str
    cwv_metrics: CWVMetrics
    render_blocking: List[RenderBlockingResource]
    image_optimization: ImageOptimization
    cls_analysis: CLSAnalysis
    cache_policy: CachePolicy
    font_optimization: FontOptimization
    overall_score: float
    grade: str
    priority_actions: List[Dict[str, str]]


class CWVAnalyzer:
    """
    Comprehensive Core Web Vitals Analyzer
    Provides element-level performance insights
    Now with Google PageSpeed Insights API integration
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.image_size_recommendations = {
            'hero': {'width': 1600, 'height': 900},
            'gallery': {'width': 800, 'height': 600},
            'thumbnail': {'width': 300, 'height': 300},
            'logo': {'width': 200, 'height': 80}
        }
        
        # Get API key from parameter, environment, or config file
        self.api_key = api_key or self._load_api_key()
        self.use_real_api = bool(self.api_key)
    
    def _load_api_key(self) -> Optional[str]:
        """Load Google PageSpeed API key from environment or config"""
        # Try environment variable first
        api_key = os.environ.get('GOOGLE_PAGESPEED_API_KEY')
        if api_key:
            return api_key
        
        # Try config file
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'configs', 'api_keys.json'
            )
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('google_pagespeed_api_key')
        except Exception as e:
            print(f"⚠️ Could not load API key from config: {e}")
        
        return None
    
    def analyze_cwv(self, soup: BeautifulSoup, url: str, response_time: Optional[float] = None) -> CWVReport:
        """
        Perform comprehensive CWV analysis
        Uses Google PageSpeed Insights API for real metrics if available
        Falls back to static analysis if API is not configured
        """
        import datetime
        
        timestamp = datetime.datetime.now().isoformat()
        
        # 1. Try to get real metrics from Google PageSpeed Insights API
        if self.use_real_api:
            print("📊 Using Google PageSpeed Insights API for real metrics...")
            cwv_metrics = self._get_real_cwv_metrics(url)
            if cwv_metrics:
                print("✅ Real metrics obtained from Google API")
            else:
                print("⚠️ API failed, falling back to static analysis")
                cwv_metrics = self._estimate_cwv_metrics(soup, url, response_time)
        else:
            print("⚠️ No API key configured, using static analysis")
            print("💡 For real metrics, add GOOGLE_PAGESPEED_API_KEY to environment")
            cwv_metrics = self._estimate_cwv_metrics(soup, url, response_time)
        
        # 2. Identify render-blocking resources
        render_blocking = self._identify_render_blocking(soup, url)
        
        # 3. Analyze images
        image_optimization = self._analyze_images(soup)
        
        # 4. Analyze CLS causes
        cls_analysis = self._analyze_cls(soup, cwv_metrics.cls)
        
        # 5. Check cache policy
        cache_policy = self._analyze_cache_policy(url)
        
        # 6. Analyze fonts
        font_optimization = self._analyze_fonts(soup)
        
        # 7. Calculate overall score
        overall_score = self._calculate_performance_score(
            cwv_metrics, render_blocking, image_optimization, cls_analysis
        )
        grade = self._calculate_grade(overall_score)
        
        # 8. Generate priority actions
        priority_actions = self._generate_priority_actions(
            cwv_metrics, render_blocking, image_optimization, 
            cls_analysis, cache_policy, font_optimization
        )
        
        return CWVReport(
            url=url,
            timestamp=timestamp,
            cwv_metrics=cwv_metrics,
            render_blocking=render_blocking,
            image_optimization=image_optimization,
            cls_analysis=cls_analysis,
            cache_policy=cache_policy,
            font_optimization=font_optimization,
            overall_score=overall_score,
            grade=grade,
            priority_actions=priority_actions
        )
    
    def _get_real_cwv_metrics(self, url: str, strategy: str = 'mobile') -> Optional[CWVMetrics]:
        """
        Get real Core Web Vitals metrics from Google PageSpeed Insights API
        
        Args:
            url: Website URL to analyze
            strategy: 'mobile' or 'desktop'
            
        Returns:
            CWVMetrics with real data from Chrome User Experience Report
        """
        if not self.api_key:
            return None
        
        try:
            # Call PageSpeed Insights API
            api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            params = {
                'url': url,
                'key': self.api_key,
                'strategy': strategy,
                'category': ['performance']
            }
            
            print(f"🌐 Calling PageSpeed Insights API for {url}...")
            response = requests.get(api_url, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code}")
                return None
            
            data = response.json()
            
            # Extract field data (real user data from Chrome UX Report)
            loading_experience = data.get('loadingExperience', {})
            metrics = loading_experience.get('metrics', {})
            
            # Extract lab data (Lighthouse) - Always available!
            lighthouse = data.get('lighthouseResult', {})
            audits = lighthouse.get('audits', {})
            
            # Parse LCP - Try Field Data first, fallback to Lab Data
            lcp_ms_field = metrics.get('LARGEST_CONTENTFUL_PAINT_MS', {}).get('percentile')
            if lcp_ms_field:
                lcp = lcp_ms_field / 1000
            else:
                # Fallback to Lab Data (Lighthouse)
                lcp_audit = audits.get('largest-contentful-paint', {})
                lcp_value_lab = lcp_audit.get('numericValue')
                lcp = (lcp_value_lab / 1000) if lcp_value_lab else None
            
            # Parse INP - Try Field Data first, fallback to Lab Data (TBT as proxy)
            inp_field = metrics.get('INTERACTION_TO_NEXT_PAINT', {}).get('percentile')
            if inp_field:
                inp = inp_field
            else:
                # Use Total Blocking Time (TBT) as proxy for INP
                tbt_audit = audits.get('total-blocking-time', {})
                tbt_value = tbt_audit.get('numericValue')
                # TBT to INP conversion (rough estimate)
                inp = int(tbt_value * 0.3) if tbt_value else None
            
            # Parse CLS - Try Field Data first, fallback to Lab Data
            cls_score_field = metrics.get('CUMULATIVE_LAYOUT_SHIFT_SCORE', {}).get('percentile')
            if cls_score_field:
                cls = cls_score_field / 100  # Convert from 0-100 to 0-1
            else:
                # Fallback to Lab Data
                cls_audit = audits.get('cumulative-layout-shift', {})
                cls_value_lab = cls_audit.get('numericValue')
                cls = cls_value_lab if cls_value_lab else None
            
            # Get lab data from Lighthouse (always available)
            fcp_audit = audits.get('first-contentful-paint', {})
            fcp_value = fcp_audit.get('numericValue')  # in milliseconds
            fcp = (fcp_value / 1000) if fcp_value else None
            
            ttfb_audit = audits.get('server-response-time', {})
            ttfb_value = ttfb_audit.get('numericValue')  # in milliseconds
            ttfb = (ttfb_value / 1000) if ttfb_value else None
            
            tti_audit = audits.get('interactive', {})
            tti_value = tti_audit.get('numericValue')  # in milliseconds
            tti = (tti_value / 1000) if tti_value else None
            
            print(f"✅ Metrics retrieved:")
            print(f"   LCP: {lcp}s" if lcp else "   LCP: N/A")
            print(f"   INP: {inp}ms" if inp else "   INP: N/A")
            print(f"   CLS: {cls}" if cls is not None else "   CLS: N/A")
            print(f"   FCP: {fcp}s" if fcp else "   FCP: N/A")
            print(f"   TTFB: {ttfb}s" if ttfb else "   TTFB: N/A")
            print(f"   TTI: {tti}s" if tti else "   TTI: N/A")
            
            return CWVMetrics(
                lcp=round(lcp, 2) if lcp else None,
                inp=int(inp) if inp else None,
                cls=round(cls, 3) if cls else None,
                fcp=round(fcp, 2) if fcp else None,
                ttfb=round(ttfb, 3) if ttfb else None,
                tti=round(tti, 2) if tti else None
            )
            
        except Exception as e:
            print(f"❌ Error calling PageSpeed Insights API: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _estimate_cwv_metrics(self, soup: BeautifulSoup, url: str, response_time: Optional[float]) -> CWVMetrics:
        """
        Estimate CWV metrics based on static analysis
        For accurate metrics, use Lighthouse API or WebPageTest
        """
        # TTFB from response time
        ttfb = response_time if response_time else None
        
        # Estimate FCP based on render-blocking resources
        render_blocking_count = len(soup.find_all('link', rel='stylesheet')) + len(soup.find_all('script', src=True))
        estimated_fcp = (ttfb or 0.5) + (render_blocking_count * 0.1)
        
        # Estimate LCP based on largest image or text block
        images = soup.find_all('img')
        # Rough estimate: LCP happens around FCP + image load time
        estimated_lcp = estimated_fcp + 0.5
        
        # CLS estimation based on images without dimensions
        images_without_dimensions = sum(1 for img in images if not (img.get('width') and img.get('height')))
        estimated_cls = min(0.25, images_without_dimensions * 0.05)
        
        # INP is hard to estimate without interaction data
        estimated_inp = None
        
        # TTI estimation
        scripts_count = len(soup.find_all('script'))
        estimated_tti = estimated_fcp + (scripts_count * 0.05)
        
        return CWVMetrics(
            lcp=round(estimated_lcp, 2),
            inp=estimated_inp,
            cls=round(estimated_cls, 3),
            fcp=round(estimated_fcp, 2),
            ttfb=round(ttfb, 3) if ttfb else None,
            tti=round(estimated_tti, 2)
        )
    
    def _identify_render_blocking(self, soup: BeautifulSoup, base_url: str) -> List[RenderBlockingResource]:
        """Identify render-blocking CSS and JavaScript"""
        blocking_resources = []
        
        # Check CSS files
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if not href:
                continue
            
            is_external = href.startswith('http')
            
            # Check if it has async/defer or media attribute
            media = link.get('media', 'all')
            is_blocking = media == 'all' or media == 'screen'
            
            if is_blocking:
                blocking_resources.append(RenderBlockingResource(
                    url=href,
                    type='css',
                    is_external=is_external,
                    recommendation="Consider critical CSS inline or preload with media query"
                ))
        
        # Check JavaScript files
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if not src:
                continue
            
            is_external = src.startswith('http')
            has_async = script.get('async') is not None
            has_defer = script.get('defer') is not None
            
            if not has_async and not has_defer:
                blocking_resources.append(RenderBlockingResource(
                    url=src,
                    type='js',
                    is_external=is_external,
                    recommendation="Add async or defer attribute to non-critical scripts"
                ))
        
        return blocking_resources
    
    def _analyze_images(self, soup: BeautifulSoup) -> ImageOptimization:
        """Comprehensive image analysis"""
        images = soup.find_all('img')
        total_images = len(images)
        
        images_without_dimensions = 0
        images_without_lazy = 0
        oversized_images = []
        recommended_formats = {}
        
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            # Check dimensions
            width = img.get('width')
            height = img.get('height')
            
            if not (width and height):
                images_without_dimensions += 1
            
            # Check lazy loading
            loading = img.get('loading')
            if loading != 'lazy':
                images_without_lazy += 1
            
            # Check file format
            if src:
                if src.endswith(('.jpg', '.jpeg', '.png')):
                    recommended_formats[src] = 'WebP'
                
                # Detect potentially oversized images
                # (This is a heuristic - actual size would need HTTP request)
                if 'hero' in src.lower() or 'banner' in src.lower():
                    oversized_images.append({
                        'src': src,
                        'reason': 'Hero image - ensure it\'s optimized',
                        'recommended_size': '1600x900, WebP format'
                    })
        
        # Estimate total size (very rough)
        estimated_total_size = total_images * 150  # Assume 150KB per image
        
        # Recommended sizes per slot type
        recommended_sizes = self.image_size_recommendations.copy()
        
        return ImageOptimization(
            total_images=total_images,
            total_size_kb=estimated_total_size,
            images_without_dimensions=images_without_dimensions,
            images_without_lazy=images_without_lazy,
            oversized_images=oversized_images,
            recommended_formats=recommended_formats,
            recommended_sizes=recommended_sizes
        )
    
    def _analyze_cls(self, soup: BeautifulSoup, estimated_cls: Optional[float]) -> CLSAnalysis:
        """Analyze potential CLS (Cumulative Layout Shift) causes"""
        cls_score = estimated_cls if estimated_cls is not None else 0.1
        
        # Rating based on Web Vitals thresholds
        if cls_score < 0.1:
            rating = 'good'
        elif cls_score < 0.25:
            rating = 'needs-improvement'
        else:
            rating = 'poor'
        
        potential_causes = []
        recommendations = []
        
        # 1. Images without dimensions
        images_without_dims = soup.find_all('img')
        images_without_dims = [img for img in images_without_dims if not (img.get('width') and img.get('height'))]
        
        if images_without_dims:
            potential_causes.append({
                'element': 'Images',
                'count': str(len(images_without_dims)),
                'issue': 'Missing width/height attributes'
            })
            recommendations.append(f"Add width and height attributes to {len(images_without_dims)} images")
        
        # 2. Web fonts without font-display
        font_links = soup.find_all('link', href=lambda h: h and 'font' in h)
        if font_links:
            potential_causes.append({
                'element': 'Web Fonts',
                'count': str(len(font_links)),
                'issue': 'May cause text shifting'
            })
            recommendations.append("Use font-display: swap or optional in @font-face")
        
        # 3. Ads/embeds without fixed containers
        iframes = soup.find_all('iframe')
        iframes_without_dims = [iframe for iframe in iframes if not (iframe.get('width') and iframe.get('height'))]
        
        if iframes_without_dims:
            potential_causes.append({
                'element': 'Iframes/Embeds',
                'count': str(len(iframes_without_dims)),
                'issue': 'Missing dimensions'
            })
            recommendations.append(f"Reserve space for {len(iframes_without_dims)} iframes with fixed dimensions")
        
        # 4. Dynamic content injection
        scripts_count = len(soup.find_all('script'))
        if scripts_count > 10:
            potential_causes.append({
                'element': 'JavaScript',
                'count': str(scripts_count),
                'issue': 'Many scripts may inject content dynamically'
            })
            recommendations.append("Review scripts for dynamic content injection that causes layout shifts")
        
        if not potential_causes:
            recommendations.append("✅ No obvious CLS issues detected")
        
        return CLSAnalysis(
            cls_score=cls_score,
            rating=rating,
            potential_causes=potential_causes,
            recommendations=recommendations
        )
    
    def _analyze_cache_policy(self, url: str) -> CachePolicy:
        """Analyze caching policy (requires HTTP headers)"""
        # This is a simplified analysis
        # In production, you'd check actual Cache-Control headers
        
        recommendations = []
        has_cache_control = False
        cache_duration = None
        
        try:
            response = requests.head(url, timeout=5)
            cache_control = response.headers.get('Cache-Control', '')
            
            if cache_control:
                has_cache_control = True
                # Parse max-age
                if 'max-age=' in cache_control:
                    import re
                    match = re.search(r'max-age=(\d+)', cache_control)
                    if match:
                        cache_duration = int(match.group(1))
            
            if not has_cache_control:
                recommendations.append("Add Cache-Control headers for static resources")
            elif cache_duration and cache_duration < 86400:  # Less than 1 day
                recommendations.append(f"Increase cache duration (current: {cache_duration}s, recommended: 31536000s for static assets)")
            else:
                recommendations.append("✅ Cache policy looks good")
                
        except Exception as e:
            recommendations.append(f"Could not check cache policy: {str(e)}")
        
        return CachePolicy(
            has_cache_control=has_cache_control,
            cache_duration=cache_duration,
            static_resources_cached=0,  # Would need to check each resource
            static_resources_total=0,
            recommendations=recommendations
        )
    
    def _analyze_fonts(self, soup: BeautifulSoup) -> FontOptimization:
        """Analyze web font usage and optimization"""
        font_files = []
        
        # Check for @font-face in style tags
        style_tags = soup.find_all('style')
        has_font_display = False
        font_display_value = None
        
        for style in style_tags:
            content = style.string
            if content and '@font-face' in content:
                # Check for font-display
                if 'font-display:' in content:
                    has_font_display = True
                    import re
                    match = re.search(r'font-display:\s*(\w+)', content)
                    if match:
                        font_display_value = match.group(1)
        
        # Check for external font links
        font_links = soup.find_all('link', href=lambda h: h and ('font' in h or 'googleapis' in h))
        
        for link in font_links:
            href = link.get('href', '')
            font_files.append({
                'url': href,
                'type': 'external',
                'preload': link.get('rel') == 'preload'
            })
        
        total_fonts = len(font_files)
        
        recommendations = []
        
        if total_fonts == 0:
            recommendations.append("✅ Using system fonts (good for performance)")
        else:
            if not has_font_display:
                recommendations.append("Add font-display: swap to @font-face rules")
            
            if total_fonts > 3:
                recommendations.append(f"Using {total_fonts} font files. Consider reducing to 2-3 for better performance")
            
            # Check for preload
            preloaded = sum(1 for f in font_files if f.get('preload'))
            if preloaded == 0 and total_fonts > 0:
                recommendations.append("Preload critical fonts with <link rel=\"preload\">")
        
        if not recommendations:
            recommendations.append("✅ Font optimization looks good")
        
        return FontOptimization(
            total_fonts=total_fonts,
            font_files=font_files,
            has_font_display=has_font_display,
            font_display_value=font_display_value,
            recommendations=recommendations
        )
    
    def _calculate_performance_score(self, cwv: CWVMetrics, render_blocking: List,
                                    images: ImageOptimization, cls: CLSAnalysis) -> float:
        """Calculate overall performance score"""
        score = 100
        
        # LCP penalty
        if cwv.lcp:
            if cwv.lcp > 4.0:
                score -= 30
            elif cwv.lcp > 2.5:
                score -= 15
        
        # CLS penalty
        if cwv.cls:
            if cwv.cls > 0.25:
                score -= 25
            elif cwv.cls > 0.1:
                score -= 10
        
        # FCP penalty
        if cwv.fcp:
            if cwv.fcp > 3.0:
                score -= 20
            elif cwv.fcp > 1.8:
                score -= 10
        
        # Render-blocking penalty
        if len(render_blocking) > 5:
            score -= 15
        elif len(render_blocking) > 0:
            score -= 5
        
        # Image optimization penalty
        if images.images_without_dimensions > 0:
            score -= min(10, images.images_without_dimensions * 2)
        
        if images.images_without_lazy > 3:
            score -= 5
        
        return max(0, min(100, score))
    
    def _calculate_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        else:
            return 'D'
    
    def _generate_priority_actions(self, cwv: CWVMetrics, render_blocking: List,
                                   images: ImageOptimization, cls: CLSAnalysis,
                                   cache: CachePolicy, fonts: FontOptimization) -> List[Dict[str, str]]:
        """Generate prioritized performance actions"""
        actions = []
        
        # CWV priorities
        if cwv.lcp and cwv.lcp > 2.5:
            actions.append({
                'priority': 'CRITICAL',
                'category': 'LCP',
                'action': f'Optimize LCP (current: {cwv.lcp}s, target: <2.5s)',
                'details': 'Optimize largest image/text block, reduce server response time'
            })
        
        if cwv.cls and cwv.cls > 0.1:
            priority = 'CRITICAL' if cwv.cls > 0.25 else 'HIGH'
            actions.append({
                'priority': priority,
                'category': 'CLS',
                'action': f'Fix layout shifts (current: {cwv.cls}, target: <0.1)',
                'details': '; '.join(cls.recommendations[:2]) if cls.recommendations else 'Add dimensions to images and iframes'
            })
        
        if cwv.fcp and cwv.fcp > 1.8:
            actions.append({
                'priority': 'HIGH',
                'category': 'FCP',
                'action': f'Improve First Contentful Paint (current: {cwv.fcp}s)',
                'details': 'Reduce render-blocking resources, optimize server response'
            })
        
        # Render-blocking resources
        if len(render_blocking) > 0:
            css_count = sum(1 for r in render_blocking if r.type == 'css')
            js_count = sum(1 for r in render_blocking if r.type == 'js')
            
            if css_count > 0:
                actions.append({
                    'priority': 'HIGH',
                    'category': 'Render-Blocking CSS',
                    'action': f'Eliminate {css_count} render-blocking CSS file(s)',
                    'details': 'Inline critical CSS, defer non-critical CSS'
                })
            
            if js_count > 0:
                actions.append({
                    'priority': 'HIGH',
                    'category': 'Render-Blocking JS',
                    'action': f'Defer {js_count} JavaScript file(s)',
                    'details': 'Add async or defer attributes'
                })
        
        # Image optimization
        if images.images_without_dimensions > 0:
            actions.append({
                'priority': 'HIGH',
                'category': 'Images',
                'action': f'Add dimensions to {images.images_without_dimensions} images',
                'details': 'Prevents layout shifts (CLS)'
            })
        
        if images.images_without_lazy > 3:
            actions.append({
                'priority': 'MEDIUM',
                'category': 'Images',
                'action': f'Add lazy loading to {images.images_without_lazy} images',
                'details': 'Use loading="lazy" attribute'
            })
        
        if len(images.recommended_formats) > 0:
            actions.append({
                'priority': 'MEDIUM',
                'category': 'Images',
                'action': f'Convert {len(images.recommended_formats)} images to WebP',
                'details': 'Reduce image file sizes by 25-35%'
            })
        
        # Cache policy
        if not cache.has_cache_control:
            actions.append({
                'priority': 'MEDIUM',
                'category': 'Caching',
                'action': 'Implement cache-control headers',
                'details': 'Cache-Control: public, max-age=31536000 for static assets'
            })
        
        # Font optimization
        if fonts.total_fonts > 0 and not fonts.has_font_display:
            actions.append({
                'priority': 'MEDIUM',
                'category': 'Fonts',
                'action': 'Add font-display: swap to web fonts',
                'details': 'Prevents invisible text during font load'
            })
        
        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        actions.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        return actions
    
    def export_report_json(self, report: CWVReport, filename: str):
        """Export CWV report to JSON"""
        import json
        from dataclasses import asdict
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, ensure_ascii=False, indent=2)
        
        print(f"✅ CWV report exported to {filename}")

