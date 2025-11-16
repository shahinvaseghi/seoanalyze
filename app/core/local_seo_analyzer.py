"""
Local SEO Analyzer
Analyzes NAP consistency, local citations, Google Maps integration, and geo-targeting
"""

from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import re


@dataclass
class NAPConsistency:
    """Name, Address, Phone consistency check"""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    consistent: bool = False
    issues: List[str] = field(default_factory=list)
    score: float = 0.0


@dataclass
class Citation:
    """Local business citation"""
    platform: str
    url: str
    priority: str  # 'essential', 'recommended', 'optional'
    category: str  # 'directory', 'social', 'industry-specific'


@dataclass
class GoogleMapsData:
    """Google Maps integration data"""
    has_embedded_map: bool = False
    place_id: Optional[str] = None
    maps_url: Optional[str] = None
    has_utm_tracking: bool = False
    utm_parameters: Dict[str, str] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class GeoSchema:
    """Geographic schema markup"""
    has_geo_coordinates: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    has_area_served: bool = False
    areas_served: List[str] = field(default_factory=list)
    has_service_area: bool = False
    service_radius: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)


@dataclass
class NeighborhoodPage:
    """Neighborhood-specific page suggestion"""
    neighborhood: str
    url_suggested: str
    angle: str  # 'proximity', 'landmarks', 'demographics'
    keywords: List[str]
    priority: int


@dataclass
class LocalSEOReport:
    """Complete Local SEO analysis report"""
    url: str
    nap_consistency: NAPConsistency
    citations_needed: List[Citation]
    google_maps: GoogleMapsData
    geo_schema: GeoSchema
    neighborhood_pages: List[NeighborhoodPage]
    local_keywords: List[str]
    overall_score: float
    grade: str
    priority_actions: List[Dict[str, str]]


class LocalSEOAnalyzer:
    """
    Comprehensive Local SEO Analyzer
    """
    
    def __init__(self):
        self.essential_citations = [
            Citation('Google Business Profile', 'https://business.google.com', 'essential', 'directory'),
            Citation('Bing Places', 'https://www.bingplaces.com', 'essential', 'directory'),
            Citation('Apple Maps', 'https://mapsconnect.apple.com', 'essential', 'directory'),
            Citation('Yelp', 'https://www.yelp.com', 'recommended', 'directory'),
            Citation('Facebook', 'https://www.facebook.com', 'recommended', 'social'),
            Citation('Instagram', 'https://www.instagram.com', 'recommended', 'social'),
        ]
        
        # Persian/Iranian cities and neighborhoods
        self.major_cities_fa = [
            'تهران', 'اصفهان', 'مشهد', 'شیراز', 'تبریز', 'کرج', 'قم', 'اهواز'
        ]
        
        self.tehran_neighborhoods = [
            'سعادت‌آباد', 'فرمانیه', 'نیاوران', 'زعفرانیه', 'ولنجک', 'شهرک غرب',
            'پونک', 'اقدسیه', 'الهیه', 'جردن', 'چیتگر', 'اندیشه', 'پاسداران',
            'قیطریه', 'کامرانیه', 'آجودانیه'
        ]
        
        self.local_keywords_patterns = [
            'در {city}', '{city}', 'نزدیک {landmark}', '{neighborhood}',
            'غرب تهران', 'شمال تهران', 'شرق تهران', 'جنوب تهران'
        ]
    
    def analyze_local_seo(self, soup: BeautifulSoup, url: str, business_name: Optional[str] = None) -> LocalSEOReport:
        """
        Perform comprehensive local SEO analysis
        """
        # 1. NAP Consistency Check
        nap = self._check_nap_consistency(soup, business_name)
        
        # 2. Citation Recommendations
        citations = self._get_citation_recommendations()
        
        # 3. Google Maps Integration
        google_maps = self._check_google_maps(soup)
        
        # 4. Geo Schema Analysis
        geo_schema = self._analyze_geo_schema(soup)
        
        # 5. Neighborhood Page Suggestions
        neighborhood_pages = self._suggest_neighborhood_pages(soup, nap.address)
        
        # 6. Local Keywords Detection
        local_keywords = self._detect_local_keywords(soup)
        
        # 7. Calculate overall score
        overall_score = self._calculate_local_seo_score(
            nap, google_maps, geo_schema, local_keywords
        )
        grade = self._calculate_grade(overall_score)
        
        # 8. Generate priority actions
        priority_actions = self._generate_priority_actions(
            nap, google_maps, geo_schema, neighborhood_pages
        )
        
        return LocalSEOReport(
            url=url,
            nap_consistency=nap,
            citations_needed=citations,
            google_maps=google_maps,
            geo_schema=geo_schema,
            neighborhood_pages=neighborhood_pages,
            local_keywords=local_keywords,
            overall_score=overall_score,
            grade=grade,
            priority_actions=priority_actions
        )
    
    def _check_nap_consistency(self, soup: BeautifulSoup, business_name: Optional[str]) -> NAPConsistency:
        """Check Name, Address, Phone consistency"""
        page_text = soup.get_text()
        page_html = str(soup)
        
        issues = []
        
        # Extract name
        name = business_name
        if not name:
            # Try to extract from schema
            name = self._extract_from_schema(soup, 'name')
            if not name:
                # Try from title or H1
                h1 = soup.find('h1')
                name = h1.get_text(strip=True) if h1 else soup.title.string if soup.title else None
        
        # Extract phone
        phone = self._extract_phone(page_html)
        
        # Extract address
        address = self._extract_address(page_text)
        
        # Extract email
        email = self._extract_email(page_html)
        
        # Check consistency
        consistent = True
        
        if not name:
            issues.append("Business name not found")
            consistent = False
        
        if not phone:
            issues.append("Phone number not found")
            consistent = False
        elif not self._validate_phone_format(phone):
            issues.append(f"Phone format inconsistent: {phone}")
            consistent = False
        
        if not address:
            issues.append("Address not found")
            consistent = False
        
        # Calculate NAP score
        nap_elements = [name, address, phone]
        score = (sum(1 for elem in nap_elements if elem) / len(nap_elements)) * 100
        
        return NAPConsistency(
            name=name,
            address=address,
            phone=phone,
            email=email,
            consistent=consistent,
            issues=issues if issues else ["✅ NAP data found"],
            score=round(score, 1)
        )
    
    def _extract_from_schema(self, soup: BeautifulSoup, field: str) -> Optional[str]:
        """Extract field from Schema.org markup"""
        import json
        
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if field in data:
                        return str(data[field])
                    if '@graph' in data:
                        for item in data['@graph']:
                            if field in item:
                                return str(item[field])
            except (json.JSONDecodeError, AttributeError):
                continue
        return None
    
    def _extract_phone(self, html: str) -> Optional[str]:
        """Extract phone number"""
        # Persian/Iranian phone patterns
        phone_patterns = [
            r'(?:۰۲۱|021|0098 21|\\+98 21)[- ]?\\d{8}',  # Tehran landline
            r'(?:۰۹|09|0098 9|\\+98 9)\\d{9}',  # Mobile
            r'tel:[+\\d\\s()-]+',  # tel: links
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(0).replace('tel:', '').strip()
        
        return None
    
    def _extract_address(self, text: str) -> Optional[str]:
        """Extract address"""
        # Look for common address keywords
        address_keywords = ['آدرس', 'نشانی', 'address']
        
        for keyword in address_keywords:
            if keyword in text:
                # Extract text after the keyword (rough extraction)
                idx = text.find(keyword)
                # Get next 100 chars
                potential_address = text[idx:idx+150]
                # Clean up
                lines = potential_address.split('\n')
                if len(lines) > 1:
                    return lines[1].strip()[:100]
        
        # Try to find from schema
        # (Would check LocalBusiness schema address field)
        
        return None
    
    def _extract_email(self, html: str) -> Optional[str]:
        """Extract email address"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, html)
        return match.group(0) if match else None
    
    def _validate_phone_format(self, phone: str) -> bool:
        """Validate phone number format"""
        # Remove common separators
        cleaned = re.sub(r'[\\s()-]', '', phone)
        # Check if it's a valid length
        return len(cleaned) >= 10
    
    def _get_citation_recommendations(self) -> List[Citation]:
        """Get recommended citation sources"""
        return self.essential_citations
    
    def _check_google_maps(self, soup: BeautifulSoup) -> GoogleMapsData:
        """Check Google Maps integration"""
        has_map = False
        place_id = None
        maps_url = None
        has_utm = False
        utm_params = {}
        recommendations = []
        
        # Check for embedded Google Maps iframe
        iframes = soup.find_all('iframe', src=lambda s: s and 'google.com/maps' in s)
        
        if iframes:
            has_map = True
            maps_url = iframes[0].get('src', '')
            
            # Extract Place ID if present
            place_id_match = re.search(r'place_id=([A-Za-z0-9_-]+)', maps_url)
            if place_id_match:
                place_id = place_id_match.group(1)
            
            # Check for UTM parameters
            utm_pattern = r'utm_(source|medium|campaign|content|term)=([^&]+)'
            utm_matches = re.findall(utm_pattern, maps_url)
            if utm_matches:
                has_utm = True
                utm_params = {param: value for param, value in utm_matches}
        
        # Generate recommendations
        if not has_map:
            recommendations.append("🚨 Add embedded Google Maps to show location")
        else:
            recommendations.append("✅ Google Maps embedded")
        
        if has_map and not place_id:
            recommendations.append("💡 Use Place ID in Maps embed for better tracking")
        
        if has_map and not has_utm:
            recommendations.append("💡 Add UTM parameters to Maps link for analytics")
        
        return GoogleMapsData(
            has_embedded_map=has_map,
            place_id=place_id,
            maps_url=maps_url,
            has_utm_tracking=has_utm,
            utm_parameters=utm_params,
            recommendations=recommendations
        )
    
    def _analyze_geo_schema(self, soup: BeautifulSoup) -> GeoSchema:
        """Analyze geographic schema markup"""
        import json
        
        has_geo = False
        latitude = None
        longitude = None
        has_area_served = False
        areas_served = []
        has_service_area = False
        service_radius = None
        recommendations = []
        
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Handle @graph structure
                items = []
                if isinstance(data, dict):
                    if '@graph' in data:
                        items = data['@graph']
                    else:
                        items = [data]
                
                for item in items:
                    # Check for GeoCoordinates
                    if 'geo' in item:
                        geo_data = item['geo']
                        if isinstance(geo_data, dict):
                            has_geo = True
                            latitude = geo_data.get('latitude')
                            longitude = geo_data.get('longitude')
                    
                    # Check for areaServed
                    if 'areaServed' in item:
                        has_area_served = True
                        area_data = item['areaServed']
                        if isinstance(area_data, list):
                            areas_served = [a.get('name', str(a)) for a in area_data if isinstance(a, dict)]
                        elif isinstance(area_data, dict):
                            areas_served = [area_data.get('name', '')]
                        elif isinstance(area_data, str):
                            areas_served = [area_data]
                    
                    # Check for serviceArea
                    if 'serviceArea' in item:
                        has_service_area = True
                        # Could extract radius if specified
                    
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Generate recommendations
        if not has_geo:
            recommendations.append("Add GeoCoordinates schema for precise location")
        else:
            recommendations.append(f"✅ GeoCoordinates found ({latitude}, {longitude})")
        
        if not has_area_served:
            recommendations.append("Add areaServed schema to specify service areas")
        else:
            recommendations.append(f"✅ AreaServed defined: {', '.join(areas_served[:3])}")
        
        if not has_service_area:
            recommendations.append("Consider adding serviceArea schema with radius")
        
        return GeoSchema(
            has_geo_coordinates=has_geo,
            latitude=latitude,
            longitude=longitude,
            has_area_served=has_area_served,
            areas_served=areas_served,
            has_service_area=has_service_area,
            service_radius=service_radius,
            recommendations=recommendations
        )
    
    def _suggest_neighborhood_pages(self, soup: BeautifulSoup, address: Optional[str]) -> List[NeighborhoodPage]:
        """Suggest neighborhood-specific landing pages"""
        suggestions = []
        
        # Detect current city/neighborhood
        current_city = None
        current_neighborhood = None
        
        page_text = soup.get_text().lower()
        
        # Detect city
        for city in self.major_cities_fa:
            if city in page_text:
                current_city = city
                break
        
        # If Tehran, detect neighborhood
        if current_city == 'تهران' or 'تهران' in page_text:
            for neighborhood in self.tehran_neighborhoods:
                if neighborhood in page_text:
                    current_neighborhood = neighborhood
                    break
            
            # Suggest pages for other neighborhoods
            for neighborhood in self.tehran_neighborhoods[:5]:  # Top 5
                if neighborhood != current_neighborhood:
                    suggestions.append(NeighborhoodPage(
                        neighborhood=neighborhood,
                        url_suggested=f"/services/{neighborhood.replace(' ', '-')}/",
                        angle='proximity',
                        keywords=[
                            f"خدمات در {neighborhood}",
                            f"{neighborhood}",
                            f"نزدیک {neighborhood}"
                        ],
                        priority=8
                    ))
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _detect_local_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Detect local keywords on the page"""
        page_text = soup.get_text().lower()
        local_kws = []
        
        # Check for city names
        for city in self.major_cities_fa:
            if city in page_text:
                local_kws.append(city)
        
        # Check for neighborhoods
        for neighborhood in self.tehran_neighborhoods:
            if neighborhood in page_text:
                local_kws.append(neighborhood)
        
        # Check for directional keywords
        directions = ['غرب تهران', 'شمال تهران', 'شرق تهران', 'جنوب تهران']
        for direction in directions:
            if direction in page_text:
                local_kws.append(direction)
        
        # Check for "near me" equivalents
        near_keywords = ['نزدیک', 'در نزدیکی', 'نزدیک من', 'near me']
        for kw in near_keywords:
            if kw in page_text:
                local_kws.append(kw)
        
        return list(set(local_kws))
    
    def _calculate_local_seo_score(self, nap: NAPConsistency, maps: GoogleMapsData,
                                   geo: GeoSchema, local_kws: List[str]) -> float:
        """Calculate overall local SEO score"""
        score = 0
        
        # NAP score (40% weight)
        score += nap.score * 0.4
        
        # Google Maps (25% weight)
        maps_score = 0
        if maps.has_embedded_map:
            maps_score += 50
        if maps.place_id:
            maps_score += 30
        if maps.has_utm_tracking:
            maps_score += 20
        score += maps_score * 0.25
        
        # Geo Schema (25% weight)
        geo_score = 0
        if geo.has_geo_coordinates:
            geo_score += 40
        if geo.has_area_served:
            geo_score += 40
        if geo.has_service_area:
            geo_score += 20
        score += geo_score * 0.25
        
        # Local Keywords (10% weight)
        kw_score = min(100, len(local_kws) * 20)
        score += kw_score * 0.1
        
        return round(score, 1)
    
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
    
    def _generate_priority_actions(self, nap: NAPConsistency, maps: GoogleMapsData,
                                   geo: GeoSchema, neighborhoods: List[NeighborhoodPage]) -> List[Dict[str, str]]:
        """Generate prioritized local SEO actions"""
        actions = []
        
        # NAP priorities
        if not nap.consistent:
            for issue in nap.issues:
                if "not found" in issue.lower():
                    actions.append({
                        'priority': 'CRITICAL',
                        'category': 'NAP',
                        'action': issue,
                        'details': 'Add consistent NAP (Name, Address, Phone) information'
                    })
        
        # Google Maps priorities
        if not maps.has_embedded_map:
            actions.append({
                'priority': 'HIGH',
                'category': 'Google Maps',
                'action': 'Embed Google Maps on website',
                'details': 'Show business location visually'
            })
        elif not maps.place_id:
            actions.append({
                'priority': 'MEDIUM',
                'category': 'Google Maps',
                'action': 'Add Place ID to Maps embed',
                'details': 'Enables better tracking and integration'
            })
        
        # Schema priorities
        if not geo.has_geo_coordinates:
            actions.append({
                'priority': 'HIGH',
                'category': 'Schema',
                'action': 'Add GeoCoordinates schema',
                'details': 'Latitude/longitude for precise location'
            })
        
        if not geo.has_area_served:
            actions.append({
                'priority': 'MEDIUM',
                'category': 'Schema',
                'action': 'Add areaServed schema',
                'details': 'Specify cities/neighborhoods served'
            })
        
        # Neighborhood pages
        if neighborhoods:
            actions.append({
                'priority': 'MEDIUM',
                'category': 'Content',
                'action': f'Create {len(neighborhoods)} neighborhood-specific pages',
                'details': f"Target: {', '.join([n.neighborhood for n in neighborhoods[:3]])}"
            })
        
        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        actions.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        return actions
    
    def export_report_json(self, report: LocalSEOReport, filename: str):
        """Export local SEO report to JSON"""
        import json
        from dataclasses import asdict
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, ensure_ascii=False, indent=2)
        
        print(f"✅ Local SEO report exported to {filename}")

