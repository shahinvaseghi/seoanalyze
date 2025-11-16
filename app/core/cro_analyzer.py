"""
CRO (Conversion Rate Optimization) Analyzer
Analyzes CTA placement, UX elements, accessibility, and conversion optimization
"""

from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import re
from dataclasses import dataclass, field


@dataclass
class CTAAnalysis:
    """CTA (Call-to-Action) analysis results"""
    total_ctas: int
    cta_types: Dict[str, int]
    cta_locations: List[Dict[str, Any]]
    above_fold_ctas: int
    optimal_placement: Dict[str, Any]
    recommendations: List[str]


@dataclass
class FormAnalysis:
    """Form analysis results"""
    total_forms: int
    forms: List[Dict[str, Any]]
    avg_fields: float
    recommendations: List[str]


@dataclass
class TrustSignals:
    """Trust signals on the page"""
    has_phone: bool
    has_address: bool
    has_email: bool
    has_social_proof: bool
    has_credentials: bool
    has_certifications: bool
    has_reviews: bool
    has_testimonials: bool
    has_secure_badges: bool
    trust_score: float
    elements: List[Dict[str, str]]


@dataclass
class AccessibilityCheck:
    """Accessibility checklist results"""
    score: int  # 0-100
    grade: str
    passed: List[str]
    failed: List[str]
    warnings: List[str]
    aria_issues: List[str]
    color_contrast_issues: List[str]
    keyboard_navigation_issues: List[str]


@dataclass
class CROReport:
    """Complete CRO analysis report"""
    url: str
    cta_analysis: CTAAnalysis
    form_analysis: FormAnalysis
    trust_signals: TrustSignals
    accessibility: AccessibilityCheck
    overall_cro_score: float
    grade: str
    priority_actions: List[Dict[str, str]]


class CROAnalyzer:
    """
    Comprehensive CRO (Conversion Rate Optimization) Analyzer
    """
    
    def __init__(self):
        self.cta_keywords_fa = [
            'رزرو', 'ثبت نام', 'تماس', 'مشاوره', 'خرید', 'سفارش',
            'دریافت', 'دانلود', 'شروع', 'همین حالا', 'کلیک'
        ]
        
        self.cta_keywords_en = [
            'book', 'sign up', 'contact', 'call', 'buy', 'order',
            'get', 'download', 'start', 'now', 'click', 'submit',
            'register', 'reserve', 'schedule', 'consult'
        ]
        
        self.trust_keywords = {
            'phone': ['تلفن', 'موبایل', 'phone', 'mobile', 'tel:'],
            'email': ['ایمیل', 'email', 'mailto:', '@'],
            'address': ['آدرس', 'نشانی', 'address', 'location'],
            'credentials': ['دکتر', 'مهندس', 'استاد', 'dr.', 'phd', 'md'],
            'certifications': ['گواهینامه', 'مجوز', 'certificate', 'license', 'نماد'],
            'reviews': ['نظر', 'امتیاز', 'review', 'rating', 'stars'],
            'testimonials': ['تجربه', 'نظرات', 'testimonial', 'feedback'],
            'secure': ['ssl', 'secure', 'امن', 'https']
        }
    
    def analyze_cro(self, soup: BeautifulSoup, url: str, viewport_height: int = 800) -> CROReport:
        """
        Perform complete CRO analysis
        """
        # 1. CTA Analysis
        cta_analysis = self._analyze_ctas(soup, viewport_height)
        
        # 2. Form Analysis
        form_analysis = self._analyze_forms(soup)
        
        # 3. Trust Signals
        trust_signals = self._analyze_trust_signals(soup)
        
        # 4. Accessibility Check
        accessibility = self._check_accessibility(soup)
        
        # 5. Calculate overall CRO score
        overall_score = self._calculate_cro_score(
            cta_analysis, form_analysis, trust_signals, accessibility
        )
        grade = self._calculate_grade(overall_score)
        
        # 6. Generate priority actions
        priority_actions = self._generate_priority_actions(
            cta_analysis, form_analysis, trust_signals, accessibility
        )
        
        return CROReport(
            url=url,
            cta_analysis=cta_analysis,
            form_analysis=form_analysis,
            trust_signals=trust_signals,
            accessibility=accessibility,
            overall_cro_score=overall_score,
            grade=grade,
            priority_actions=priority_actions
        )
    
    def _analyze_ctas(self, soup: BeautifulSoup, viewport_height: int) -> CTAAnalysis:
        """Analyze all CTAs on the page"""
        ctas = []
        cta_types = {}
        
        # Find all buttons and links that look like CTAs
        for element in soup.find_all(['button', 'a', 'input']):
            text = element.get_text(strip=True).lower()
            
            # Check if it's a CTA
            is_cta = False
            cta_type = 'generic'
            
            # Persian keywords
            for keyword in self.cta_keywords_fa:
                if keyword in text:
                    is_cta = True
                    cta_type = self._classify_cta_type(keyword)
                    break
            
            # English keywords
            if not is_cta:
                for keyword in self.cta_keywords_en:
                    if keyword in text:
                        is_cta = True
                        cta_type = self._classify_cta_type(keyword)
                        break
            
            # Check button/input type
            if not is_cta:
                if element.name == 'button' or (element.name == 'input' and element.get('type') == 'submit'):
                    is_cta = True
                    cta_type = 'form_submit'
            
            if is_cta:
                # Try to estimate position (very rough - would need rendering engine for accuracy)
                position = self._estimate_element_position(element, soup)
                
                cta_info = {
                    'text': element.get_text(strip=True)[:50],
                    'type': cta_type,
                    'tag': element.name,
                    'position': position,
                    'href': element.get('href', ''),
                    'classes': ' '.join(element.get('class', [])),
                    'is_above_fold': position.get('estimated_top', 999) < viewport_height
                }
                
                ctas.append(cta_info)
                cta_types[cta_type] = cta_types.get(cta_type, 0) + 1
        
        # Count above-fold CTAs
        above_fold_ctas = sum(1 for cta in ctas if cta['is_above_fold'])
        
        # Optimal placement recommendations
        optimal_placement = self._recommend_cta_placement(ctas, soup)
        
        # Recommendations
        recommendations = []
        if len(ctas) == 0:
            recommendations.append("🚨 CRITICAL: No CTAs found! Add clear call-to-action buttons.")
        elif len(ctas) < 2:
            recommendations.append("⚠️ Only one CTA found. Consider adding more CTAs throughout the page.")
        
        if above_fold_ctas == 0:
            recommendations.append("🚨 CRITICAL: No CTAs above the fold! Add a visible CTA in the hero section.")
        
        if cta_types.get('phone', 0) == 0 and cta_types.get('whatsapp', 0) == 0:
            recommendations.append("💡 Add a phone/WhatsApp CTA for immediate contact.")
        
        if len(ctas) > 10:
            recommendations.append("⚠️ Too many CTAs ({len(ctas)}) may dilute focus. Prioritize 3-5 key actions.")
        
        return CTAAnalysis(
            total_ctas=len(ctas),
            cta_types=cta_types,
            cta_locations=ctas,
            above_fold_ctas=above_fold_ctas,
            optimal_placement=optimal_placement,
            recommendations=recommendations
        )
    
    def _classify_cta_type(self, keyword: str) -> str:
        """Classify CTA type based on keyword"""
        keyword_lower = keyword.lower()
        
        if keyword_lower in ['رزرو', 'book', 'reserve', 'schedule']:
            return 'booking'
        elif keyword_lower in ['تماس', 'call', 'contact', 'phone']:
            return 'phone'
        elif keyword_lower in ['مشاوره', 'consult']:
            return 'consultation'
        elif keyword_lower in ['خرید', 'buy', 'order', 'سفارش']:
            return 'purchase'
        elif keyword_lower in ['ثبت نام', 'sign up', 'register']:
            return 'signup'
        elif keyword_lower in ['دانلود', 'download', 'get']:
            return 'download'
        else:
            return 'generic'
    
    def _estimate_element_position(self, element, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Estimate element position (rough approximation)
        In production, use Selenium/Playwright for accurate positioning
        """
        # Count preceding elements as a rough estimate
        all_elements = list(soup.find_all(['div', 'section', 'article', 'header', 'main']))
        
        try:
            index = all_elements.index(element.find_parent(['div', 'section', 'article', 'header', 'main']))
        except (ValueError, AttributeError):
            index = 0
        
        # Very rough estimate: each element ~100px
        estimated_top = index * 100
        
        # Check if in header
        is_in_header = element.find_parent('header') is not None
        
        return {
            'estimated_top': estimated_top if not is_in_header else 50,
            'is_in_header': is_in_header,
            'parent_tag': element.parent.name if element.parent else 'unknown'
        }
    
    def _recommend_cta_placement(self, ctas: List[Dict[str, Any]], soup: BeautifulSoup) -> Dict[str, Any]:
        """Recommend optimal CTA placements"""
        h2_tags = soup.find_all('h2')
        
        recommendations = {
            'hero_section': {
                'recommended': True,
                'current': any(cta['is_above_fold'] for cta in ctas),
                'suggestion': 'Add primary CTA in hero section (above fold)',
                'type': 'booking or consultation'
            },
            'after_h2_2': {
                'recommended': True,
                'current': False,  # Would need more sophisticated detection
                'suggestion': 'Add CTA after 2nd H2 section',
                'type': 'form or phone'
            },
            'sidebar': {
                'recommended': True,
                'current': False,  # Would need layout detection
                'suggestion': 'Add sticky sidebar CTA for high-intent users',
                'type': 'phone or WhatsApp'
            },
            'end_of_content': {
                'recommended': True,
                'current': False,
                'suggestion': 'Add final CTA before footer',
                'type': 'comprehensive form'
            }
        }
        
        return recommendations
    
    def _analyze_forms(self, soup: BeautifulSoup) -> FormAnalysis:
        """Analyze all forms on the page"""
        forms = []
        
        for form in soup.find_all('form'):
            # Count input fields
            inputs = form.find_all(['input', 'textarea', 'select'])
            visible_inputs = [
                inp for inp in inputs 
                if inp.get('type') not in ['hidden', 'submit', 'button']
            ]
            
            # Get form action and method
            action = form.get('action', '')
            method = form.get('method', 'get').upper()
            
            # Check for validation
            has_validation = any(
                inp.get('required') or inp.get('pattern') 
                for inp in inputs
            )
            
            # Field types
            field_types = {}
            for inp in visible_inputs:
                field_type = inp.get('type', 'text') if inp.name == 'input' else inp.name
                field_types[field_type] = field_types.get(field_type, 0) + 1
            
            forms.append({
                'total_fields': len(visible_inputs),
                'field_types': field_types,
                'action': action,
                'method': method,
                'has_validation': has_validation,
                'has_submit_button': form.find(['button', 'input'], type='submit') is not None
            })
        
        # Calculate average fields
        avg_fields = sum(f['total_fields'] for f in forms) / len(forms) if forms else 0
        
        # Recommendations
        recommendations = []
        if len(forms) == 0:
            recommendations.append("💡 Consider adding a contact form to capture leads.")
        
        for form in forms:
            if form['total_fields'] > 7:
                recommendations.append(f"⚠️ Form has {form['total_fields']} fields. Consider reducing to 3-5 for better conversion.")
            
            if not form['has_submit_button']:
                recommendations.append("🚨 Form missing submit button!")
            
            if form['method'] == 'GET' and 'contact' in form.get('action', '').lower():
                recommendations.append("⚠️ Contact form using GET method. Use POST for better security.")
        
        if avg_fields > 5:
            recommendations.append(f"💡 Average form length ({avg_fields:.1f} fields) is high. Aim for 3-4 fields for lead gen forms.")
        
        return FormAnalysis(
            total_forms=len(forms),
            forms=forms,
            avg_fields=round(avg_fields, 1),
            recommendations=recommendations
        )
    
    def _analyze_trust_signals(self, soup: BeautifulSoup) -> TrustSignals:
        """Analyze trust signals on the page"""
        page_text = soup.get_text().lower()
        page_html = str(soup).lower()
        
        elements = []
        
        # Check for phone
        has_phone = any(kw in page_text for kw in self.trust_keywords['phone'])
        if has_phone:
            elements.append({'type': 'phone', 'description': 'Phone number found'})
        
        # Check for email
        has_email = any(kw in page_html for kw in self.trust_keywords['email'])
        if has_email:
            elements.append({'type': 'email', 'description': 'Email contact found'})
        
        # Check for address
        has_address = any(kw in page_text for kw in self.trust_keywords['address'])
        if has_address:
            elements.append({'type': 'address', 'description': 'Physical address found'})
        
        # Check for social proof (reviews, ratings)
        has_reviews = any(kw in page_text for kw in self.trust_keywords['reviews'])
        if has_reviews:
            elements.append({'type': 'reviews', 'description': 'Reviews/ratings found'})
        
        # Check for testimonials
        has_testimonials = any(kw in page_text for kw in self.trust_keywords['testimonials'])
        if has_testimonials:
            elements.append({'type': 'testimonials', 'description': 'Testimonials found'})
        
        # Check for credentials
        has_credentials = any(kw in page_text for kw in self.trust_keywords['credentials'])
        if has_credentials:
            elements.append({'type': 'credentials', 'description': 'Professional credentials found'})
        
        # Check for certifications
        has_certifications = any(kw in page_text for kw in self.trust_keywords['certifications'])
        if has_certifications:
            elements.append({'type': 'certifications', 'description': 'Certifications/badges found'})
        
        # Check for secure badges
        has_secure_badges = any(kw in page_html for kw in self.trust_keywords['secure'])
        if has_secure_badges:
            elements.append({'type': 'secure', 'description': 'Security badges found'})
        
        # Check for social proof indicators
        has_social_proof = has_reviews or has_testimonials
        
        # Calculate trust score
        trust_factors = [
            has_phone, has_email, has_address, has_social_proof,
            has_credentials, has_certifications, has_secure_badges
        ]
        trust_score = (sum(trust_factors) / len(trust_factors)) * 100
        
        return TrustSignals(
            has_phone=has_phone,
            has_address=has_address,
            has_email=has_email,
            has_social_proof=has_social_proof,
            has_credentials=has_credentials,
            has_certifications=has_certifications,
            has_reviews=has_reviews,
            has_testimonials=has_testimonials,
            has_secure_badges=has_secure_badges,
            trust_score=round(trust_score, 1),
            elements=elements
        )
    
    def _check_accessibility(self, soup: BeautifulSoup) -> AccessibilityCheck:
        """Comprehensive accessibility check"""
        passed = []
        failed = []
        warnings = []
        aria_issues = []
        color_contrast_issues = []
        keyboard_nav_issues = []
        
        # 1. Check images for alt text
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        
        if len(images_without_alt) == 0 and len(images) > 0:
            passed.append("✅ All images have alt text")
        elif len(images_without_alt) > 0:
            failed.append(f"❌ {len(images_without_alt)}/{len(images)} images missing alt text")
        
        # 2. Check for proper heading hierarchy
        h1_count = len(soup.find_all('h1'))
        if h1_count == 1:
            passed.append("✅ Single H1 tag (good structure)")
        elif h1_count == 0:
            failed.append("❌ No H1 tag found")
        elif h1_count > 1:
            warnings.append(f"⚠️ Multiple H1 tags ({h1_count}) - consider using only one")
        
        # 3. Check for ARIA labels
        interactive_elements = soup.find_all(['button', 'a', 'input'])
        elements_without_label = []
        
        for elem in interactive_elements:
            has_label = (
                elem.get('aria-label') or 
                elem.get('aria-labelledby') or 
                elem.get('title') or
                elem.get_text(strip=True)
            )
            if not has_label:
                elements_without_label.append(elem.name)
        
        if len(elements_without_label) == 0:
            passed.append("✅ All interactive elements have labels")
        else:
            aria_issues.append(f"⚠️ {len(elements_without_label)} interactive elements without labels")
        
        # 4. Check for form labels
        forms = soup.find_all('form')
        for form in forms:
            inputs = form.find_all(['input', 'textarea', 'select'])
            for inp in inputs:
                if inp.get('type') not in ['hidden', 'submit', 'button']:
                    # Check if input has associated label
                    inp_id = inp.get('id')
                    has_label = False
                    
                    if inp_id:
                        has_label = soup.find('label', {'for': inp_id}) is not None
                    
                    if not has_label and not inp.get('aria-label'):
                        aria_issues.append(f"⚠️ Input field without label: {inp.get('name', 'unnamed')}")
        
        # 5. Check for focus indicators (basic check)
        # This would require CSS analysis in production
        if soup.find('style') or soup.find('link', rel='stylesheet'):
            passed.append("✅ Stylesheet present (check for :focus styles manually)")
        else:
            warnings.append("⚠️ No stylesheet found - ensure focus indicators are defined")
        
        # 6. Check for lang attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            passed.append(f"✅ Language attribute set: {html_tag.get('lang')}")
        else:
            failed.append("❌ Missing lang attribute on <html> tag")
        
        # 7. Check for skip links
        skip_link = soup.find('a', href='#main-content') or soup.find('a', href='#content')
        if skip_link:
            passed.append("✅ Skip navigation link found")
        else:
            warnings.append("💡 Consider adding a 'skip to main content' link")
        
        # 8. Check for semantic HTML5 elements
        semantic_elements = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']
        found_semantic = [elem for elem in semantic_elements if soup.find(elem)]
        
        if len(found_semantic) >= 4:
            passed.append(f"✅ Good use of semantic HTML5 ({len(found_semantic)}/7 elements)")
        else:
            warnings.append(f"⚠️ Limited semantic HTML5 ({len(found_semantic)}/7 elements)")
        
        # 9. Check for color contrast (very basic - would need CSS analysis)
        # Just check if there's inline styling with colors
        elements_with_colors = soup.find_all(style=re.compile(r'color:\s*#'))
        if elements_with_colors:
            color_contrast_issues.append("⚠️ Manual check needed: Verify color contrast ratios (WCAG AA: 4.5:1)")
        
        # 10. Check for keyboard navigation
        buttons_with_tabindex = soup.find_all(['button', 'a'], tabindex='-1')
        if buttons_with_tabindex:
            keyboard_nav_issues.append(f"⚠️ {len(buttons_with_tabindex)} elements with tabindex=-1 (not keyboard accessible)")
        
        # Calculate accessibility score
        total_checks = len(passed) + len(failed) + len(warnings)
        score = int((len(passed) / total_checks * 100)) if total_checks > 0 else 50
        
        # Deduct for critical issues
        if aria_issues:
            score -= min(len(aria_issues) * 5, 20)
        if keyboard_nav_issues:
            score -= min(len(keyboard_nav_issues) * 5, 15)
        
        score = max(0, min(100, score))
        grade = self._calculate_grade(score)
        
        return AccessibilityCheck(
            score=score,
            grade=grade,
            passed=passed,
            failed=failed,
            warnings=warnings,
            aria_issues=aria_issues if aria_issues else ["✅ No ARIA issues detected"],
            color_contrast_issues=color_contrast_issues if color_contrast_issues else ["✅ No obvious contrast issues"],
            keyboard_navigation_issues=keyboard_nav_issues if keyboard_nav_issues else ["✅ No keyboard nav issues detected"]
        )
    
    def _calculate_cro_score(self, cta: CTAAnalysis, forms: FormAnalysis, 
                            trust: TrustSignals, accessibility: AccessibilityCheck) -> float:
        """Calculate overall CRO score"""
        # Weighted scoring
        cta_score = min(100, (cta.above_fold_ctas * 30) + (cta.total_ctas * 10))
        cta_score = min(100, cta_score)
        
        form_score = 100 if forms.total_forms > 0 else 50
        if forms.total_forms > 0 and forms.avg_fields <= 5:
            form_score = 100
        elif forms.avg_fields > 5:
            form_score = max(70, 100 - (forms.avg_fields - 5) * 5)
        
        trust_score = trust.trust_score
        accessibility_score = accessibility.score
        
        # Weighted average
        overall = (
            cta_score * 0.35 +
            form_score * 0.20 +
            trust_score * 0.25 +
            accessibility_score * 0.20
        )
        
        return round(overall, 1)
    
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
    
    def _generate_priority_actions(self, cta: CTAAnalysis, forms: FormAnalysis,
                                   trust: TrustSignals, accessibility: AccessibilityCheck) -> List[Dict[str, str]]:
        """Generate prioritized action items"""
        actions = []
        
        # CTA priorities
        if cta.above_fold_ctas == 0:
            actions.append({
                'priority': 'CRITICAL',
                'category': 'CTA',
                'action': 'Add a clear CTA above the fold',
                'impact': 'High conversion impact'
            })
        
        if cta.total_ctas < 2:
            actions.append({
                'priority': 'HIGH',
                'category': 'CTA',
                'action': 'Add CTAs throughout the page (after key sections)',
                'impact': 'Increase conversion opportunities'
            })
        
        # Form priorities
        if forms.total_forms == 0:
            actions.append({
                'priority': 'HIGH',
                'category': 'Forms',
                'action': 'Add a lead capture form',
                'impact': 'Enable lead generation'
            })
        elif forms.avg_fields > 5:
            actions.append({
                'priority': 'MEDIUM',
                'category': 'Forms',
                'action': f'Reduce form fields from {forms.avg_fields:.0f} to 3-4',
                'impact': 'Improve form completion rate'
            })
        
        # Trust signal priorities
        if not trust.has_phone:
            actions.append({
                'priority': 'HIGH',
                'category': 'Trust',
                'action': 'Add visible phone number',
                'impact': 'Build trust and enable direct contact'
            })
        
        if not trust.has_social_proof:
            actions.append({
                'priority': 'MEDIUM',
                'category': 'Trust',
                'action': 'Add testimonials or reviews',
                'impact': 'Build credibility and trust'
            })
        
        if not trust.has_credentials:
            actions.append({
                'priority': 'MEDIUM',
                'category': 'Trust',
                'action': 'Highlight professional credentials',
                'impact': 'Establish expertise'
            })
        
        # Accessibility priorities
        if accessibility.score < 70:
            actions.append({
                'priority': 'HIGH',
                'category': 'Accessibility',
                'action': 'Fix accessibility issues (images, labels, ARIA)',
                'impact': 'Improve UX and SEO'
            })
        
        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        actions.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        return actions
    
    def export_report_json(self, report: CROReport, filename: str):
        """Export CRO report to JSON"""
        import json
        from dataclasses import asdict
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, ensure_ascii=False, indent=2)
        
        print(f"✅ CRO report exported to {filename}")

