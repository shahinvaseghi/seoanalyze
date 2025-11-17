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
        # Website type detection keywords
        self.educational_keywords = [
            'آموزش', 'دوره', 'course', 'training', 'learn', 'tutorial', 'آموزشگاه',
            'مدرس', 'instructor', 'teacher', 'استاد', 'کلاس', 'class', 'workshop',
            'گواهینامه', 'certificate', 'certification', 'دیپلم', 'diploma'
        ]
        
        self.medical_keywords = [
            'دکتر', 'پزشک', 'متخصص', 'doctor', 'specialist', 'medical',
            'بیمارستان', 'hospital', 'کلینیک', 'clinic', 'درمان', 'treatment',
            'جراحی', 'surgery', 'بیمار', 'patient', 'نظام پزشکی'
        ]
        
        self.ecommerce_keywords = [
            'خرید', 'فروش', 'buy', 'sell', 'product', 'محصول', 'قیمت', 'price',
            'سفارش', 'order', 'سبد خرید', 'cart', 'checkout'
        ]
        
        # Expertise signals (Persian and English)
        self.expertise_keywords = [
            'دکتر', 'پزشک', 'متخصص', 'doctor', 'specialist', 'expert',
            'md', 'phd', 'استاد', 'professor', 'دانشیار',
            'مدرک', 'certificate', 'گواهینامه', 'board certified',
            'فلوشیپ', 'fellowship', 'رزیدنت', 'resident',
            'مدرس', 'instructor', 'teacher', 'trainer', 'coach'
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
        
        # Detect website type
        website_type = self._detect_website_type(soup, text, url)
        
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
        
        # Generate recommendations for each component (based on website type)
        expertise['recommendations'] = self._generate_expertise_recommendations(expertise, soup, text, website_type)
        experience['recommendations'] = self._generate_experience_recommendations(experience, soup, text, website_type)
        authoritativeness['recommendations'] = self._generate_authoritativeness_recommendations(authoritativeness, soup, text, website_type)
        trustworthiness['recommendations'] = self._generate_trustworthiness_recommendations(trustworthiness, soup, text, website_type)
        
        return {
            'overall_score': round(overall_score, 1),
            'overall_grade': self._get_grade(overall_score),
            'website_type': website_type,
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
    
    def _detect_website_type(self, soup: BeautifulSoup, text: str, url: str) -> str:
        """Detect website type based on content and keywords"""
        # Count keyword matches
        educational_score = sum(1 for kw in self.educational_keywords if kw in text or kw in url.lower())
        medical_score = sum(1 for kw in self.medical_keywords if kw in text or kw in url.lower())
        ecommerce_score = sum(1 for kw in self.ecommerce_keywords if kw in text or kw in url.lower())
        
        # Check URL patterns
        if any(pattern in url.lower() for pattern in ['/course', '/training', '/learn', '/آموزش', '/دوره']):
            educational_score += 3
        if any(pattern in url.lower() for pattern in ['/doctor', '/clinic', '/hospital', '/پزشک', '/کلینیک']):
            medical_score += 3
        if any(pattern in url.lower() for pattern in ['/shop', '/product', '/buy', '/خرید', '/فروش']):
            ecommerce_score += 3
        
        # Determine type
        if educational_score > medical_score and educational_score > ecommerce_score:
            return 'educational'
        elif medical_score > educational_score and medical_score > ecommerce_score:
            return 'medical'
        elif ecommerce_score > educational_score and ecommerce_score > medical_score:
            return 'ecommerce'
        else:
            return 'general'
    
    def _generate_expertise_recommendations(self, expertise: Dict, soup: BeautifulSoup, text: str, website_type: str) -> List[str]:
        """Generate expertise-specific recommendations based on website type"""
        recommendations = []
        
        # Check if author bio exists
        author_sections = soup.find_all(['section', 'div'], class_=re.compile(r'author|writer|bio|instructor|teacher', re.I))
        if not author_sections:
            if website_type == 'educational':
                recommendations.append("✍️ Add a detailed instructor/teacher bio section with teaching credentials, education, and experience")
            elif website_type == 'medical':
                recommendations.append("✍️ Add a detailed doctor/physician bio section with medical credentials, education, and specialization")
            else:
                recommendations.append("✍️ Add a detailed author bio section with credentials, education, and professional background")
        
        # Check for Person schema
        scripts = soup.find_all('script', type='application/ld+json')
        has_person_schema = False
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and (data.get('@type') == 'Person' or 'author' in data):
                    has_person_schema = True
                    break
            except:
                pass
        
        if not has_person_schema:
            if website_type == 'educational':
                recommendations.append("👨‍🏫 Implement Person schema (JSON-LD) for instructor/teacher profile with teaching credentials")
            elif website_type == 'medical':
                recommendations.append("👨‍⚕️ Implement Person schema (JSON-LD) for doctor/physician profile with medical credentials")
            else:
                recommendations.append("👤 Implement Person schema (JSON-LD) for author profile with credentials")
        
        # Type-specific recommendations
        if website_type == 'educational':
            if expertise['score'] < 50:
                recommendations.append("🎓 Display teaching certifications, educational degrees, and professional qualifications")
                recommendations.append("📚 Mention courses taught, student success rates, and teaching experience")
            if expertise['score'] < 70:
                recommendations.append("🏆 Highlight teaching awards, recognitions, and educational achievements")
                recommendations.append("📖 Showcase published educational content, tutorials, or course materials")
        elif website_type == 'medical':
            if expertise['score'] < 50:
                recommendations.append("🎓 Mention relevant medical certifications, board memberships, and professional qualifications")
                recommendations.append("📜 Display educational background (university, medical school, degrees)")
            if expertise['score'] < 70:
                recommendations.append("🏆 Highlight medical awards, recognitions, and professional achievements")
                recommendations.append("📚 Mention medical publications, research papers, or contributions to the field")
        else:
            if expertise['score'] < 50:
                recommendations.append("🎓 Mention relevant certifications, qualifications, and professional background")
                recommendations.append("📜 Display educational background and professional training")
            if expertise['score'] < 70:
                recommendations.append("🏆 Highlight awards, recognitions, and professional achievements")
                recommendations.append("📚 Mention publications, articles, or contributions to your field")
        
        if not recommendations:
            recommendations.append("✅ Good expertise signals detected. Continue maintaining credentials and qualifications.")
        
        return recommendations
    
    def _generate_experience_recommendations(self, experience: Dict, soup: BeautifulSoup, text: str, website_type: str) -> List[str]:
        """Generate experience-specific recommendations based on website type"""
        recommendations = []
        
        # Check for portfolio/images
        images = soup.find_all('img')
        portfolio_images = [
            img for img in images
            if any(term in img.get('alt', '').lower() for term in ['قبل', 'بعد', 'before', 'after', 'نمونه', 'portfolio', 'student', 'کار'])
        ]
        
        # Check for testimonials
        review_sections = soup.find_all(['div', 'section'], class_=re.compile(r'review|testimonial|نظر|student|feedback', re.I))
        
        # Check for years of experience
        years_pattern = r'(\d+)\s*(سال|year).*?(تجربه|سابقه|experience|teaching)'
        has_years = re.search(years_pattern, text, re.I)
        
        if website_type == 'educational':
            if not portfolio_images:
                recommendations.append("📷 Add student work examples, course completion certificates, or success stories with images")
            if not review_sections:
                recommendations.append("⭐ Include student testimonials, reviews, and success stories")
            if not has_years:
                recommendations.append("📊 Mention years of teaching experience and number of students taught")
            if experience['score'] < 50:
                recommendations.append("📈 Add statistics: number of students, course completion rates, student satisfaction")
                recommendations.append("🎬 Include video testimonials from successful students")
            if experience['score'] < 70:
                recommendations.append("📋 Create detailed case studies showing student progress and achievements")
                recommendations.append("🏅 Display teaching milestones, certifications, and educational achievements")
        elif website_type == 'medical':
            if not portfolio_images:
                recommendations.append("📷 Add before/after portfolio images with descriptive alt text")
            if not review_sections:
                recommendations.append("⭐ Include patient testimonials, reviews, and case studies")
            if not has_years:
                recommendations.append("📊 Mention years of experience and number of cases/patients treated")
            if experience['score'] < 50:
                recommendations.append("📈 Add statistics: number of successful cases, patient satisfaction rate")
                recommendations.append("🎬 Include video testimonials or patient success stories")
            if experience['score'] < 70:
                recommendations.append("📋 Create detailed case studies with before/after results")
                recommendations.append("🏅 Display professional milestones and career highlights")
        else:
            if not portfolio_images:
                recommendations.append("📷 Add portfolio images, project examples, or work samples with descriptive alt text")
            if not review_sections:
                recommendations.append("⭐ Include client testimonials, reviews, and case studies")
            if not has_years:
                recommendations.append("📊 Mention years of experience and number of projects/clients")
            if experience['score'] < 50:
                recommendations.append("📈 Add statistics: number of successful projects, client satisfaction rate")
                recommendations.append("🎬 Include video testimonials or success stories")
            if experience['score'] < 70:
                recommendations.append("📋 Create detailed case studies showing project results")
                recommendations.append("🏅 Display professional milestones and career highlights")
        
        if not recommendations:
            recommendations.append("✅ Good experience signals detected. Continue showcasing your work and achievements.")
        
        return recommendations
    
    def _generate_authoritativeness_recommendations(self, authoritativeness: Dict, soup: BeautifulSoup, text: str, website_type: str) -> List[str]:
        """Generate authoritativeness-specific recommendations based on website type"""
        recommendations = []
        
        # Check for external citations
        external_links = soup.find_all('a', href=re.compile(r'^https?://'))
        
        if website_type == 'educational':
            authority_domains = [
                'coursera', 'udemy', 'edx', 'khan academy', 'ted', 'youtube.com/education',
                'wikipedia', 'stackoverflow', 'github', 'medium', 'towards data science',
                'ministry of education', 'وزارت آموزش', 'دانشگاه'
            ]
            authoritative_links = [
                link for link in external_links
                if any(domain in link.get('href', '').lower() for domain in authority_domains)
            ]
            
            if not authoritative_links:
                recommendations.append("📚 Add references to authoritative educational sources (Coursera, Udemy, educational institutions, Wikipedia)")
        elif website_type == 'medical':
            authority_domains = [
                'pubmed', 'nih.gov', 'who.int', 'cdc.gov',
                'behdasht.gov.ir', 'fda.gov', 'ncbi',
                'sciencedirect', 'springer', 'wiley'
            ]
            authoritative_links = [
                link for link in external_links
                if any(domain in link.get('href', '').lower() for domain in authority_domains)
            ]
            
            if not authoritative_links:
                recommendations.append("📚 Add references to authoritative sources (PubMed, medical journals, WHO, FDA)")
        else:
            authority_domains = [
                'wikipedia', 'gov', 'edu', 'org', 'research', 'study'
            ]
            authoritative_links = [
                link for link in external_links
                if any(domain in link.get('href', '').lower() for domain in authority_domains)
            ]
            
            if not authoritative_links:
                recommendations.append("📚 Add references to authoritative sources relevant to your field")
        
        # Check for references section
        ref_sections = soup.find_all(['section', 'div'], id=re.compile(r'reference|منابع|sources', re.I))
        if not ref_sections and not re.search(r'منابع|references|sources', text, re.I):
            if website_type == 'educational':
                recommendations.append("📖 Create a references section citing educational resources, tutorials, and learning materials")
            elif website_type == 'medical':
                recommendations.append("📖 Create a references section citing medical journals and research papers")
            else:
                recommendations.append("📖 Create a references section citing authoritative sources")
        
        # Check for publication dates
        date_patterns = [
            r'تاریخ\s+انتشار',
            r'به‌روزرسانی',
            r'published|updated',
            r'datePublished|dateModified'
        ]
        
        has_date = any(re.search(pattern, text, re.I) for pattern in date_patterns)
        if not has_date:
            recommendations.append("📅 Include publication date and last updated date to show content freshness")
        
        if website_type == 'educational':
            if authoritativeness['score'] < 50:
                recommendations.append("🏫 Mention educational affiliations (universities, training centers, educational institutions)")
                recommendations.append("🔗 Link to authoritative educational sources and learning platforms")
            if authoritativeness['score'] < 70:
                recommendations.append("📝 Cite recent educational research, teaching methodologies, and best practices")
                recommendations.append("🌐 Get backlinks from educational websites, blogs, and learning communities")
        elif website_type == 'medical':
            if authoritativeness['score'] < 50:
                recommendations.append("🏥 Mention institutional affiliations (hospitals, universities, medical centers)")
                recommendations.append("🔗 Link to authoritative external sources and research papers")
            if authoritativeness['score'] < 70:
                recommendations.append("📝 Cite recent studies and medical research relevant to your content")
                recommendations.append("🌐 Get backlinks from authoritative medical websites and organizations")
        else:
            if authoritativeness['score'] < 50:
                recommendations.append("🏢 Mention professional affiliations and industry associations")
                recommendations.append("🔗 Link to authoritative external sources in your field")
            if authoritativeness['score'] < 70:
                recommendations.append("📝 Cite recent research, studies, and industry best practices")
                recommendations.append("🌐 Get backlinks from authoritative websites in your industry")
        
        if not recommendations:
            recommendations.append("✅ Good authoritativeness signals detected. Continue citing authoritative sources.")
        
        return recommendations
    
    def _generate_trustworthiness_recommendations(self, trustworthiness: Dict, soup: BeautifulSoup, text: str, website_type: str) -> List[str]:
        """Generate trustworthiness-specific recommendations based on website type"""
        recommendations = []
        
        # Check for contact information
        contact_patterns = [
            r'\+?\d{10,}',
            r'[\w\.-]+@[\w\.-]+\.\w+',
            r'تلفن|phone|mobile',
            r'آدرس|address'
        ]
        
        contact_found = any(re.search(pattern, text, re.I) for pattern in contact_patterns)
        if not contact_found:
            recommendations.append("📞 Add complete contact information (phone, email, physical address)")
        
        # Check for privacy policy
        privacy_links = soup.find_all('a', href=re.compile(r'privacy|حریم\s*خصوصی', re.I))
        if not privacy_links and not re.search(r'privacy|حریم\s*خصوصی', text, re.I):
            recommendations.append("🔒 Add privacy policy page and link to it in footer")
        
        # Check for terms of service
        terms_links = soup.find_all('a', href=re.compile(r'terms|قوانین', re.I))
        if not terms_links:
            if website_type == 'educational':
                recommendations.append("📋 Add terms of service and refund policy for course purchases")
            else:
                recommendations.append("📋 Add terms of service page for legal transparency")
        
        # Check for security badges
        cert_patterns = [
            r'ssl|secure',
            r'enamad|نماد اعتماد',
            r'samandehi|ساماندهی',
            r'verified|تایید\s*شده'
        ]
        
        has_cert = any(re.search(pattern, text, re.I) for pattern in cert_patterns)
        if not has_cert:
            recommendations.append("✅ Display trust badges (eNamad, Samandehi, SSL certificate)")
        
        # Check for social media
        social_patterns = [
            r'instagram', r'telegram', r'twitter',
            r'facebook', r'linkedin', r'youtube'
        ]
        
        social_count = sum(1 for pattern in social_patterns if re.search(pattern, text, re.I))
        if social_count < 2:
            recommendations.append("👥 Add social media profiles (Instagram, Telegram, LinkedIn) with verification")
        
        if website_type == 'educational':
            if trustworthiness['score'] < 50:
                recommendations.append("🆔 Display educational licenses, teaching certifications, and accreditations")
                recommendations.append("📸 Add real photos of instructors, classrooms, or learning environment")
            if trustworthiness['score'] < 70:
                recommendations.append("💬 Add live chat or quick contact form for student inquiries")
                recommendations.append("⭐ Display student reviews and ratings from trusted platforms")
        elif website_type == 'medical':
            if trustworthiness['score'] < 50:
                recommendations.append("🆔 Display professional licenses and medical certifications prominently")
                recommendations.append("📸 Add real photos of the team/facility to build trust")
            if trustworthiness['score'] < 70:
                recommendations.append("💬 Add live chat or quick contact form for easy communication")
                recommendations.append("⭐ Display patient reviews and ratings from trusted platforms")
        else:
            if trustworthiness['score'] < 50:
                recommendations.append("🆔 Display professional licenses and certifications prominently")
                recommendations.append("📸 Add real photos of the team/facility to build trust")
            if trustworthiness['score'] < 70:
                recommendations.append("💬 Add live chat or quick contact form for easy communication")
                recommendations.append("⭐ Display customer reviews and ratings from trusted platforms")
        
        if not recommendations:
            recommendations.append("✅ Good trustworthiness signals detected. Continue maintaining transparency and trust.")
        
        return recommendations
    
    def _generate_recommendations(self, expertise, experience, authoritativeness, trustworthiness) -> List[str]:
        """Generate overall actionable recommendations"""
        recommendations = []
        
        # Overall priority recommendations
        if expertise['score'] < 70:
            recommendations.append("🎓 Priority: Improve expertise signals by adding author credentials and qualifications")
        
        if experience['score'] < 70:
            recommendations.append("⭐ Priority: Showcase experience through portfolio, testimonials, and case studies")
        
        if authoritativeness['score'] < 70:
            recommendations.append("📚 Priority: Build authoritativeness by citing authoritative sources and research")
        
        if trustworthiness['score'] < 70:
            recommendations.append("🔒 Priority: Enhance trustworthiness with contact info, policies, and trust badges")
        
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


