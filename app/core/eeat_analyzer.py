"""
E-E-A-T Analyzer
Analyzes Expertise, Experience, Authoritativeness, and Trustworthiness signals
"""

import re
from typing import List, Dict, Tuple, Optional
from bs4 import BeautifulSoup


class EEATAnalyzer:
    """Analyzes E-E-A-T signals in content"""
    
    def __init__(self):
        # Expertise signals (Persian and English)
        self.expertise_keywords = [
            'دکتر', 'پزشک', 'متخصص', 'doctor', 'specialist', 'expert',
            'md', 'phd', 'استاد', 'professor', 'دانشیار',
            'مدرک', 'certificate', 'گواهینامه', 'board certified',
            'فلوشیپ', 'fellowship', 'رزیدنت', 'resident'
        ]
        
        # Authority signals
        self.authority_keywords = [
            'منبع', 'مرجع', 'source', 'reference', 'استناد', 'citation',
            'تحقیق', 'research', 'مطالعه', 'study', 'pubmed',
            'انجمن', 'association', 'سازمان', 'organization',
            'وزارت بهداشت', 'ministry of health', 'fda', 'who'
        ]
        
        # Trust signals
        self.trust_keywords = [
            'تضمین', 'guarantee', 'ضمانت', 'warranty',
            'بیمه', 'insurance', 'مجوز', 'license',
            'نظام پزشکی', 'medical council', 'رسمی', 'official',
            'تایید شده', 'verified', 'certified'
        ]
        
        # Experience signals
        self.experience_keywords = [
            'سابقه', 'تجربه', 'experience', 'years',
            'نمونه کار', 'portfolio', 'قبل و بعد', 'before after',
            'مراجعین', 'patients', 'بیماران', 'clients',
            'موفق', 'successful', 'انجام شده', 'performed'
        ]
    
    def analyze_eeat(self, soup: BeautifulSoup, url: str) -> Dict[str, any]:
        """
        Comprehensive E-E-A-T analysis
        
        Args:
            soup: BeautifulSoup object of the page
            url: Page URL
            
        Returns:
            Dictionary with E-E-A-T scores and signals
        """
        text = soup.get_text().lower()
        
        # Analyze each component
        expertise = self._analyze_expertise(soup, text)
        experience = self._analyze_experience(soup, text)
        authoritativeness = self._analyze_authoritativeness(soup, text, url)
        trustworthiness = self._analyze_trustworthiness(soup, text)
        
        # Calculate overall score
        overall_score = (
            expertise['score'] * 0.3 +
            experience['score'] * 0.25 +
            authoritativeness['score'] * 0.25 +
            trustworthiness['score'] * 0.2
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'overall_grade': self._get_grade(overall_score),
            'expertise': expertise,
            'experience': experience,
            'authoritativeness': authoritativeness,
            'trustworthiness': trustworthiness,
            'recommendations': self._generate_recommendations(expertise, experience, authoritativeness, trustworthiness)
        }
    
    def _analyze_expertise(self, soup: BeautifulSoup, text: str) -> Dict:
        """Analyze expertise signals"""
        signals_found = []
        score = 0
        
        # Check for expertise keywords
        for keyword in self.expertise_keywords:
            if keyword in text:
                signals_found.append(keyword)
                score += 10
        
        # Check for author bio section
        author_sections = soup.find_all(['section', 'div'], class_=re.compile(r'author|writer|bio', re.I))
        if author_sections:
            signals_found.append('author_bio_section')
            score += 15
        
        # Check for credentials in schema
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Check for Person schema with credentials
                    if data.get('@type') == 'Person' or 'author' in data:
                        signals_found.append('author_schema')
                        score += 20
            except:
                pass
        
        # Check for educational background mentions
        education_patterns = [
            r'دانشگاه\s+[\w\s]+',
            r'university\s+of\s+[\w\s]+',
            r'دانشکده\s+پزشکی',
            r'medical\s+school'
        ]
        
        for pattern in education_patterns:
            if re.search(pattern, text, re.I):
                signals_found.append('educational_background')
                score += 10
                break
        
        # Normalize score to 0-100
        score = min(score, 100)
        
        return {
            'score': score,
            'grade': self._get_grade(score),
            'signals_found': signals_found,
            'signal_count': len(signals_found)
        }
    
    def _analyze_experience(self, soup: BeautifulSoup, text: str) -> Dict:
        """Analyze experience signals"""
        signals_found = []
        score = 0
        
        # Check for experience keywords
        for keyword in self.experience_keywords:
            if keyword in text:
                signals_found.append(keyword)
                score += 8
        
        # Check for portfolio/before-after images
        images = soup.find_all('img')
        portfolio_images = [
            img for img in images
            if any(term in img.get('alt', '').lower() for term in ['قبل', 'بعد', 'before', 'after', 'نمونه'])
        ]
        
        if portfolio_images:
            signals_found.append('portfolio_images')
            score += 20
        
        # Check for testimonials/reviews
        review_sections = soup.find_all(['div', 'section'], class_=re.compile(r'review|testimonial|نظر', re.I))
        if review_sections:
            signals_found.append('testimonials')
            score += 15
        
        # Check for case studies
        if re.search(r'مورد\s+\d+', text) or re.search(r'\d+\s+cases?', text):
            signals_found.append('case_numbers')
            score += 10
        
        # Check for years of experience
        years_pattern = r'(\d+)\s*(سال|year).*?(تجربه|سابقه|experience)'
        years_match = re.search(years_pattern, text, re.I)
        if years_match:
            years = int(years_match.group(1))
            signals_found.append(f'{years}_years_experience')
            score += min(years * 2, 25)  # Max 25 points
        
        # Normalize score
        score = min(score, 100)
        
        return {
            'score': score,
            'grade': self._get_grade(score),
            'signals_found': signals_found,
            'signal_count': len(signals_found)
        }
    
    def _analyze_authoritativeness(self, soup: BeautifulSoup, text: str, url: str) -> Dict:
        """Analyze authoritativeness signals"""
        signals_found = []
        score = 0
        
        # Check for authority keywords
        for keyword in self.authority_keywords:
            if keyword in text:
                signals_found.append(keyword)
                score += 8
        
        # Check for external citations/references
        external_links = soup.find_all('a', href=re.compile(r'^https?://'))
        authority_domains = [
            'pubmed', 'nih.gov', 'who.int', 'cdc.gov',
            'behdasht.gov.ir', 'fda.gov', 'ncbi',
            'sciencedirect', 'springer', 'wiley'
        ]
        
        authoritative_links = [
            link for link in external_links
            if any(domain in link.get('href', '').lower() for domain in authority_domains)
        ]
        
        if authoritative_links:
            signals_found.append('authoritative_citations')
            score += 20
        
        # Check for references section
        ref_sections = soup.find_all(['section', 'div'], id=re.compile(r'reference|منابع', re.I))
        if ref_sections or re.search(r'منابع\s*:?', text, re.I):
            signals_found.append('references_section')
            score += 15
        
        # Check for publication/update dates
        date_patterns = [
            r'تاریخ\s+انتشار',
            r'به‌روزرسانی',
            r'published|updated',
            r'datePublished|dateModified'
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, text, re.I):
                signals_found.append('publication_date')
                score += 10
                break
        
        # Check for affiliation with institutions
        institution_patterns = [
            r'دانشگاه\s+علوم\s+پزشکی',
            r'بیمارستان',
            r'medical\s+university',
            r'hospital'
        ]
        
        for pattern in institution_patterns:
            if re.search(pattern, text, re.I):
                signals_found.append('institutional_affiliation')
                score += 15
                break
        
        # Normalize score
        score = min(score, 100)
        
        return {
            'score': score,
            'grade': self._get_grade(score),
            'signals_found': signals_found,
            'signal_count': len(signals_found),
            'authoritative_links_count': len(authoritative_links)
        }
    
    def _analyze_trustworthiness(self, soup: BeautifulSoup, text: str) -> Dict:
        """Analyze trustworthiness signals"""
        signals_found = []
        score = 0
        
        # Check for trust keywords
        for keyword in self.trust_keywords:
            if keyword in text:
                signals_found.append(keyword)
                score += 8
        
        # Check for HTTPS
        # (This would be checked from the URL in real implementation)
        signals_found.append('https_enabled')
        score += 10
        
        # Check for contact information
        contact_patterns = [
            r'\+?\d{10,}',  # Phone numbers
            r'[\w\.-]+@[\w\.-]+\.\w+',  # Email
            r'تلفن|phone|mobile',
            r'آدرس|address'
        ]
        
        contact_found = False
        for pattern in contact_patterns:
            if re.search(pattern, text, re.I):
                contact_found = True
                break
        
        if contact_found:
            signals_found.append('contact_information')
            score += 15
        
        # Check for privacy policy
        privacy_links = soup.find_all('a', href=re.compile(r'privacy|حریم\s*خصوصی', re.I))
        if privacy_links or re.search(r'privacy|حریم\s*خصوصی', text, re.I):
            signals_found.append('privacy_policy')
            score += 10
        
        # Check for terms of service
        terms_links = soup.find_all('a', href=re.compile(r'terms|قوانین', re.I))
        if terms_links:
            signals_found.append('terms_of_service')
            score += 10
        
        # Check for security badges/certifications
        cert_patterns = [
            r'ssl|secure',
            r'enamad|نماد اعتماد',
            r'samandehi|ساماندهی',
            r'verified|تایید\s*شده'
        ]
        
        for pattern in cert_patterns:
            if re.search(pattern, text, re.I):
                signals_found.append('security_badges')
                score += 12
                break
        
        # Check for about page
        about_links = soup.find_all('a', href=re.compile(r'about|درباره', re.I))
        if about_links:
            signals_found.append('about_page')
            score += 8
        
        # Check for social media links
        social_patterns = [
            r'instagram', r'telegram', r'twitter',
            r'facebook', r'linkedin', r'youtube'
        ]
        
        social_count = sum(1 for pattern in social_patterns if re.search(pattern, text, re.I))
        if social_count > 0:
            signals_found.append(f'{social_count}_social_profiles')
            score += min(social_count * 5, 15)  # Max 15 points
        
        # Normalize score
        score = min(score, 100)
        
        return {
            'score': score,
            'grade': self._get_grade(score),
            'signals_found': signals_found,
            'signal_count': len(signals_found)
        }
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_recommendations(self, expertise, experience, authoritativeness, trustworthiness) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Expertise recommendations
        if expertise['score'] < 70:
            recommendations.append("✍️ Add detailed author bio with credentials and education")
            recommendations.append("👨‍⚕️ Implement Person schema for author/doctor profile")
            recommendations.append("🎓 Mention relevant certifications and board memberships")
        
        # Experience recommendations
        if experience['score'] < 70:
            recommendations.append("📷 Add before/after portfolio images with alt text")
            recommendations.append("⭐ Include patient testimonials and reviews")
            recommendations.append("📊 Mention years of experience and number of cases")
        
        # Authoritativeness recommendations
        if authoritativeness['score'] < 70:
            recommendations.append("📚 Add references to medical journals (PubMed, etc.)")
            recommendations.append("📅 Include publication and last updated dates")
            recommendations.append("🏥 Mention institutional affiliations")
            recommendations.append("🔗 Link to authoritative external sources")
        
        # Trustworthiness recommendations
        if trustworthiness['score'] < 70:
            recommendations.append("📞 Add complete contact information (phone, email, address)")
            recommendations.append("🔒 Add privacy policy and terms of service pages")
            recommendations.append("✅ Display trust badges (eNamad, Samandehi, SSL)")
            recommendations.append("👥 Add social media profiles and verification")
        
        return recommendations


# ==================== Example Usage ====================

if __name__ == "__main__":
    # Test HTML
    test_html = """
    <html>
    <head>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": "دکتر محمد رضایی",
            "jobTitle": "متخصص پوست و مو",
            "affiliation": {
                "@type": "Organization",
                "name": "دانشگاه علوم پزشکی تهران"
            }
        }
        </script>
    </head>
    <body>
        <h1>درباره دکتر</h1>
        <p>دکتر محمد رضایی با 15 سال سابقه در زمینه پوست و مو فعالیت می‌کند.
        ایشان دانش‌آموخته دانشگاه علوم پزشکی تهران و دارای فلوشیپ از کشور آلمان هستند.</p>
        
        <h2>نمونه کارها</h2>
        <img src="before.jpg" alt="قبل از لیزر">
        <img src="after.jpg" alt="بعد از لیزر">
        
        <h2>نظرات بیماران</h2>
        <div class="testimonials">
            <p>بسیار راضی هستم - خانم احمدی</p>
        </div>
        
        <h2>منابع</h2>
        <p>مطالعات علمی از 
        <a href="https://pubmed.ncbi.nlm.nih.gov/">PubMed</a>
        و <a href="https://behdasht.gov.ir/">وزارت بهداشت</a>
        </p>
        
        <footer>
            <p>تلفن: 02188888888</p>
            <p>آدرس: تهران، سعادت‌آباد</p>
            <a href="/privacy">حریم خصوصی</a>
            <img src="enamad.png" alt="نماد اعتماد الکترونیکی">
        </footer>
    </body>
    </html>
    """
    
    soup = BeautifulSoup(test_html, 'html.parser')
    analyzer = EEATAnalyzer()
    
    print("\n" + "="*70)
    print("🏆 E-E-A-T ANALYZER TEST")
    print("="*70 + "\n")
    
    # Analyze
    results = analyzer.analyze_eeat(soup, "https://example.com/about-doctor/")
    
    print(f"📊 Overall E-E-A-T Score: {results['overall_score']}/100 (Grade: {results['overall_grade']})\n")
    
    print(f"🎓 Expertise: {results['expertise']['score']}/100 (Grade: {results['expertise']['grade']})")
    print(f"   Signals: {', '.join(results['expertise']['signals_found'][:5])}\n")
    
    print(f"⭐ Experience: {results['experience']['score']}/100 (Grade: {results['experience']['grade']})")
    print(f"   Signals: {', '.join(results['experience']['signals_found'][:5])}\n")
    
    print(f"📚 Authoritativeness: {results['authoritativeness']['score']}/100 (Grade: {results['authoritativeness']['grade']})")
    print(f"   Signals: {', '.join(results['authoritativeness']['signals_found'][:5])}")
    print(f"   Authoritative Links: {results['authoritativeness']['authoritative_links_count']}\n")
    
    print(f"🔒 Trustworthiness: {results['trustworthiness']['score']}/100 (Grade: {results['trustworthiness']['grade']})")
    print(f"   Signals: {', '.join(results['trustworthiness']['signals_found'][:5])}\n")
    
    if results['recommendations']:
        print("💡 Recommendations:")
        for rec in results['recommendations'][:8]:
            print(f"   {rec}")


