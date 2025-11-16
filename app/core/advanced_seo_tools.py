"""
Advanced SEO Tools
Additional features for comprehensive SEO analysis:
- Technical SEO Audit
- Page Speed Analysis
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


class AdvancedSEOTools:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    # ==================== Technical SEO Audit ====================
    
    def technical_seo_audit(self, url):
        """
        Comprehensive technical SEO audit
        """
        print(f"\n🔧 Running Technical SEO Audit for: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            audit = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'checks': {}
            }
            
            # 1. HTTPS Check
            audit['checks']['https'] = {
                'status': url.startswith('https://'),
                'importance': 'HIGH',
                'message': 'HTTPS enabled' if url.startswith('https://') else '⚠️ Switch to HTTPS'
            }
            
            # 2. Title Tag
            title = soup.find('title')
            title_length = len(title.text) if title else 0
            audit['checks']['title'] = {
                'exists': title is not None,
                'length': title_length,
                'optimal': 50 <= title_length <= 60,
                'importance': 'HIGH',
                'message': 'Title tag optimal' if 50 <= title_length <= 60 else f'⚠️ Title length is {title_length} (optimal: 50-60)'
            }
            
            # 3. Meta Description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            desc_length = len(meta_desc['content']) if meta_desc and meta_desc.get('content') else 0
            audit['checks']['meta_description'] = {
                'exists': meta_desc is not None,
                'length': desc_length,
                'optimal': 150 <= desc_length <= 160,
                'importance': 'HIGH',
                'message': 'Meta description optimal' if 150 <= desc_length <= 160 else f'⚠️ Description length is {desc_length} (optimal: 150-160)'
            }
            
            # 4. H1 Tag
            h1_tags = soup.find_all('h1')
            audit['checks']['h1'] = {
                'count': len(h1_tags),
                'optimal': len(h1_tags) == 1,
                'importance': 'HIGH',
                'message': 'One H1 tag found' if len(h1_tags) == 1 else f'⚠️ Found {len(h1_tags)} H1 tags (should be 1)'
            }
            
            # 5. Images Alt Text
            images = soup.find_all('img')
            images_without_alt = [img for img in images if not img.get('alt')]
            images_without_alt_list = []
            for img in images_without_alt:
                src = img.get('src', 'No source')
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = url.rstrip('/') + src
                images_without_alt_list.append({
                    'src': src,
                    'title': img.get('title', ''),
                    'class': img.get('class', [])
                })
            
            audit['checks']['images_alt'] = {
                'total_images': len(images),
                'missing_alt': len(images_without_alt),
                'missing_alt_list': images_without_alt_list,
                'importance': 'MEDIUM',
                'message': 'All images have alt text' if len(images_without_alt) == 0 else f'⚠️ {len(images_without_alt)} images missing alt text'
            }
            
            # 6. Canonical Tag
            canonical = soup.find('link', rel='canonical')
            audit['checks']['canonical'] = {
                'exists': canonical is not None,
                'importance': 'MEDIUM',
                'message': 'Canonical tag found' if canonical else '⚠️ Add canonical tag'
            }
            
            # 7. Robots Meta
            robots_meta = soup.find('meta', attrs={'name': 'robots'})
            audit['checks']['robots_meta'] = {
                'exists': robots_meta is not None,
                'content': robots_meta['content'] if robots_meta else None,
                'importance': 'MEDIUM',
                'message': f"Robots meta: {robots_meta['content']}" if robots_meta else 'No robots meta tag'
            }
            
            # 8. Open Graph Tags
            og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
            og_tags_list = []
            for tag in og_tags:
                property_name = tag.get('property', '')
                content = tag.get('content', '')
                og_tags_list.append({
                    'property': property_name,
                    'content': content
                })
            
            audit['checks']['open_graph'] = {
                'count': len(og_tags),
                'tags_list': og_tags_list,
                'importance': 'LOW',
                'message': f'Found {len(og_tags)} Open Graph tags' if len(og_tags) > 0 else 'ℹ️ Consider adding Open Graph tags for social media'
            }
            
            # 9. Schema Markup
            schema_scripts = soup.find_all('script', type='application/ld+json')
            audit['checks']['schema_markup'] = {
                'exists': len(schema_scripts) > 0,
                'count': len(schema_scripts),
                'importance': 'HIGH',
                'message': f'Found {len(schema_scripts)} Schema markup(s)' if len(schema_scripts) > 0 else '⚠️ Add Schema.org structured data'
            }
            
            # 10. Mobile Viewport
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            audit['checks']['mobile_viewport'] = {
                'exists': viewport is not None,
                'importance': 'HIGH',
                'message': 'Mobile viewport configured' if viewport else '⚠️ Add viewport meta tag for mobile'
            }
            
            # Calculate score
            audit['score'] = self._calculate_seo_score(audit['checks'])
            
            # Generate priority actions
            audit['priority_actions'] = self._generate_priority_actions(audit['checks'])
            
            return audit
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def _calculate_seo_score(self, checks):
        """Calculate overall SEO score"""
        total_points = 0
        earned_points = 0
        
        importance_weights = {
            'HIGH': 3,
            'MEDIUM': 2,
            'LOW': 1
        }
        
        for check_name, check_data in checks.items():
            weight = importance_weights.get(check_data['importance'], 1)
            total_points += weight
            
            # Check if passed
            if check_data.get('exists') or check_data.get('optimal') or check_data.get('status'):
                earned_points += weight
        
        score = (earned_points / total_points * 100) if total_points > 0 else 0
        
        return {
            'score': round(score, 1),
            'grade': 'A' if score >= 90 else 'B' if score >= 75 else 'C' if score >= 60 else 'D',
            'total_points': total_points,
            'earned_points': earned_points
        }
    
    def _generate_priority_actions(self, checks):
        """Generate priority actions based on failed checks"""
        actions = []
        
        if not checks:
            return actions
        
        for check_name, check_data in checks.items():
            if not check_data or 'importance' not in check_data:
                continue
                
            if check_data['importance'] == 'HIGH':
                # Check if failed
                if not (check_data.get('exists') or check_data.get('optimal') or check_data.get('status')):
                    actions.append({
                        'check': check_name,
                        'importance': check_data['importance'],
                        'message': check_data.get('message', 'No message available')
                    })
        
        return actions

