"""
SEO Analyzer Tool
A comprehensive Python tool for SEO analysis including:
- Competitor Analysis
- Google Trends
- Keyword Research
- Content Gap Analysis
- Technical SEO Audit
"""

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, urljoin
import time
from collections import Counter
import re
from datetime import datetime
import csv
from time import perf_counter

class SEOAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.results = {}
    
    # ==================== Google Search ====================
    
    def search_google(self, keyword, num_results=10):
        """
        Search Google and extract top results
        
        Args:
            keyword: Search keyword
            num_results: Number of results to extract (default 10)
            
        Returns:
            List of URLs from search results
        """
        print(f"\n🔍 جستجوی گوگل برای: '{keyword}'")
        
        try:
            # Encode keyword for URL
            from urllib.parse import quote_plus
            encoded_keyword = quote_plus(keyword)
            
            # Google search URL
            search_url = f"https://www.google.com/search?q={encoded_keyword}&num={num_results}"
            
            # Add more realistic headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Make request
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"⚠️ خطا در دریافت نتایج: کد {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract URLs from search results
            urls = []
            
            # Method 1: Look for result divs
            for result in soup.find_all('div', class_='g'):
                link = result.find('a', href=True)
                if link and link['href'].startswith('http'):
                    url = link['href']
                    # Skip Google's own links
                    if 'google.com' not in url and 'youtube.com' not in url:
                        if url not in urls:
                            urls.append(url)
                            print(f"  ✓ {len(urls)}. {url[:60]}...")
            
            # Method 2: Look for cite tags (backup)
            if len(urls) < num_results:
                for cite in soup.find_all('cite'):
                    url_text = cite.get_text()
                    if url_text.startswith('http'):
                        if url_text not in urls and 'google.com' not in url_text:
                            urls.append(url_text)
                            print(f"  ✓ {len(urls)}. {url_text[:60]}...")
            
            # Method 3: Look for all links (last resort)
            if len(urls) < 3:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('http') and 'google.com' not in href:
                        if href not in urls and 'youtube.com' not in href:
                            urls.append(href)
                            print(f"  ✓ {len(urls)}. {href[:60]}...")
                            if len(urls) >= num_results:
                                break
            
            # Limit to requested number
            urls = urls[:num_results]
            
            print(f"\n✅ پیدا شد: {len(urls)} URL")
            
            if len(urls) == 0:
                print("⚠️ هیچ نتیجه‌ای پیدا نشد. احتمالاً گوگل درخواست را block کرده است.")
                print("💡 راه‌حل:")
                print("   1. از VPN استفاده کنید")
                print("   2. یا URL های رقبا را دستی در تب 'تحلیل رقبا' وارد کنید")
                print("   3. یا چند دقیقه صبر کنید و دوباره تلاش کنید")
            
            return urls
            
        except Exception as e:
            print(f"❌ خطا در جستجوی گوگل: {str(e)}")
            return []
    
    def analyze_google_results(self, keyword, num_results=10, track_keywords=None):
        """
        Search Google for keyword and analyze top results
        
        Args:
            keyword: Search keyword
            num_results: Number of results to analyze (default 10)
            track_keywords: List of keywords to track (optional)
            
        Returns:
            Competitor analysis data
        """
        print("\n" + "="*60)
        print("🔍 تحلیل پیشرفته رقبا - بر اساس نتایج گوگل")
        print("="*60)
        
        # Search Google
        urls = self.search_google(keyword, num_results)
        
        if not urls:
            print("\n❌ نتیجه‌ای برای تحلیل یافت نشد")
            return []
        
        # Analyze the URLs
        print(f"\n📊 شروع تحلیل {len(urls)} رقیب...")
        results = self.compare_competitors(urls, keywords=track_keywords)
        
        return results
    
    # ==================== Competitor Analysis ====================
    
    def analyze_competitor(self, url, keywords=None):
        """
        Analyze a competitor's webpage for SEO metrics
        
        Args:
            url: URL to analyze
            keywords: List of keywords to track (optional)
        """
        print(f"\n🔍 Analyzing competitor: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get full text for keyword analysis
            full_text = soup.get_text().lower()
            
            # Extract additional data for Schema
            logo_url = self._extract_logo_url(soup, url)
            featured_image = self._extract_featured_image(soup, url)
            address_data = self._extract_address(soup)
            maps_url = self._extract_google_maps_url(soup)
            page_type = self._detect_page_type(soup, url)
            
            analysis = {
                'url': url,
                'status_code': response.status_code,
                'title': self._extract_title(soup),
                'meta_description': self._extract_meta_description(soup),
                'meta_keywords': self._extract_meta_keywords(soup),
                'h1_tags': self._extract_h1_tags(soup),
                'h1_count': len(self._extract_h1_tags(soup)),
                'h2_tags': self._extract_h2_tags(soup),
                'h2_count': len(self._extract_h2_tags(soup)),
                'h3_tags': self._extract_h3_tags(soup),
                'h3_count': len(self._extract_h3_tags(soup)),
                'h4_tags': self._extract_h4_tags(soup),
                'h4_count': len(self._extract_h4_tags(soup)),
                'word_count': self._count_words(soup),
                'images_count': self._count_images(soup),
                'images_without_alt': self._count_images_without_alt(soup),
                'images_detailed': self._analyze_images_detailed(soup, url),
                'internal_links': self._count_internal_links(soup, url),
                'internal_links_details': self._extract_internal_links(soup, url),
                'external_links': self._count_external_links(soup, url),
                'external_links_details': self._extract_external_links(soup, url),
                'has_schema': self._check_schema_markup(soup),
                'page_load_size': len(response.content) / 1024,  # KB
                'keywords_found': self._extract_keywords(soup),
                'content_structure': self._analyze_content_structure(soup),
                # New Schema-related data
                'logo_url': logo_url,
                'featured_image': featured_image,
                'address': address_data,
                'google_maps_url': maps_url,
                'detected_page_type': page_type
            }
            
            # Generate Schema suggestion
            schema_suggestion = self._generate_schema_suggestion(
                soup, url, page_type, logo_url, featured_image, address_data, maps_url
            )
            analysis['suggested_schema'] = schema_suggestion
            
            # Add keyword tracking if keywords provided
            if keywords:
                analysis['keyword_tracking'] = self._track_keywords(full_text, keywords, analysis['word_count'])
            
            # Analyze page speed (Desktop & Mobile)
            speed_data = self._analyze_page_speed(url)
            analysis['page_speed'] = speed_data
            
            # Analyze Mobile UX & UI
            ux_data = self._analyze_mobile_ux(soup, url)
            analysis['mobile_ux'] = ux_data
            
            print(f"✅ Analysis complete for {url}")
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing {url}: {str(e)}")
            return None
    
    def _extract_title(self, soup):
        title = soup.find('title')
        return title.text.strip() if title else "No title found"
    
    def _extract_meta_description(self, soup):
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta['content'].strip() if meta and meta.get('content') else "No meta description"
    
    def _extract_meta_keywords(self, soup):
        meta = soup.find('meta', attrs={'name': 'keywords'})
        return meta['content'].strip() if meta and meta.get('content') else "No meta keywords"
    
    def _extract_h1_tags(self, soup):
        return [h1.text.strip() for h1 in soup.find_all('h1')]
    
    def _extract_h2_tags(self, soup):
        return [h2.text.strip() for h2 in soup.find_all('h2')]
    
    def _extract_h3_tags(self, soup):
        return [h3.text.strip() for h3 in soup.find_all('h3')]
    
    def _extract_h4_tags(self, soup):
        return [h4.text.strip() for h4 in soup.find_all('h4')]
    
    def _count_words(self, soup):
        # Remove script and style elements
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.decompose()
        
        text = soup.get_text()
        words = text.split()
        return len(words)
    
    def _count_images(self, soup):
        return len(soup.find_all('img'))
    
    def _count_images_without_alt(self, soup):
        images = soup.find_all('img')
        return sum(1 for img in images if not img.get('alt'))
    
    def _analyze_images_detailed(self, soup, base_url):
        """Analyze images in detail including type, links, and attributes"""
        images = soup.find_all('img')
        detailed_images = []
        
        for img in images:
            src = img.get('src', '')
            if src:
                # Make absolute URL
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = base_url.rstrip('/') + src
                elif not src.startswith('http'):
                    src = base_url.rstrip('/') + '/' + src.lstrip('/')
                
                # Determine image type from extension
                img_ext = src.split('?')[0].split('.')[-1].lower()
                img_type = 'Unknown'
                if img_ext in ['jpg', 'jpeg']:
                    img_type = 'JPEG'
                elif img_ext == 'png':
                    img_type = 'PNG'
                elif img_ext == 'gif':
                    img_type = 'GIF'
                elif img_ext == 'svg':
                    img_type = 'SVG'
                elif img_ext == 'webp':
                    img_type = 'WebP'
                elif img_ext == 'ico':
                    img_type = 'Icon'
                elif img_ext in ['bmp', 'tiff', 'tif']:
                    img_type = img_ext.upper()
                
                # Check if image is wrapped in anchor tag
                parent_link = img.find_parent('a')
                link_url = None
                link_type = None
                
                if parent_link and parent_link.get('href'):
                    link_url = parent_link.get('href')
                    # Make absolute URL
                    if link_url.startswith('//'):
                        link_url = 'https:' + link_url
                    elif link_url.startswith('/'):
                        link_url = base_url.rstrip('/') + link_url
                    elif not link_url.startswith('http'):
                        link_url = base_url.rstrip('/') + '/' + link_url.lstrip('/')
                    
                    # Determine link type
                    domain = urlparse(base_url).netloc
                    link_domain = urlparse(link_url).netloc
                    
                    if domain == link_domain or not link_domain:
                        link_type = 'internal'
                    else:
                        link_type = 'external'
                
                img_data = {
                    'src': src,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'type': img_type,
                    'has_alt': bool(img.get('alt')),
                    'is_linked': bool(parent_link),
                    'link_url': link_url,
                    'link_type': link_type,
                    'width': img.get('width', ''),
                    'height': img.get('height', ''),
                    'loading': img.get('loading', ''),
                }
                
                detailed_images.append(img_data)
        
        # Also check for videos
        videos = soup.find_all(['video', 'iframe'])
        video_list = []
        
        for vid in videos:
            if vid.name == 'video':
                video_list.append({
                    'type': 'video',
                    'src': vid.get('src', ''),
                    'poster': vid.get('poster', ''),
                })
            elif vid.name == 'iframe':
                src = vid.get('src', '')
                if 'youtube' in src or 'vimeo' in src or 'video' in src.lower():
                    video_list.append({
                        'type': 'embedded_video',
                        'src': src,
                    })
        
        return {
            'images': detailed_images,
            'videos': video_list,
            'total_images': len(images),
            'total_videos': len(video_list),
            'images_with_alt': sum(1 for img in detailed_images if img['has_alt']),
            'images_without_alt': sum(1 for img in detailed_images if not img['has_alt']),
            'linked_images': sum(1 for img in detailed_images if img['is_linked']),
            'image_types': {
                'JPEG': sum(1 for img in detailed_images if img['type'] == 'JPEG'),
                'PNG': sum(1 for img in detailed_images if img['type'] == 'PNG'),
                'GIF': sum(1 for img in detailed_images if img['type'] == 'GIF'),
                'SVG': sum(1 for img in detailed_images if img['type'] == 'SVG'),
                'WebP': sum(1 for img in detailed_images if img['type'] == 'WebP'),
                'Other': sum(1 for img in detailed_images if img['type'] not in ['JPEG', 'PNG', 'GIF', 'SVG', 'WebP']),
            }
        }
    
    def _count_internal_links(self, soup, base_url):
        domain = urlparse(base_url).netloc
        links = soup.find_all('a', href=True)
        return sum(1 for link in links if domain in link['href'])
    
    def _count_external_links(self, soup, base_url):
        domain = urlparse(base_url).netloc
        links = soup.find_all('a', href=True)
        return sum(1 for link in links if link['href'].startswith('http') and domain not in link['href'])
    
    def _extract_internal_links(self, soup, base_url, limit=10):
        """Extract internal links with anchor text"""
        domain = urlparse(base_url).netloc
        links = soup.find_all('a', href=True)
        
        internal_links = []
        for link in links:
            href = link['href']
            
            # Check if internal
            if domain in href or (not href.startswith('http') and not href.startswith('//')):
                # Get anchor text
                anchor_text = link.get_text(strip=True)
                
                # Make absolute URL
                if not href.startswith('http'):
                    href = urljoin(base_url, href)
                
                if anchor_text:  # Only add if has text
                    internal_links.append({
                        'anchor': anchor_text,
                        'url': href
                    })
                    
                    if len(internal_links) >= limit:
                        break
        
        return internal_links
    
    def _extract_external_links(self, soup, base_url, limit=10):
        """Extract external links with anchor text"""
        domain = urlparse(base_url).netloc
        links = soup.find_all('a', href=True)
        
        external_links = []
        for link in links:
            href = link['href']
            
            # Check if external
            if href.startswith('http') and domain not in href:
                # Get anchor text
                anchor_text = link.get_text(strip=True)
                
                if anchor_text:  # Only add if has text
                    external_links.append({
                        'anchor': anchor_text,
                        'url': href
                    })
                    
                    if len(external_links) >= limit:
                        break
        
        return external_links
    
    def _check_schema_markup(self, soup):
        schema_types = []
        
        # Check for JSON-LD
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and '@type' in data:
                    schema_types.append(data['@type'])
            except:
                pass
        
        return schema_types if schema_types else False
    
    def _extract_logo_url(self, soup, base_url):
        """Extract website logo URL"""
        logo_url = None
        
        # Method 1: Check schema.org logo
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'logo' in data:
                        logo_url = data['logo']
                        if isinstance(logo_url, dict) and 'url' in logo_url:
                            logo_url = logo_url['url']
                        break
                    elif 'publisher' in data and isinstance(data['publisher'], dict):
                        if 'logo' in data['publisher']:
                            logo_url = data['publisher']['logo']
                            if isinstance(logo_url, dict) and 'url' in logo_url:
                                logo_url = logo_url['url']
                            break
            except:
                pass
        
        # Method 2: Check common logo locations
        if not logo_url:
            # Look for logo in header
            logo_selectors = [
                'img.logo', 'img#logo', 'a.logo img', '.site-logo img',
                'header img', '.header-logo img', '[class*="logo"] img'
            ]
            for selector in logo_selectors:
                logo = soup.select_one(selector)
                if logo and logo.get('src'):
                    logo_url = logo['src']
                    break
        
        # Method 3: Look for PNG in common paths
        if not logo_url:
            common_paths = ['/logo.png', '/images/logo.png', '/assets/logo.png']
            for path in common_paths:
                test_url = urljoin(base_url, path)
                try:
                    resp = requests.head(test_url, timeout=3)
                    if resp.status_code == 200:
                        logo_url = test_url
                        break
                except:
                    pass
        
        # Make absolute URL
        if logo_url and not logo_url.startswith('http'):
            logo_url = urljoin(base_url, logo_url)
        
        return logo_url
    
    def _extract_featured_image(self, soup, base_url):
        """Extract featured/main image URL"""
        featured_image = None
        
        # Method 1: Open Graph image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            featured_image = og_image['content']
        
        # Method 2: Twitter card image
        if not featured_image:
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                featured_image = twitter_image['content']
        
        # Method 3: Schema.org image
        if not featured_image:
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'image' in data:
                        img = data['image']
                        if isinstance(img, str):
                            featured_image = img
                        elif isinstance(img, list) and len(img) > 0:
                            featured_image = img[0]
                        elif isinstance(img, dict) and 'url' in img:
                            featured_image = img['url']
                        if featured_image:
                            break
                except:
                    pass
        
        # Method 4: First article image
        if not featured_image:
            article_img = soup.select_one('article img, .post-content img, .entry-content img')
            if article_img and article_img.get('src'):
                featured_image = article_img['src']
        
        # Make absolute URL
        if featured_image and not featured_image.startswith('http'):
            featured_image = urljoin(base_url, featured_image)
        
        return featured_image
    
    def _extract_address(self, soup):
        """Extract physical address"""
        address_data = {
            'street': None,
            'locality': None,
            'country': None,
            'full_address': None
        }
        
        # Method 1: Schema.org address
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    address = None
                    if 'address' in data:
                        address = data['address']
                    elif 'publisher' in data and isinstance(data['publisher'], dict):
                        address = data['publisher'].get('address')
                    
                    if address and isinstance(address, dict):
                        address_data['street'] = address.get('streetAddress')
                        address_data['locality'] = address.get('addressLocality')
                        address_data['country'] = address.get('addressCountry', 'IR')
                        
                        # Build full address
                        parts = [address_data['street'], address_data['locality']]
                        address_data['full_address'] = ', '.join([p for p in parts if p])
                        return address_data
            except:
                pass
        
        # Method 2: Look for address in footer/contact sections
        address_selectors = [
            'address', '.address', '#address', '.contact-address',
            'footer address', '.footer-address'
        ]
        for selector in address_selectors:
            addr_elem = soup.select_one(selector)
            if addr_elem:
                address_data['full_address'] = addr_elem.get_text(strip=True)
                break
        
        return address_data
    
    def _extract_google_maps_url(self, soup):
        """Extract Google Maps URL"""
        maps_url = None
        
        # Method 1: Schema.org hasMap
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'hasMap' in data:
                        maps_url = data['hasMap']
                        return maps_url
                    elif 'publisher' in data and isinstance(data['publisher'], dict):
                        if 'hasMap' in data['publisher']:
                            maps_url = data['publisher']['hasMap']
                            return maps_url
            except:
                pass
        
        # Method 2: Look for Google Maps links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'maps.google.com' in href or 'goo.gl/maps' in href or 'google.com/maps' in href:
                maps_url = href
                break
        
        # Method 3: Look for embedded maps
        if not maps_url:
            iframe = soup.find('iframe', src=re.compile(r'google\.com/maps'))
            if iframe and iframe.get('src'):
                maps_url = iframe['src']
        
        return maps_url
    
    def _detect_page_type(self, soup, url):
        """Detect the type of page for Schema.org"""
        page_type = 'WebPage'  # Default
        
        # Check existing schema
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and '@type' in data:
                    return data['@type']
            except:
                pass
        
        # Detect based on content
        title = self._extract_title(soup).lower()
        h1_tags = ' '.join(self._extract_h1_tags(soup)).lower()
        content = (title + ' ' + h1_tags).lower()
        
        # Course detection
        course_keywords = ['آموزش', 'دوره', 'course', 'training', 'learn', 'tutorial']
        if any(kw in content for kw in course_keywords):
            page_type = 'Course'
        
        # Article detection
        elif soup.find('article') or 'مقاله' in content or 'article' in content:
            page_type = 'Article'
        
        # Product detection
        elif 'خرید' in content or 'قیمت' in content or 'product' in content or soup.select_one('.product, .woocommerce'):
            page_type = 'Product'
        
        # FAQ detection
        elif 'سوال' in content or 'faq' in content or len(soup.find_all(['details', 'dl'])) > 3:
            page_type = 'FAQPage'
        
        # Organization/About detection
        elif 'درباره' in content or 'about' in url or 'contact' in url:
            page_type = 'Organization'
        
        return page_type
    
    def _generate_schema_suggestion(self, soup, url, page_type, logo_url, featured_image, address_data, maps_url):
        """Generate suggested Schema.org markup"""
        
        domain = urlparse(url).netloc
        site_name = domain.replace('www.', '').split('.')[0].title()
        
        title = self._extract_title(soup)
        description = self._extract_meta_description(soup)
        
        # Base schema
        schema = {
            "@context": "https://schema.org",
            "@type": page_type,
            "name": title,
            "description": description if description != "No meta description" else title,
            "url": url
        }
        
        # Add featured image
        if featured_image:
            schema["image"] = featured_image
        
        # Type-specific additions
        if page_type == 'Course':
            schema["provider"] = {
                "@type": "Organization",
                "name": site_name,
                "url": f"https://{domain}"
            }
            
            if logo_url:
                schema["provider"]["logo"] = logo_url
            
            # Add address if available
            if address_data.get('full_address'):
                schema["provider"]["address"] = {
                    "@type": "PostalAddress"
                }
                if address_data.get('street'):
                    schema["provider"]["address"]["streetAddress"] = address_data['street']
                if address_data.get('locality'):
                    schema["provider"]["address"]["addressLocality"] = address_data['locality']
                if address_data.get('country'):
                    schema["provider"]["address"]["addressCountry"] = address_data['country']
                elif address_data.get('full_address'):
                    schema["provider"]["address"]["streetAddress"] = address_data['full_address']
            
            # Add Google Maps
            if maps_url:
                schema["provider"]["hasMap"] = maps_url
        
        elif page_type == 'Article':
            schema["@type"] = "Article"
            schema["headline"] = title
            schema["author"] = {
                "@type": "Organization",
                "name": site_name
            }
            schema["publisher"] = {
                "@type": "Organization",
                "name": site_name,
                "url": f"https://{domain}"
            }
            
            if logo_url:
                schema["publisher"]["logo"] = {
                    "@type": "ImageObject",
                    "url": logo_url
                }
            
            schema["datePublished"] = datetime.now().strftime('%Y-%m-%d')
            
        elif page_type == 'Product':
            schema["@type"] = "Product"
            schema["brand"] = {
                "@type": "Brand",
                "name": site_name
            }
            if featured_image:
                schema["image"] = featured_image
            schema["offers"] = {
                "@type": "Offer",
                "availability": "https://schema.org/InStock",
                "url": url
            }
        
        elif page_type == 'Organization':
            schema["@type"] = "Organization"
            if logo_url:
                schema["logo"] = logo_url
            
            if address_data.get('full_address'):
                schema["address"] = {
                    "@type": "PostalAddress"
                }
                if address_data.get('street'):
                    schema["address"]["streetAddress"] = address_data['street']
                if address_data.get('locality'):
                    schema["address"]["addressLocality"] = address_data['locality']
                if address_data.get('country'):
                    schema["address"]["addressCountry"] = address_data['country']
                elif address_data.get('full_address'):
                    schema["address"]["streetAddress"] = address_data['full_address']
            
            if maps_url:
                schema["hasMap"] = maps_url
        
        return schema
    
    def _analyze_page_speed(self, url):
        """
        Analyze page speed for both desktop and mobile
        
        Returns:
            Dictionary with speed metrics
        """
        print(f"  📊 Testing page speed...")
        
        speed_data = {
            'desktop': {},
            'mobile': {},
            'average_load_time': 0,
            'performance_rating': 'N/A'
        }
        
        try:
            # Desktop Speed Test
            desktop_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            start_time = perf_counter()
            response_desktop = requests.get(url, headers=desktop_headers, timeout=15)
            desktop_load_time = perf_counter() - start_time
            
            speed_data['desktop'] = {
                'load_time': round(desktop_load_time, 2),
                'size_kb': round(len(response_desktop.content) / 1024, 2),
                'status_code': response_desktop.status_code
            }
            
            # Mobile Speed Test
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
            }
            
            start_time = perf_counter()
            response_mobile = requests.get(url, headers=mobile_headers, timeout=15)
            mobile_load_time = perf_counter() - start_time
            
            speed_data['mobile'] = {
                'load_time': round(mobile_load_time, 2),
                'size_kb': round(len(response_mobile.content) / 1024, 2),
                'status_code': response_mobile.status_code
            }
            
            # Calculate average
            avg_time = (desktop_load_time + mobile_load_time) / 2
            speed_data['average_load_time'] = round(avg_time, 2)
            
            # Performance rating
            if avg_time < 1:
                speed_data['performance_rating'] = 'عالی'
                speed_data['performance_score'] = 95
            elif avg_time < 2:
                speed_data['performance_rating'] = 'خوب'
                speed_data['performance_score'] = 75
            elif avg_time < 3:
                speed_data['performance_rating'] = 'متوسط'
                speed_data['performance_score'] = 50
            elif avg_time < 5:
                speed_data['performance_rating'] = 'ضعیف'
                speed_data['performance_score'] = 30
            else:
                speed_data['performance_rating'] = 'خیلی ضعیف'
                speed_data['performance_score'] = 10
            
            print(f"    ⚡ Desktop: {speed_data['desktop']['load_time']}s")
            print(f"    📱 Mobile: {speed_data['mobile']['load_time']}s")
            print(f"    📊 Rating: {speed_data['performance_rating']}")
            
        except Exception as e:
            print(f"    ⚠️ Speed test error: {str(e)}")
            speed_data['error'] = str(e)
        
        return speed_data
    
    def _analyze_mobile_ux(self, soup, url):
        """
        Analyze Mobile UX and UI quality
        
        Returns:
            Dictionary with UX/UI metrics
        """
        print(f"  📱 Checking Mobile UX & UI...")
        
        ux_data = {
            'mobile_friendly': False,
            'responsive_design': False,
            'ui_quality': 'N/A',
            'ux_score': 0,
            'issues': [],
            'good_points': []
        }
        
        try:
            # 1. Check Viewport Meta Tag (Mobile-Friendly)
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            if viewport:
                ux_data['mobile_friendly'] = True
                ux_data['good_points'].append('✅ Viewport meta tag موجود است')
                ux_data['ux_score'] += 20
            else:
                ux_data['issues'].append('❌ Viewport meta tag ندارد')
            
            # 2. Check Responsive Design (Media Queries)
            has_media_queries = False
            styles = soup.find_all('style')
            for style in styles:
                if '@media' in style.get_text():
                    has_media_queries = True
                    break
            
            # Also check external stylesheets
            if not has_media_queries:
                links = soup.find_all('link', rel='stylesheet')
                if len(links) > 0:
                    has_media_queries = True  # Assume external CSS might have media queries
            
            if has_media_queries:
                ux_data['responsive_design'] = True
                ux_data['good_points'].append('✅ طراحی Responsive دارد')
                ux_data['ux_score'] += 20
            else:
                ux_data['issues'].append('⚠️ Media queries مشخص نیست')
            
            # 3. Font Size Analysis
            font_too_small = False
            body = soup.find('body')
            if body and body.get('style'):
                if 'font-size' in body.get('style'):
                    ux_data['good_points'].append('✅ Font size تنظیم شده')
                    ux_data['ux_score'] += 10
            
            # 4. Touch Targets (Button and Link sizes)
            buttons = soup.find_all(['button', 'a'])
            if len(buttons) > 0:
                ux_data['good_points'].append(f'✅ {len(buttons)} دکمه/لینک دارد')
                ux_data['ux_score'] += 10
            
            # 5. Images with Alt Text (Accessibility)
            images = soup.find_all('img')
            images_with_alt = sum(1 for img in images if img.get('alt'))
            if images:
                alt_percentage = (images_with_alt / len(images)) * 100
                if alt_percentage > 80:
                    ux_data['good_points'].append(f'✅ {int(alt_percentage)}% تصاویر Alt Text دارند')
                    ux_data['ux_score'] += 15
                elif alt_percentage > 50:
                    ux_data['issues'].append(f'⚠️ فقط {int(alt_percentage)}% تصاویر Alt Text دارند')
                    ux_data['ux_score'] += 7
                else:
                    ux_data['issues'].append(f'❌ فقط {int(alt_percentage)}% تصاویر Alt Text دارند')
            
            # 6. Form Elements (User Input)
            forms = soup.find_all('form')
            inputs = soup.find_all(['input', 'textarea', 'select'])
            if forms and inputs:
                ux_data['good_points'].append(f'✅ {len(forms)} فرم با {len(inputs)} فیلد')
                ux_data['ux_score'] += 10
            
            # 7. Navigation Menu
            nav = soup.find_all(['nav', 'menu'])
            if nav:
                ux_data['good_points'].append('✅ منوی Navigation دارد')
                ux_data['ux_score'] += 10
            else:
                ux_data['issues'].append('⚠️ منوی Navigation مشخص نیست')
            
            # 8. Content Readability
            paragraphs = soup.find_all('p')
            if len(paragraphs) > 0:
                ux_data['good_points'].append(f'✅ {len(paragraphs)} پاراگراف محتوا')
                ux_data['ux_score'] += 5
            
            # Calculate UI Quality Rating
            if ux_data['ux_score'] >= 80:
                ux_data['ui_quality'] = 'عالی'
            elif ux_data['ux_score'] >= 60:
                ux_data['ui_quality'] = 'خوب'
            elif ux_data['ux_score'] >= 40:
                ux_data['ui_quality'] = 'متوسط'
            elif ux_data['ux_score'] >= 20:
                ux_data['ui_quality'] = 'ضعیف'
            else:
                ux_data['ui_quality'] = 'خیلی ضعیف'
            
            print(f"    📱 Mobile-Friendly: {'✅' if ux_data['mobile_friendly'] else '❌'}")
            print(f"    🎨 UI Quality: {ux_data['ui_quality']}")
            print(f"    📊 UX Score: {ux_data['ux_score']}/100")
            
        except Exception as e:
            print(f"    ⚠️ UX analysis error: {str(e)}")
            ux_data['error'] = str(e)
        
        return ux_data
    
    def _extract_keywords(self, soup):
        """Extract SEO-relevant keywords from meta tags, headings, and important content"""
        keywords = {}
        
        # Persian and English stop words
        stop_words = {
            'است', 'های', 'برای', 'این', 'که', 'از', 'به', 'در', 'با', 'را', 'یا', 'هم', 'همه', 'یکی',
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'with', 'this', 'that', 'from', 'they', 'have', 'was',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'
        }
        
        # 1. Extract from title tag
        title_tag = soup.find('title')
        if title_tag:
            title_words = self._extract_meaningful_words(title_tag.get_text(), stop_words)
            for word in title_words:
                # Give higher weight to phrases (multi-word)
                weight = 15 if ' ' in word else 10
                keywords[word] = keywords.get(word, 0) + weight
        
        # 2. Extract from meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc_words = self._extract_meaningful_words(meta_desc.get('content'), stop_words)
            for word in desc_words:
                # Give higher weight to phrases (multi-word)
                weight = 12 if ' ' in word else 8
                keywords[word] = keywords.get(word, 0) + weight
        
        # 3. Extract from H1 tags
        h1_tags = soup.find_all('h1')
        for h1 in h1_tags:
            h1_words = self._extract_meaningful_words(h1.get_text(), stop_words)
            for word in h1_words:
                # Give higher weight to phrases (multi-word)
                weight = 10 if ' ' in word else 7
                keywords[word] = keywords.get(word, 0) + weight
        
        # 4. Extract from H2 tags
        h2_tags = soup.find_all('h2')
        for h2 in h2_tags:
            h2_words = self._extract_meaningful_words(h2.get_text(), stop_words)
            for word in h2_words:
                # Give higher weight to phrases (multi-word)
                weight = 7 if ' ' in word else 5
                keywords[word] = keywords.get(word, 0) + weight
        
        # 5. Extract from H3 tags
        h3_tags = soup.find_all('h3')
        for h3 in h3_tags:
            h3_words = self._extract_meaningful_words(h3.get_text(), stop_words)
            for word in h3_words:
                # Give higher weight to phrases (multi-word)
                weight = 5 if ' ' in word else 3
                keywords[word] = keywords.get(word, 0) + weight
        
        # 6. Extract from alt attributes of images
        img_tags = soup.find_all('img', alt=True)
        for img in img_tags:
            alt_words = self._extract_meaningful_words(img.get('alt'), stop_words)
            for word in alt_words:
                # Give higher weight to phrases (multi-word)
                weight = 6 if ' ' in word else 4
                keywords[word] = keywords.get(word, 0) + weight
        
        # 7. Extract from schema markup
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                import json
                schema_data = json.loads(script.string)
                schema_words = self._extract_from_schema(schema_data, stop_words)
                for word in schema_words:
                    # Give higher weight to phrases (multi-word)
                    weight = 8 if ' ' in word else 6
                    keywords[word] = keywords.get(word, 0) + weight
            except:
                continue
        
        # 8. Extract from footer links (often contain important keywords)
        footer = soup.find('footer')
        if footer:
            footer_links = footer.find_all('a')
            for link in footer_links:
                link_words = self._extract_meaningful_words(link.get_text(), stop_words)
                for word in link_words:
                    # Give higher weight to phrases (multi-word)
                    weight = 3 if ' ' in word else 2
                    keywords[word] = keywords.get(word, 0) + weight
        
        # Filter keywords: minimum 3 characters, not stop words, meaningful
        filtered_keywords = {}
        for word, weight in keywords.items():
            if (len(word) >= 3 and 
                word.lower() not in stop_words and 
                self._is_meaningful_keyword(word) and
                weight >= 3):  # Minimum weight threshold
                filtered_keywords[word] = weight
        
        # Return top keywords sorted by weight
        sorted_keywords = sorted(filtered_keywords.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_keywords[:25])  # Return top 25 keywords
    
    def classify_keywords(self, text_content, main_keyword=None):
        """
        Classify keywords into short-tail, medium-tail, and long-tail categories
        """
        print(f"\n🔍 Classifying keywords for: '{main_keyword}'")
        
        # Extract all keywords from text
        all_keywords = self._extract_all_keywords_from_text(text_content)
        
        # Classify keywords
        classified = {
            'short_tail': [],
            'medium_tail': [],
            'long_tail': [],
            'keyword_gap': []
        }
        
        for keyword, weight in all_keywords.items():
            word_count = len(keyword.split())
            
            if word_count == 1:
                classified['short_tail'].append({'keyword': keyword, 'weight': weight})
            elif word_count <= 4:
                classified['medium_tail'].append({'keyword': keyword, 'weight': weight})
            else:
                classified['long_tail'].append({'keyword': keyword, 'weight': weight})
        
        # Sort by weight
        for category in ['short_tail', 'medium_tail', 'long_tail']:
            classified[category].sort(key=lambda x: x['weight'], reverse=True)
            classified[category] = classified[category][:20]  # Top 20 per category
        
        return classified
    
    def semantic_keyword_analysis(self, main_keyword, article_text, competitor_keywords=None):
        """
        Advanced semantic keyword analysis with stemming and semantic family extraction
        """
        print(f"\n🎯 Semantic Keyword Analysis for: '{main_keyword}'")
        
        # Step 1: Semantic analysis of main keyword
        semantic_family = self._extract_semantic_family(main_keyword)
        print(f"🔍 Semantic family: {semantic_family}")
        
        # Step 2: Tokenize and analyze article text
        all_phrases = self._extract_all_phrases_from_text(article_text)
        
        # Step 3: Calculate semantic similarity for each phrase
        scored_phrases = []
        for phrase in all_phrases:
            similarity_score = self._calculate_semantic_similarity(phrase, main_keyword, semantic_family)
            if similarity_score >= 0.7:  # High similarity threshold
                scored_phrases.append({
                    'phrase': phrase,
                    'similarity': similarity_score,
                    'frequency': all_phrases.count(phrase)
                })
        
        # Step 4: Classify by phrase length
        classified = {
            'semantic_family': semantic_family,
            'short_tail': [],
            'medium_tail': [],
            'long_tail': [],
            'keyword_gap': []
        }
        
        for item in scored_phrases:
            phrase = item['phrase']
            word_count = len(phrase.split())
            weight = item['similarity'] * item['frequency']
            
            if word_count <= 2:
                classified['short_tail'].append({
                    'keyword': phrase,
                    'weight': weight,
                    'similarity': item['similarity']
                })
            elif word_count <= 4:
                classified['medium_tail'].append({
                    'keyword': phrase,
                    'weight': weight,
                    'similarity': item['similarity']
                })
            else:
                classified['long_tail'].append({
                    'keyword': phrase,
                    'weight': weight,
                    'similarity': item['similarity']
                })
        
        # Step 5: Calculate keyword gap
        if competitor_keywords:
            classified['keyword_gap'] = self._calculate_keyword_gap(classified, competitor_keywords)
        
        # Sort by weight
        for category in ['short_tail', 'medium_tail', 'long_tail']:
            classified[category].sort(key=lambda x: x['weight'], reverse=True)
            classified[category] = classified[category][:20]  # Top 20 per category
        
        return classified
    
    def _extract_semantic_family(self, main_keyword):
        """Extract semantic family (related words) from main keyword"""
        semantic_family = set()
        
        # Add the main keyword itself
        semantic_family.add(main_keyword.lower())
        
        # Tokenize main keyword
        tokens = main_keyword.lower().split()
        semantic_family.update(tokens)
        
        # Define semantic relationships based on tokens
        for token in tokens:
            if token == 'کاشت':
                semantic_family.update(['پیوند', 'جراحی', 'عمل', 'تکنیک', 'روش', 'جدید', 'طبیعی', 'اصل', 'مصنوعی', 'کاشت مو', 'کاشت ریش', 'کاشت ابرو'])
            elif token == 'مو':
                semantic_family.update(['ریزش', 'درمان', 'مراقبت', 'نگهداری', 'محافظت', 'حفظ', 'ماندگاری', 'دوام', 'طول عمر', 'ریزش مو', 'درمان مو', 'مراقبت مو'])
            elif token == 'درمان':
                semantic_family.update(['ریزش', 'مو', 'کاشت', 'پیوند', 'جراحی', 'عمل', 'تکنیک', 'روش', 'دارو', 'قرص', 'کپسول', 'درمان ریزش مو', 'درمان مو'])
            elif token == 'ریزش':
                semantic_family.update(['مو', 'درمان', 'کاشت', 'پیوند', 'جراحی', 'عمل', 'تکنیک', 'روش', 'دارو', 'قرص', 'کپسول', 'ریزش مو', 'درمان ریزش مو'])
            elif token == 'کلینیک':
                semantic_family.update(['مرکز', 'بیمارستان', 'تخصصی', 'پزشک', 'دکتر', 'متخصص', 'جراح', 'آدرس', 'تلفن', 'تماس', 'کلینیک کاشت مو', 'مرکز کاشت مو'])
            elif token == 'هزینه':
                semantic_family.update(['قیمت', 'ارزان', 'گران', 'مقایسه', 'انتخاب', 'راهنمای', 'راهنما', 'نکات', 'توصیه', 'هزینه کاشت مو', 'قیمت کاشت مو'])
            elif token == 'قیمت':
                semantic_family.update(['هزینه', 'ارزان', 'گران', 'مقایسه', 'انتخاب', 'راهنمای', 'راهنما', 'نکات', 'توصیه', 'هزینه کاشت مو', 'قیمت کاشت مو'])
            elif token == 'نتایج':
                semantic_family.update(['نتیجه', 'بعد', 'قبل', 'تصاویر', 'نمونه', 'تجربه', 'موفقیت', 'شکست', 'مشکلات', 'نتایج کاشت مو', 'نتیجه کاشت'])
            elif token == 'مشاوره':
                semantic_family.update(['رایگان', 'نوبت', 'ویزیت', 'پزشک', 'متخصص', 'دکتر', 'جراح', 'تخصصی', 'مشاوره کاشت مو', 'مشاوره رایگان'])
            elif token == 'عوارض':
                semantic_family.update(['خطرات', 'مشکلات', 'جانبی', 'خطر', 'ایمنی', 'بی خطر', 'مطمئن', 'قابل اعتماد', 'عوارض کاشت مو', 'خطرات کاشت مو'])
            elif token == 'مراقبت':
                semantic_family.update(['نگهداری', 'محافظت', 'حفظ', 'ماندگاری', 'دوام', 'طول عمر', 'پایداری', 'مراقبت بعد کاشت', 'نگهداری کاشت مو'])
        
        return list(semantic_family)
    
    def _extract_all_phrases_from_text(self, article_text):
        """Extract all 1-6 word phrases from article text"""
        phrases = []
        
        # Persian and English stop words
        stop_words = {
            'است', 'های', 'برای', 'این', 'که', 'از', 'به', 'در', 'با', 'را', 'یا', 'هم', 'همه', 'یکی',
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'with', 'this', 'that', 'from', 'they', 'have', 'was',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'
        }
        
        # Combine all text content
        full_text = ""
        if isinstance(article_text, dict):
            for key, value in article_text.items():
                if isinstance(value, str):
                    full_text += " " + value
                elif isinstance(value, list):
                    full_text += " " + " ".join(value)
        else:
            full_text = str(article_text)
        
        # Clean text
        import re
        full_text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', full_text.lower())
        words = re.findall(r'\b[a-zA-Z\u0600-\u06FF]{2,}\b', full_text)
        
        # Filter stop words
        filtered_words = [word for word in words if word not in stop_words]
        
        # Extract phrases of different lengths
        for i in range(len(filtered_words)):
            # 1-word phrases
            if len(filtered_words[i]) >= 3:
                phrases.append(filtered_words[i])
            
            # 2-word phrases
            if i < len(filtered_words) - 1:
                phrase_2 = f"{filtered_words[i]} {filtered_words[i+1]}"
                phrases.append(phrase_2)
            
            # 3-word phrases
            if i < len(filtered_words) - 2:
                phrase_3 = f"{filtered_words[i]} {filtered_words[i+1]} {filtered_words[i+2]}"
                phrases.append(phrase_3)
            
            # 4-word phrases
            if i < len(filtered_words) - 3:
                phrase_4 = f"{filtered_words[i]} {filtered_words[i+1]} {filtered_words[i+2]} {filtered_words[i+3]}"
                phrases.append(phrase_4)
            
            # 5-word phrases
            if i < len(filtered_words) - 4:
                phrase_5 = f"{filtered_words[i]} {filtered_words[i+1]} {filtered_words[i+2]} {filtered_words[i+3]} {filtered_words[i+4]}"
                phrases.append(phrase_5)
            
            # 6-word phrases
            if i < len(filtered_words) - 5:
                phrase_6 = f"{filtered_words[i]} {filtered_words[i+1]} {filtered_words[i+2]} {filtered_words[i+3]} {filtered_words[i+4]} {filtered_words[i+5]}"
                phrases.append(phrase_6)
        
        return phrases
    
    def _calculate_semantic_similarity(self, phrase, main_keyword, semantic_family):
        """Calculate semantic similarity between phrase and main keyword"""
        similarity = 0.0
        
        # Direct match with main keyword
        if main_keyword.lower() in phrase.lower():
            similarity += 0.9
        
        # Match with semantic family
        phrase_words = phrase.lower().split()
        for word in phrase_words:
            if word in semantic_family:
                similarity += 0.3
        
        # Partial match with main keyword tokens
        main_tokens = main_keyword.lower().split()
        for token in main_tokens:
            if token in phrase.lower():
                similarity += 0.2
        
        # Normalize similarity (max 1.0)
        return min(similarity, 1.0)
    
    def _calculate_keyword_gap(self, classified, competitor_keywords):
        """Calculate keyword gap between current and competitor keywords"""
        gap = []
        
        # Get all current keywords
        current_keywords = set()
        for category in ['short_tail', 'medium_tail', 'long_tail']:
            for item in classified[category]:
                current_keywords.add(item['keyword'])
        
        # Find missing keywords
        for comp_keyword in competitor_keywords:
            if comp_keyword not in current_keywords:
                gap.append({
                    'keyword': comp_keyword,
                    'weight': 1.0,
                    'similarity': 0.5  # Default similarity for gap keywords
                })
        
        return gap[:15]  # Top 15 gap keywords
    
    def _extract_all_keywords_from_text(self, text_content):
        """Extract all keywords from text content with comprehensive analysis"""
        keywords = {}
        
        # Persian and English stop words
        stop_words = {
            'است', 'های', 'برای', 'این', 'که', 'از', 'به', 'در', 'با', 'را', 'یا', 'هم', 'همه', 'یکی',
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'with', 'this', 'that', 'from', 'they', 'have', 'was',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'
        }
        
        # Extract from different parts of content
        if 'title' in text_content:
            title_words = self._extract_meaningful_words(text_content['title'], stop_words)
            for word in title_words:
                weight = 15 if ' ' in word else 10
                keywords[word] = keywords.get(word, 0) + weight
        
        if 'meta_description' in text_content:
            desc_words = self._extract_meaningful_words(text_content['meta_description'], stop_words)
            for word in desc_words:
                weight = 12 if ' ' in word else 8
                keywords[word] = keywords.get(word, 0) + weight
        
        if 'h1_tags' in text_content:
            for h1 in text_content['h1_tags']:
                h1_words = self._extract_meaningful_words(h1, stop_words)
                for word in h1_words:
                    weight = 10 if ' ' in word else 7
                    keywords[word] = keywords.get(word, 0) + weight
        
        if 'h2_tags' in text_content:
            for h2 in text_content['h2_tags']:
                h2_words = self._extract_meaningful_words(h2, stop_words)
                for word in h2_words:
                    weight = 7 if ' ' in word else 5
                    keywords[word] = keywords.get(word, 0) + weight
        
        if 'h3_tags' in text_content:
            for h3 in text_content['h3_tags']:
                h3_words = self._extract_meaningful_words(h3, stop_words)
                for word in h3_words:
                    weight = 5 if ' ' in word else 3
                    keywords[word] = keywords.get(word, 0) + weight
        
        if 'body_content' in text_content:
            body_words = self._extract_meaningful_words(text_content['body_content'], stop_words)
            for word in body_words:
                weight = 3 if ' ' in word else 2
                keywords[word] = keywords.get(word, 0) + weight
        
        if 'alt_texts' in text_content:
            for alt in text_content['alt_texts']:
                alt_words = self._extract_meaningful_words(alt, stop_words)
                for word in alt_words:
                    weight = 4 if ' ' in word else 3
                    keywords[word] = keywords.get(word, 0) + weight
        
        # Filter keywords
        filtered_keywords = {}
        for word, weight in keywords.items():
            if (len(word) >= 3 and 
                word.lower() not in stop_words and 
                self._is_meaningful_keyword(word) and
                weight >= 2):
                filtered_keywords[word] = weight
        
        return filtered_keywords
    
    def _extract_meaningful_words(self, text, stop_words):
        """Extract meaningful words and phrases from text"""
        if not text:
            return []
        
        # Clean text
        text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text.lower())
        
        # Extract single words
        words = re.findall(r'\b[a-zA-Z\u0600-\u06FF]{3,}\b', text)
        filtered_words = [word for word in words if word.lower() not in stop_words]
        
        # Extract meaningful phrases (2-4 words)
        phrases = self._extract_meaningful_phrases(text, stop_words)
        
        # Combine words and phrases
        return filtered_words + phrases
    
    def _extract_meaningful_phrases(self, text, stop_words):
        """Extract meaningful phrases from text"""
        phrases = []
        
        # Define important phrase patterns for hair transplant context
        important_phrases = [
            'کاشت مو', 'درمان ریزش مو', 'پیوند مو', 'کاشت ریش', 'کاشت ابرو',
            'هزینه کاشت مو', 'قیمت کاشت مو', 'کاشت مو ارزان', 'کاشت مو گران',
            'نتایج کاشت مو', 'نتیجه کاشت', 'بعد از کاشت', 'قبل و بعد',
            'مشاوره کاشت مو', 'مشاوره رایگان', 'نوبت مشاوره', 'مشاوره تخصصی',
            'جراحی کاشت مو', 'عمل کاشت مو', 'کاشت مو جراحی', 'جراحی مو',
            'تکنیک کاشت مو', 'روش کاشت مو', 'کاشت مو جدید', 'تکنولوژی کاشت',
            'پزشک کاشت مو', 'دکتر کاشت مو', 'متخصص کاشت مو', 'جراح کاشت مو',
            'کلینیک کاشت مو', 'مرکز کاشت مو', 'بیمارستان کاشت مو', 'مرکز تخصصی',
            'عوارض کاشت مو', 'خطرات کاشت مو', 'مشکلات کاشت مو', 'عوارض جانبی',
            'مراقبت بعد کاشت', 'نگهداری کاشت مو', 'محافظت کاشت', 'مراقبت مو',
            'ماندگاری کاشت مو', 'دوام کاشت مو', 'طول عمر کاشت', 'پایداری کاشت',
            'کاشت مو طبیعی', 'کاشت طبیعی', 'مو طبیعی', 'کاشت مو اصل',
            'ریزش مو', 'درمان ریزش', 'ریزش مو درمان', 'درمان مو',
            'کلینیک کاشت', 'مرکز کاشت', 'بیمارستان کاشت', 'مرکز تخصصی کاشت',
            'هزینه کاشت', 'قیمت کاشت', 'کاشت ارزان', 'کاشت گران',
            'نتایج کاشت', 'نتیجه کاشت', 'بعد کاشت', 'قبل کاشت',
            'مشاوره کاشت', 'مشاوره رایگان کاشت', 'نوبت کاشت', 'مشاوره تخصصی کاشت',
            'جراحی کاشت', 'عمل کاشت', 'کاشت جراحی', 'جراحی',
            'تکنیک کاشت', 'روش کاشت', 'کاشت جدید', 'تکنولوژی',
            'پزشک کاشت', 'دکتر کاشت', 'متخصص کاشت', 'جراح کاشت',
            'عوارض کاشت', 'خطرات کاشت', 'مشکلات کاشت', 'عوارض',
            'مراقبت کاشت', 'نگهداری کاشت', 'محافظت', 'مراقبت',
            'ماندگاری کاشت', 'دوام کاشت', 'طول عمر', 'پایداری'
        ]
        
        # Check for each important phrase in the text
        for phrase in important_phrases:
            if phrase in text:
                # Count occurrences
                count = text.count(phrase)
                for _ in range(count):
                    phrases.append(phrase)
        
        # Also extract general 2-3 word phrases that don't contain stop words
        words = text.split()
        for i in range(len(words) - 1):
            # 2-word phrases
            phrase_2 = f"{words[i]} {words[i+1]}"
            if (len(words[i]) >= 3 and len(words[i+1]) >= 3 and 
                words[i] not in stop_words and words[i+1] not in stop_words):
                phrases.append(phrase_2)
            
            # 3-word phrases
            if i < len(words) - 2:
                phrase_3 = f"{words[i]} {words[i+1]} {words[i+2]}"
                if (len(words[i]) >= 3 and len(words[i+1]) >= 3 and len(words[i+2]) >= 3 and
                    words[i] not in stop_words and words[i+1] not in stop_words and words[i+2] not in stop_words):
                    phrases.append(phrase_3)
        
        return phrases
    
    def _extract_from_schema(self, schema_data, stop_words):
        """Extract keywords from schema markup"""
        words = []
        
        def extract_from_dict(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, str) and len(value) > 3:
                        if key in ['name', 'title', 'description', 'keywords']:
                            words.extend(self._extract_meaningful_words(value, stop_words))
                    elif isinstance(value, (dict, list)):
                        extract_from_dict(value)
            elif isinstance(data, list):
                for item in data:
                    extract_from_dict(item)
        
        extract_from_dict(schema_data)
        return words
    
    def _is_meaningful_keyword(self, word):
        """Check if a word is a meaningful keyword"""
        # Check if word contains only letters and is not too generic
        if not re.match(r'^[a-zA-Z\u0600-\u06FF]+$', word):
            return False
        
        # Persian meaningful keyword patterns
        persian_meaningful = [
            'کلینیک', 'پزشک', 'دکتر', 'درمان', 'جراحی', 'زیبایی', 'پوست', 'مو', 'کاشت', 'لیزر',
            'آموزش', 'میکروتیک', 'شبکه', 'امنیت', 'برنامه', 'نویسی', 'طراحی', 'وب', 'سایت',
            'خرید', 'فروش', 'قیمت', 'محصول', 'خدمات', 'شرکت', 'تولید', 'صنعت', 'تکنولوژی'
        ]
        
        # Check if word is in meaningful patterns
        for pattern in persian_meaningful:
            if pattern in word.lower():
                return True
        
        # Check English meaningful patterns
        english_meaningful = [
            'clinic', 'doctor', 'medical', 'health', 'beauty', 'skin', 'hair', 'treatment', 'surgery',
            'education', 'training', 'course', 'learning', 'technology', 'software', 'development',
            'business', 'service', 'product', 'company', 'industry', 'solution'
        ]
        
        for pattern in english_meaningful:
            if pattern in word.lower():
                return True
        
        # If word is longer than 5 characters and not generic, consider it meaningful
        return len(word) >= 5
    
    def _analyze_content_structure(self, soup):
        """Analyze the content structure"""
        return {
            'paragraphs': len(soup.find_all('p')),
            'lists': len(soup.find_all(['ul', 'ol'])),
            'tables': len(soup.find_all('table')),
            'videos': len(soup.find_all(['video', 'iframe'])),
            'forms': len(soup.find_all('form'))
        }
    
    def _track_keywords(self, text, keywords, total_words):
        """
        Track keyword occurrences and calculate density
        
        Args:
            text: Full text content (lowercase)
            keywords: List of keywords to track
            total_words: Total word count
            
        Returns:
            Dictionary with keyword tracking data
        """
        tracking = {
            'total_words': total_words,
            'keywords': []
        }
        
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            count = text.count(keyword_lower)
            density = (count / total_words * 100) if total_words > 0 else 0
            
            tracking['keywords'].append({
                'keyword': keyword.strip(),
                'count': count,
                'density': round(density, 2),
                'status': self._get_keyword_status(density)
            })
        
        return tracking
    
    def _get_keyword_status(self, density):
        """Get keyword density status"""
        if density == 0:
            return 'missing'
        elif density < 0.5:
            return 'low'
        elif density <= 2.5:
            return 'good'
        else:
            return 'high'
    
    def compare_competitors(self, competitor_urls, keywords=None, my_site_url=None):
        """
        Compare multiple competitors
        
        Args:
            competitor_urls: List of URLs to analyze
            keywords: List of keywords to track (optional)
            my_site_url: URL of the user's site for gap analysis (optional)
        """
        print("\n" + "="*60)
        print("🏆 COMPETITOR COMPARISON ANALYSIS")
        print("="*60)
        
        competitors_data = []
        
        for url in competitor_urls:
            analysis = self.analyze_competitor(url, keywords=keywords)
            if analysis:
                competitors_data.append(analysis)
            time.sleep(2)  # Be polite to servers
        
        # Calculate averages
        if competitors_data:
            avg_data = self._calculate_averages(competitors_data)
            competitors_data.append(avg_data)
        
        # Generate content gaps and keyword gaps
        content_gaps = self._generate_content_gaps(competitors_data)
        keyword_gaps = self._generate_keyword_gaps(competitors_data, my_site_url)
        
        # Create result structure
        result = {
            'competitors': competitors_data,
            'summary': {
                'total_analyzed': len([c for c in competitors_data if c.get('url') != '📊 AVERAGE']),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'average': avg_data if competitors_data else {},
            'content_gaps': content_gaps,
            'keyword_gaps': keyword_gaps,
            'recommendations': self._generate_competitor_recommendations(competitors_data)
        }
        
        return result
    
    def _calculate_averages(self, data):
        """Calculate average metrics from competitor data"""
        return {
            'url': '📊 AVERAGE',
            'word_count': int(sum(d['word_count'] for d in data) / len(data)),
            'images_count': int(sum(d['images_count'] for d in data) / len(data)),
            'h1_count': int(sum(len(d['h1_tags']) for d in data) / len(data)),
            'h2_count': int(sum(len(d['h2_tags']) for d in data) / len(data)),
            'h3_count': int(sum(len(d['h3_tags']) for d in data) / len(data)),
            'internal_links': int(sum(d['internal_links'] for d in data) / len(data)),
            'external_links': int(sum(d['external_links'] for d in data) / len(data)),
        }
    
    def _generate_content_gaps(self, competitors_data):
        """Generate content gaps based on competitor analysis"""
        gaps = []
        
        # Analyze common topics in H2 tags
        all_h2_tags = []
        for comp in competitors_data:
            if comp.get('url') != '📊 AVERAGE':
                all_h2_tags.extend(comp.get('h2_tags', []))
        
        # Find most common topics
        from collections import Counter
        h2_counter = Counter(all_h2_tags)
        common_topics = h2_counter.most_common(10)
        
        for topic, count in common_topics:
            if count >= 2:  # Topic appears in at least 2 competitors
                # Find which competitors have this topic
                competitor_sites = []
                for comp in competitors_data:
                    if comp.get('url') != '📊 AVERAGE' and topic in comp.get('h2_tags', []):
                        competitor_sites.append(comp.get('url', ''))
                
                gaps.append({
                    'topic': topic,
                    'description': f'موضوع "{topic}" در {count} رقیب استفاده شده است',
                    'competitors': competitor_sites,
                    'priority': 'high' if count >= 3 else 'medium',
                    'total_weight': count
                })
        
        return gaps[:8]  # Return top 8 gaps
    
    def _generate_keyword_gaps(self, competitors_data, my_site_url=None):
        """Generate keyword gaps based on competitor analysis compared to user's site"""
        if not my_site_url:
            # Fallback to old behavior if no user site provided
            return self._generate_keyword_gaps_fallback(competitors_data)
        
        # Analyze user's site
        print(f"🔍 Analyzing user's site: {my_site_url}")
        try:
            user_site_analysis = self.analyze_competitor(my_site_url)
            if not user_site_analysis:
                print(f"❌ Failed to analyze user's site: {my_site_url}")
                return []
            
            print(f"✅ User's site analyzed successfully. Found {len(user_site_analysis.get('keywords_found', {}))} keywords")
        except Exception as e:
            print(f"❌ Error analyzing user's site: {str(e)}")
            return []
        
        user_keywords = user_site_analysis.get('keywords_found', {})
        user_word_count = user_site_analysis.get('word_count', 1)
        
        # Collect all keywords from competitors with details
        keyword_details = {}
        
        for comp in competitors_data:
            if comp.get('url') != '📊 AVERAGE':
                keywords = comp.get('keywords_found', {})
                comp_url = comp.get('url', 'Unknown')
                comp_word_count = comp.get('word_count', 1)
                
                for keyword, count in keywords.items():
                    if keyword not in keyword_details:
                        keyword_details[keyword] = {
                            'total_frequency': 0,
                            'total_weight': 0,
                            'sites': [],
                            'competitor_density': 0,
                            'user_density': 0,
                            'gap_type': 'missing',  # missing, low_density, high_density
                            'gap_score': 0
                        }
                    
                    keyword_details[keyword]['total_frequency'] += count
                    keyword_details[keyword]['sites'].append({
                        'url': comp_url,
                        'count': count,
                        'weight': count,
                        'density': (count / comp_word_count * 100) if comp_word_count > 0 else 0
                    })
                    keyword_details[keyword]['total_weight'] += count
                    keyword_details[keyword]['competitor_density'] += (count / comp_word_count * 100) if comp_word_count > 0 else 0
        
        # Calculate gaps for each keyword
        keyword_gaps = []
        for keyword, details in keyword_details.items():
            # Calculate user's keyword density
            user_count = user_keywords.get(keyword, 0)
            user_density = (user_count / user_word_count * 100) if user_word_count > 0 else 0
            
            # Calculate average competitor density
            competitor_density = details['competitor_density'] / len(details['sites']) if details['sites'] else 0
            
            # Determine gap type and score
            gap_type = 'missing'
            gap_score = 0
            
            if user_count == 0:
                gap_type = 'missing'
                gap_score = competitor_density * 10  # High priority for missing keywords
            elif user_density < competitor_density * 0.5:
                gap_type = 'low_density'
                gap_score = (competitor_density - user_density) * 5  # Medium priority
            elif user_density < competitor_density * 0.8:
                gap_type = 'medium_density'
                gap_score = (competitor_density - user_density) * 2  # Lower priority
            else:
                continue  # Skip keywords where user is competitive
            
            details['user_density'] = user_density
            details['gap_type'] = gap_type
            details['gap_score'] = gap_score
            
            keyword_gaps.append((keyword, details))
        
        # Sort by gap score (highest gaps first)
        keyword_gaps.sort(key=lambda x: x[1]['gap_score'], reverse=True)
        
        return keyword_gaps[:25]  # Return top 25 keyword gaps
    
    def _generate_keyword_gaps_fallback(self, competitors_data):
        """Fallback method when no user site is provided"""
        keyword_details = {}
        
        for comp in competitors_data:
            if comp.get('url') != '📊 AVERAGE':
                keywords = comp.get('keywords_found', {})
                comp_url = comp.get('url', 'Unknown')
                
                for keyword, count in keywords.items():
                    if keyword not in keyword_details:
                        keyword_details[keyword] = {
                            'total_frequency': 0,
                            'sites': [],
                            'total_weight': 0,
                            'competitor_density': 0,
                            'user_density': 0,
                            'gap_type': 'general',
                            'gap_score': 0
                        }
                    
                    keyword_details[keyword]['total_frequency'] += count
                    keyword_details[keyword]['sites'].append({
                        'url': comp_url,
                        'count': count,
                        'weight': count
                    })
                    keyword_details[keyword]['total_weight'] += count
        
        sorted_keywords = sorted(keyword_details.items(), key=lambda x: x[1]['total_weight'], reverse=True)
        return sorted_keywords[:25]
    
    def _generate_competitor_recommendations(self, competitors_data):
        """Generate recommendations based on competitor analysis"""
        recommendations = []
        
        if not competitors_data:
            return recommendations
        
        # Calculate averages (excluding the average row)
        real_competitors = [c for c in competitors_data if c.get('url') != '📊 AVERAGE']
        if not real_competitors:
            return recommendations
        
        avg_word_count = sum(c.get('word_count', 0) for c in real_competitors) / len(real_competitors)
        avg_h2_count = sum(len(c.get('h2_tags', [])) for c in real_competitors) / len(real_competitors)
        avg_images = sum(c.get('images_count', 0) for c in real_competitors) / len(real_competitors)
        
        # Generate recommendations
        if avg_word_count > 0:
            recommendations.append(f"حداقل {int(avg_word_count)} کلمه محتوا بنویسید")
        
        if avg_h2_count > 0:
            recommendations.append(f"حداقل {int(avg_h2_count)} عنوان H2 استفاده کنید")
        
        if avg_images > 0:
            recommendations.append(f"حداقل {int(avg_images)} تصویر اضافه کنید")
        
        return recommendations
    
    # ==================== Keyword Research ====================
    
    def keyword_analysis(self, keyword, competitors_data):
        """
        Analyze keyword usage across competitors
        """
        print(f"\n🔑 Keyword Analysis: '{keyword}'")
        
        keyword_lower = keyword.lower()
        results = []
        
        for comp in competitors_data:
            if comp['url'] == '📊 AVERAGE':
                continue
                
            # Count keyword in title
            title = comp.get('title', '')
            title_count = title.lower().count(keyword_lower) if title else 0
            
            # Count keyword in meta description
            meta_description = comp.get('meta_description', '')
            meta_count = meta_description.lower().count(keyword_lower) if meta_description else 0
            
            # Count keyword in H1 tags
            h1_tags = comp.get('h1_tags', [])
            h1_count = sum(keyword_lower in h1.lower() for h1 in h1_tags) if h1_tags else 0
            
            # Count keyword in H2 tags
            h2_tags = comp.get('h2_tags', [])
            h2_count = sum(keyword_lower in h2.lower() for h2 in h2_tags) if h2_tags else 0
            
            # Check if keyword in keywords_found
            keywords_found = comp.get('keywords_found', {})
            keyword_density = keywords_found.get(keyword_lower, 0) if keywords_found else 0
            
            results.append({
                'url': comp.get('url', ''),
                'title': title,
                'in_title': title_count > 0,
                'in_meta': meta_count > 0,
                'in_h1': h1_count > 0,
                'h1_count': h1_count,
                'h2_count': h2_count,
                'total_mentions': keyword_density
            })
        
        return results
    
    def suggest_related_keywords(self, base_keyword, competitors_data):
        """
        Suggest related keywords based on competitor analysis
        """
        print(f"\n💡 Suggesting related keywords for: '{base_keyword}'")
        
        all_keywords = []
        
        for comp in competitors_data:
            if comp['url'] == '📊 AVERAGE':
                continue
            all_keywords.extend(comp['keywords_found'].keys())
        
        # Count frequency across all competitors
        keyword_counter = Counter(all_keywords)
        
        # Filter related keywords (this is basic, can be improved)
        related = []
        base_words = set(base_keyword.lower().split())
        
        for keyword, count in keyword_counter.most_common(50):
            # If any word from base_keyword is in this keyword
            keyword_words = set(keyword.split())
            if keyword_words.intersection(base_words):
                related.append({'keyword': keyword, 'frequency': count})
        
        return related[:20]
    
    # ==================== Content Gap Analysis ====================
    
    def content_gap_analysis(self, my_url, competitor_urls, main_keyword=None):
        """
        Find content gaps between your site and competitors
        """
        print("\n" + "="*60)
        print("🔍 CONTENT GAP ANALYSIS")
        print("="*60)
        
        if main_keyword:
            print(f"🎯 Main keyword: '{main_keyword}'")
        
        # Analyze your site
        print("\n📌 Analyzing your website...")
        my_data = self.analyze_competitor(my_url)
        
        if not my_data:
            print("❌ Could not analyze your website")
            return None
        
        # Analyze competitors
        print("\n📌 Analyzing competitors...")
        competitors_data = []
        for url in competitor_urls:
            data = self.analyze_competitor(url)
            if data:
                competitors_data.append(data)
            time.sleep(2)
        
        # Find gaps
        gaps = {
            'keyword_gaps': self._find_keyword_gaps(my_data, competitors_data, main_keyword),
            'content_length_gap': self._find_content_length_gap(my_data, competitors_data),
            'structure_gaps': self._find_structure_gaps(my_data, competitors_data),
            'technical_gaps': self._find_technical_gaps(my_data, competitors_data),
            'recommendations': []
        }
        
        # Generate recommendations
        gaps['recommendations'] = self._generate_recommendations(my_data, competitors_data, gaps)
        
        return gaps
    
    def _find_keyword_gaps(self, my_data, competitors_data, main_keyword=None):
        """Find keywords competitors use but you don't (with advanced semantic analysis)"""
        print(f"\n🔍 Finding keyword gaps for: '{main_keyword}'")
        
        # Prepare text content for my site
        my_text_content = self._prepare_text_content(my_data)
        
        # Use advanced semantic analysis for my site
        my_semantic_analysis = self.semantic_keyword_analysis(main_keyword, my_text_content)
        
        # Collect competitor keywords
        competitor_keywords = set()
        for comp in competitors_data:
            comp_text_content = self._prepare_text_content(comp)
            comp_semantic_analysis = self.semantic_keyword_analysis(main_keyword, comp_text_content)
            
            # Add competitor keywords to set
            for category in ['short_tail', 'medium_tail', 'long_tail']:
                for item in comp_semantic_analysis[category]:
                    competitor_keywords.add(item['keyword'])
        
        # Calculate keyword gap using semantic analysis
        my_semantic_analysis['keyword_gap'] = self._calculate_keyword_gap(my_semantic_analysis, list(competitor_keywords))
        
        # Convert to the expected format
        all_gaps = {}
        
        # Add keyword gap items
        for gap_item in my_semantic_analysis['keyword_gap']:
            keyword = gap_item['keyword']
            weight = gap_item['weight']
            all_gaps[keyword] = weight
        
        # Add semantic gaps from previous analysis
        semantic_gaps = self._find_semantic_keyword_gaps(my_data, competitors_data, main_keyword)
        for keyword, score in semantic_gaps.items():
            all_gaps[keyword] = all_gaps.get(keyword, 0) + score
        
        # Add advanced semantic gaps
        advanced_semantic_gaps = self._analyze_semantic_context(my_data, competitors_data, main_keyword)
        for keyword, score in advanced_semantic_gaps.items():
            all_gaps[keyword] = all_gaps.get(keyword, 0) + score
        
        # Sort by frequency/score
        sorted_keywords = sorted(all_gaps.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_keywords[:30]
    
    def _prepare_text_content(self, data):
        """Prepare text content from analysis data"""
        return {
            'title': data.get('title', ''),
            'meta_description': data.get('meta_description', ''),
            'h1_tags': data.get('h1_tags', []),
            'h2_tags': data.get('h2_tags', []),
            'h3_tags': data.get('h3_tags', []),
            'body_content': data.get('full_content', ''),
            'alt_texts': [img.get('alt', '') for img in data.get('images', []) if img.get('alt')]
        }
    
    def _find_category_gaps(self, my_keywords, competitor_classified, category):
        """Find gaps in a specific keyword category"""
        gaps = []
        
        # Get all competitor keywords in this category
        competitor_keywords = set()
        for comp in competitor_classified:
            for kw in comp[category]:
                competitor_keywords.add(kw['keyword'])
        
        # Get my keywords in this category
        my_keywords_set = set(kw['keyword'] for kw in my_keywords)
        
        # Find missing keywords
        missing_keywords = competitor_keywords - my_keywords_set
        
        # Calculate weights for missing keywords
        for keyword in missing_keywords:
            total_weight = 0
            for comp in competitor_classified:
                for kw in comp[category]:
                    if kw['keyword'] == keyword:
                        total_weight += kw['weight']
            
            if total_weight > 0:
                gaps.append({'keyword': keyword, 'weight': total_weight})
        
        # Sort by weight
        gaps.sort(key=lambda x: x['weight'], reverse=True)
        
        return gaps[:15]  # Top 15 gaps per category
    
    def _find_semantic_keyword_gaps(self, my_data, competitors_data, main_keyword=None):
        """Find semantic keyword gaps using contextual analysis based on main keyword"""
        semantic_gaps = {}
        
        # Tokenize main keyword if provided
        main_tokens = []
        if main_keyword:
            main_tokens = main_keyword.lower().split()
            print(f"🔍 Main keyword tokens: {main_tokens}")
        
        # Get all competitor keywords
        all_competitor_keywords = set()
        for comp in competitors_data:
            all_competitor_keywords.update(comp['keywords_found'].keys())
        
        # Get all my keywords
        my_keywords = set(my_data['keywords_found'].keys())
        
        # Define semantic relationships based on main keyword tokens
        if main_tokens:
            # Create dynamic semantic groups based on main keyword
            semantic_groups = self._create_semantic_groups_from_tokens(main_tokens)
        else:
            # Fallback to predefined groups
            semantic_groups = {
                'کاشت مو': {
                    'primary': ['کاشت', 'مو', 'کاشت مو'],
                    'related': ['پیوند', 'ریزش', 'درمان', 'کلینیک', 'جراحی', 'تکنیک', 'روش', 'هزینه', 'قیمت', 'نتایج', 'قبل', 'بعد', 'تصاویر', 'نمونه', 'تجربه', 'مشاوره', 'رایگان', 'نوبت', 'ویزیت', 'پزشک', 'متخصص', 'دکتر', 'جراح', 'کلینیک', 'مرکز', 'بیمارستان', 'آدرس', 'تلفن', 'تماس', 'ساعات', 'کار', 'خدمات', 'کیفیت', 'بهترین', 'ارزان', 'گران', 'مقایسه', 'انتخاب', 'راهنمای', 'راهنما', 'نکات', 'توصیه', 'مزایا', 'معایب', 'عوارض', 'خطرات', 'فواید', 'مزیت', 'مشکلات', 'حل', 'راه حل', 'جواب', 'پاسخ', 'سوال', 'سوالات', 'پرسش', 'پرسش و پاسخ', 'faq', 'سوالات متداول', 'راهنمای کامل', 'گام به گام', 'مراحل', 'فرآیند', 'زمان', 'مدت', 'دوره', 'ریکاوری', 'بهبود', 'نتیجه', 'موفقیت', 'شکست', 'مشکلات', 'عوارض جانبی', 'عوارض', 'خطر', 'خطرات', 'ایمنی', 'بی خطر', 'مطمئن', 'قابل اعتماد', 'تضمین', 'گارانتی', 'پشتیبانی', 'خدمات پس از فروش', 'مراقبت', 'نگهداری', 'محافظت', 'حفظ', 'ماندگاری', 'دوام', 'طول عمر', 'عمر', 'زندگی', 'طبیعی', 'مصنوعی', 'اصل', 'کپی', 'تقلید', 'شبیه', 'مشابه', 'متفاوت', 'فرق', 'تفاوت', 'مقایسه', 'برتری', 'برتر', 'بهتر', 'بهترین', 'عالی', 'خوب', 'بد', 'ضعیف', 'قوی', 'محکم', 'سست', 'محکم', 'قوی', 'ضعیف', 'سست', 'محکم', 'قوی', 'ضعیف', 'سست']
                }
            }
        
        # Analyze semantic relationships
        for group_name, group_data in semantic_groups.items():
            primary_words = group_data['primary']
            related_words = group_data['related']
            
            # Check if any primary word exists in my content
            my_has_primary = any(word in ' '.join(my_keywords) for word in primary_words)
            
            if my_has_primary:
                # If I have primary words, look for related words in competitors that I don't have
                for comp in competitors_data:
                    for keyword in comp['keywords_found'].keys():
                        # Check if this keyword contains any related word
                        for related_word in related_words:
                            if related_word in keyword and keyword not in my_keywords:
                                # Calculate semantic score based on relevance
                                score = comp['keywords_found'][keyword] * 0.7  # Weight semantic matches lower
                                semantic_gaps[keyword] = semantic_gaps.get(keyword, 0) + score
        
        return semantic_gaps
    
    def _create_semantic_groups_from_tokens(self, main_tokens):
        """Create semantic groups dynamically based on main keyword tokens"""
        semantic_groups = {}
        
        # Create a group name from tokens
        group_name = ' '.join(main_tokens)
        
        # Define related words based on tokens
        related_words = []
        
        # For each token, add related words
        for token in main_tokens:
            if token == 'کاشت':
                related_words.extend(['پیوند', 'جراحی', 'عمل', 'تکنیک', 'روش', 'جدید', 'طبیعی', 'اصل', 'مصنوعی'])
            elif token == 'مو':
                related_words.extend(['ریزش', 'درمان', 'مراقبت', 'نگهداری', 'محافظت', 'حفظ', 'ماندگاری', 'دوام', 'طول عمر'])
            elif token == 'درمان':
                related_words.extend(['ریزش', 'مو', 'کاشت', 'پیوند', 'جراحی', 'عمل', 'تکنیک', 'روش', 'دارو', 'قرص', 'کپسول'])
            elif token == 'ریزش':
                related_words.extend(['مو', 'درمان', 'کاشت', 'پیوند', 'جراحی', 'عمل', 'تکنیک', 'روش', 'دارو', 'قرص', 'کپسول'])
            elif token == 'کلینیک':
                related_words.extend(['مرکز', 'بیمارستان', 'تخصصی', 'پزشک', 'دکتر', 'متخصص', 'جراح', 'آدرس', 'تلفن', 'تماس'])
            elif token == 'هزینه':
                related_words.extend(['قیمت', 'ارزان', 'گران', 'مقایسه', 'انتخاب', 'راهنمای', 'راهنما', 'نکات', 'توصیه'])
            elif token == 'قیمت':
                related_words.extend(['هزینه', 'ارزان', 'گران', 'مقایسه', 'انتخاب', 'راهنمای', 'راهنما', 'نکات', 'توصیه'])
            elif token == 'نتایج':
                related_words.extend(['نتیجه', 'بعد', 'قبل', 'تصاویر', 'نمونه', 'تجربه', 'موفقیت', 'شکست', 'مشکلات'])
            elif token == 'مشاوره':
                related_words.extend(['رایگان', 'نوبت', 'ویزیت', 'پزشک', 'متخصص', 'دکتر', 'جراح', 'تخصصی'])
            elif token == 'عوارض':
                related_words.extend(['خطرات', 'مشکلات', 'جانبی', 'خطر', 'ایمنی', 'بی خطر', 'مطمئن', 'قابل اعتماد'])
            elif token == 'مراقبت':
                related_words.extend(['نگهداری', 'محافظت', 'حفظ', 'ماندگاری', 'دوام', 'طول عمر', 'پایداری'])
        
        # Add common related words
        related_words.extend([
            'کیفیت', 'بهترین', 'ارزان', 'گران', 'مقایسه', 'انتخاب', 'راهنمای', 'راهنما', 'نکات', 'توصیه',
            'مزایا', 'معایب', 'فواید', 'مزیت', 'مشکلات', 'حل', 'راه حل', 'جواب', 'پاسخ', 'سوال', 'سوالات',
            'پرسش', 'پرسش و پاسخ', 'faq', 'سوالات متداول', 'راهنمای کامل', 'گام به گام', 'مراحل', 'فرآیند',
            'زمان', 'مدت', 'دوره', 'ریکاوری', 'بهبود', 'نتیجه', 'موفقیت', 'شکست', 'مشکلات', 'عوارض جانبی',
            'عوارض', 'خطر', 'خطرات', 'ایمنی', 'بی خطر', 'مطمئن', 'قابل اعتماد', 'تضمین', 'گارانتی',
            'پشتیبانی', 'خدمات پس از فروش', 'مراقبت', 'نگهداری', 'محافظت', 'حفظ', 'ماندگاری', 'دوام',
            'طول عمر', 'عمر', 'زندگی', 'طبیعی', 'مصنوعی', 'اصل', 'کپی', 'تقلید', 'شبیه', 'مشابه',
            'متفاوت', 'فرق', 'تفاوت', 'مقایسه', 'برتری', 'برتر', 'بهتر', 'بهترین', 'عالی', 'خوب',
            'بد', 'ضعیف', 'قوی', 'محکم', 'سست'
        ])
        
        # Remove duplicates
        related_words = list(set(related_words))
        
        semantic_groups[group_name] = {
            'primary': main_tokens + [group_name],
            'related': related_words
        }
        
        print(f"🔍 Created semantic group for '{group_name}' with {len(related_words)} related words")
        
        return semantic_groups
    
    def _analyze_semantic_context(self, my_data, competitors_data, main_keyword=None):
        """Advanced semantic analysis using full text content"""
        semantic_gaps = {}
        
        # Get full text content from my site
        my_full_text = ""
        if 'full_content' in my_data:
            my_full_text = my_data['full_content'].lower()
        
        # Analyze each competitor
        for comp in competitors_data:
            comp_full_text = ""
            if 'full_content' in comp:
                comp_full_text = comp['full_content'].lower()
            
            # Look for semantic patterns in competitor content
            semantic_patterns = self._extract_semantic_patterns(comp_full_text, my_full_text, main_keyword)
            
            for pattern, score in semantic_patterns.items():
                semantic_gaps[pattern] = semantic_gaps.get(pattern, 0) + score
        
        return semantic_gaps
    
    def _extract_semantic_patterns(self, comp_text, my_text, main_keyword=None):
        """Extract semantic patterns from competitor text that are missing in my text"""
        patterns = {}
        
        # Create dynamic patterns based on main keyword
        if main_keyword:
            main_tokens = main_keyword.lower().split()
            semantic_patterns = self._create_dynamic_patterns(main_tokens)
        else:
            # Fallback to predefined patterns
            semantic_patterns = {
                'درمان ریزش مو': ['درمان ریزش مو', 'درمان ریزش', 'ریزش مو درمان', 'درمان مو'],
                'کاشت مو طبیعی': ['کاشت مو طبیعی', 'کاشت طبیعی', 'مو طبیعی', 'کاشت مو اصل'],
                'هزینه کاشت مو': ['هزینه کاشت مو', 'قیمت کاشت مو', 'کاشت مو ارزان', 'کاشت مو گران'],
                'نتایج کاشت مو': ['نتایج کاشت مو', 'نتیجه کاشت', 'بعد از کاشت', 'قبل و بعد'],
                'مشاوره کاشت مو': ['مشاوره کاشت مو', 'مشاوره رایگان', 'نوبت مشاوره', 'مشاوره تخصصی'],
                'جراحی کاشت مو': ['جراحی کاشت مو', 'عمل کاشت مو', 'کاشت مو جراحی', 'جراحی مو'],
                'تکنیک کاشت مو': ['تکنیک کاشت مو', 'روش کاشت مو', 'کاشت مو جدید', 'تکنولوژی کاشت'],
                'پزشک کاشت مو': ['پزشک کاشت مو', 'دکتر کاشت مو', 'متخصص کاشت مو', 'جراح کاشت مو'],
                'کلینیک کاشت مو': ['کلینیک کاشت مو', 'مرکز کاشت مو', 'بیمارستان کاشت مو', 'مرکز تخصصی'],
                'عوارض کاشت مو': ['عوارض کاشت مو', 'خطرات کاشت مو', 'مشکلات کاشت مو', 'عوارض جانبی'],
                'مراقبت بعد کاشت': ['مراقبت بعد کاشت', 'نگهداری کاشت مو', 'محافظت کاشت', 'مراقبت مو'],
                'ماندگاری کاشت مو': ['ماندگاری کاشت مو', 'دوام کاشت مو', 'طول عمر کاشت', 'پایداری کاشت']
            }
        
        for pattern_name, variations in semantic_patterns.items():
            # Check if competitor has this pattern
            comp_has_pattern = any(variation in comp_text for variation in variations)
            
            # Check if my site has this pattern
            my_has_pattern = any(variation in my_text for variation in variations)
            
            # If competitor has it but I don't, it's a gap
            if comp_has_pattern and not my_has_pattern:
                # Count occurrences in competitor text
                count = sum(comp_text.count(variation) for variation in variations)
                patterns[pattern_name] = count * 0.8  # Weight semantic patterns
        
        return patterns
    
    def _create_dynamic_patterns(self, main_tokens):
        """Create dynamic semantic patterns based on main keyword tokens"""
        patterns = {}
        
        # Create patterns based on token combinations
        for i, token in enumerate(main_tokens):
            # Single token patterns
            if token == 'کاشت':
                patterns['کاشت مو'] = ['کاشت مو', 'کاشت', 'پیوند مو', 'جراحی مو']
                patterns['کاشت مو طبیعی'] = ['کاشت مو طبیعی', 'کاشت طبیعی', 'مو طبیعی', 'کاشت مو اصل']
                patterns['هزینه کاشت مو'] = ['هزینه کاشت مو', 'قیمت کاشت مو', 'کاشت مو ارزان', 'کاشت مو گران']
                patterns['نتایج کاشت مو'] = ['نتایج کاشت مو', 'نتیجه کاشت', 'بعد از کاشت', 'قبل و بعد']
                patterns['مشاوره کاشت مو'] = ['مشاوره کاشت مو', 'مشاوره رایگان', 'نوبت مشاوره', 'مشاوره تخصصی']
                patterns['جراحی کاشت مو'] = ['جراحی کاشت مو', 'عمل کاشت مو', 'کاشت مو جراحی', 'جراحی مو']
                patterns['تکنیک کاشت مو'] = ['تکنیک کاشت مو', 'روش کاشت مو', 'کاشت مو جدید', 'تکنولوژی کاشت']
                patterns['پزشک کاشت مو'] = ['پزشک کاشت مو', 'دکتر کاشت مو', 'متخصص کاشت مو', 'جراح کاشت مو']
                patterns['کلینیک کاشت مو'] = ['کلینیک کاشت مو', 'مرکز کاشت مو', 'بیمارستان کاشت مو', 'مرکز تخصصی']
                patterns['عوارض کاشت مو'] = ['عوارض کاشت مو', 'خطرات کاشت مو', 'مشکلات کاشت مو', 'عوارض جانبی']
                patterns['مراقبت بعد کاشت'] = ['مراقبت بعد کاشت', 'نگهداری کاشت مو', 'محافظت کاشت', 'مراقبت مو']
                patterns['ماندگاری کاشت مو'] = ['ماندگاری کاشت مو', 'دوام کاشت مو', 'طول عمر کاشت', 'پایداری کاشت']
            
            elif token == 'مو':
                patterns['درمان ریزش مو'] = ['درمان ریزش مو', 'درمان ریزش', 'ریزش مو درمان', 'درمان مو']
                patterns['ریزش مو'] = ['ریزش مو', 'ریزش', 'مو ریزش', 'ریزش موی']
                patterns['مراقبت مو'] = ['مراقبت مو', 'نگهداری مو', 'محافظت مو', 'حفظ مو']
                patterns['ماندگاری مو'] = ['ماندگاری مو', 'دوام مو', 'طول عمر مو', 'پایداری مو']
            
            elif token == 'درمان':
                patterns['درمان ریزش مو'] = ['درمان ریزش مو', 'درمان ریزش', 'ریزش مو درمان', 'درمان مو']
                patterns['درمان طبیعی'] = ['درمان طبیعی', 'درمان گیاهی', 'درمان خانگی', 'درمان سنتی']
                patterns['درمان دارویی'] = ['درمان دارویی', 'درمان شیمیایی', 'درمان پزشکی', 'درمان تخصصی']
            
            elif token == 'ریزش':
                patterns['ریزش مو'] = ['ریزش مو', 'ریزش', 'مو ریزش', 'ریزش موی']
                patterns['درمان ریزش مو'] = ['درمان ریزش مو', 'درمان ریزش', 'ریزش مو درمان', 'درمان مو']
                patterns['علل ریزش مو'] = ['علل ریزش مو', 'دلایل ریزش مو', 'علت ریزش مو', 'سبب ریزش مو']
        
        return patterns
    
    def _find_content_length_gap(self, my_data, competitors_data):
        """Compare content length"""
        avg_competitor_words = sum(c['word_count'] for c in competitors_data) / len(competitors_data)
        my_words = my_data['word_count']
        
        return {
            'my_word_count': my_words,
            'avg_competitor_words': int(avg_competitor_words),
            'gap': int(avg_competitor_words - my_words),
            'percentage_difference': round(((avg_competitor_words - my_words) / avg_competitor_words * 100), 2) if avg_competitor_words > 0 else 0
        }
    
    def _find_structure_gaps(self, my_data, competitors_data):
        """Compare content structure"""
        avg_h2 = sum(len(c['h2_tags']) for c in competitors_data) / len(competitors_data)
        avg_h3 = sum(len(c['h3_tags']) for c in competitors_data) / len(competitors_data)
        avg_images = sum(c['images_count'] for c in competitors_data) / len(competitors_data)
        
        return {
            'h2_tags': {
                'yours': len(my_data['h2_tags']),
                'avg_competitors': round(avg_h2, 1),
                'gap': round(avg_h2 - len(my_data['h2_tags']), 1)
            },
            'h3_tags': {
                'yours': len(my_data['h3_tags']),
                'avg_competitors': round(avg_h3, 1),
                'gap': round(avg_h3 - len(my_data['h3_tags']), 1)
            },
            'images': {
                'yours': my_data['images_count'],
                'avg_competitors': round(avg_images, 1),
                'gap': round(avg_images - my_data['images_count'], 1)
            }
        }
    
    def _find_technical_gaps(self, my_data, competitors_data):
        """Compare technical aspects"""
        competitors_with_schema = sum(1 for c in competitors_data if c['has_schema'])
        
        return {
            'schema_markup': {
                'yours': bool(my_data['has_schema']),
                'competitors_percentage': round(competitors_with_schema / len(competitors_data) * 100, 1)
            },
            'images_without_alt': {
                'yours': my_data['images_without_alt'],
                'issue': my_data['images_without_alt'] > 0
            }
        }
    
    def _generate_recommendations(self, my_data, competitors_data, gaps):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Content length
        if gaps['content_length_gap']['gap'] > 0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Content',
                'issue': f"Your content is {gaps['content_length_gap']['gap']} words shorter than competitors",
                'action': f"Increase content length to at least {gaps['content_length_gap']['avg_competitor_words']} words"
            })
        
        # Headings
        if gaps['structure_gaps']['h2_tags']['gap'] > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Structure',
                'issue': f"You have {gaps['structure_gaps']['h2_tags']['gap']} fewer H2 tags than competitors",
                'action': f"Add more H2 headings (target: {int(gaps['structure_gaps']['h2_tags']['avg_competitors'])})"
            })
        
        # Images
        if gaps['structure_gaps']['images']['gap'] > 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Media',
                'issue': f"You have {gaps['structure_gaps']['images']['gap']} fewer images than competitors",
                'action': f"Add more relevant images (target: {int(gaps['structure_gaps']['images']['avg_competitors'])})"
            })
        
        # Schema
        if not gaps['technical_gaps']['schema_markup']['yours']:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Technical SEO',
                'issue': "No Schema markup detected",
                'action': "Add structured data (Schema.org) to your page"
            })
        
        # Alt text
        if gaps['technical_gaps']['images_without_alt']['issue']:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Accessibility',
                'issue': f"{my_data['images_without_alt']} images without alt text",
                'action': "Add descriptive alt text to all images"
            })
        
        # Keywords
        if gaps['keyword_gaps']:
            top_missing = [k[0] for k in gaps['keyword_gaps'][:5]]
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Keywords',
                'issue': "Missing important keywords used by competitors",
                'action': f"Consider adding these keywords: {', '.join(top_missing[:3])}"
            })
        
        return recommendations
    
    # ==================== Google Trends (Simplified) ====================
    
    def check_keyword_trends(self, keywords):
        """
        Note: For real Google Trends data, use pytrends library
        This is a simplified version
        """
        print("\n📈 Keyword Trends Analysis")
        print("Note: Install 'pytrends' library for real Google Trends data")
        print("pip install pytrends")
        
        # Placeholder for trends data
        trends_data = []
        for keyword in keywords:
            trends_data.append({
                'keyword': keyword,
                'note': 'Use pytrends library for real-time trend data',
                'suggestion': f'Research "{keyword}" on Google Trends manually'
            })
        
        return trends_data
    
    # ==================== Export Functions ====================
    
    def export_to_json(self, data, filename):
        """Export data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Data exported to: {filename}")
    
    def export_to_csv(self, data, filename):
        """Export competitor comparison to CSV"""
        if not data:
            print("No data to export")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if isinstance(data, list) and len(data) > 0:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        print(f"\n✅ Data exported to: {filename}")
    
    def generate_report(self, analysis_data, filename='seo_report.txt'):
        """Generate a comprehensive text report"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("SEO ANALYSIS REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
            
            # Write analysis data
            f.write(json.dumps(analysis_data, ensure_ascii=False, indent=2))
        
        print(f"\n✅ Report generated: {filename}")
    
    # ==================== Utility Functions ====================
    
    def print_competitor_summary(self, competitor_data):
        """Print a nice summary of competitor analysis"""
        print("\n" + "="*70)
        print("📊 COMPETITOR ANALYSIS SUMMARY")
        print("="*70)
        
        for comp in competitor_data:
            print(f"\n🌐 URL: {comp['url']}")
            print(f"   Title: {comp.get('title', 'N/A')[:60]}...")
            print(f"   Word Count: {comp.get('word_count', 0)}")
            print(f"   H1: {len(comp.get('h1_tags', []))}, H2: {len(comp.get('h2_tags', []))}, H3: {len(comp.get('h3_tags', []))}")
            print(f"   Images: {comp.get('images_count', 0)} (Alt missing: {comp.get('images_without_alt', 0)})")
            print(f"   Links: {comp.get('internal_links', 0)} internal, {comp.get('external_links', 0)} external")
            print(f"   Schema: {comp.get('has_schema', False)}")
    
    def print_content_gaps(self, gaps):
        """Print content gap analysis results"""
        if not gaps:
            return
        
        print("\n" + "="*70)
        print("🎯 CONTENT GAP ANALYSIS RESULTS")
        print("="*70)
        
        # Content length
        print("\n📝 Content Length:")
        print(f"   Your words: {gaps['content_length_gap']['my_word_count']}")
        print(f"   Competitor avg: {gaps['content_length_gap']['avg_competitor_words']}")
        print(f"   Gap: {gaps['content_length_gap']['gap']} words ({gaps['content_length_gap']['percentage_difference']}%)")
        
        # Structure
        print("\n🏗️  Content Structure:")
        print(f"   H2 tags: {gaps['structure_gaps']['h2_tags']['yours']} (Competitor avg: {gaps['structure_gaps']['h2_tags']['avg_competitors']})")
        print(f"   H3 tags: {gaps['structure_gaps']['h3_tags']['yours']} (Competitor avg: {gaps['structure_gaps']['h3_tags']['avg_competitors']})")
        print(f"   Images: {gaps['structure_gaps']['images']['yours']} (Competitor avg: {gaps['structure_gaps']['images']['avg_competitors']})")
        
        # Keywords
        print("\n🔑 Missing Keywords (Top 10):")
        for keyword, freq in gaps['keyword_gaps'][:10]:
            print(f"   - {keyword} (mentioned {freq} times by competitors)")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(gaps['recommendations'], 1):
            print(f"\n   {i}. [{rec['priority']}] {rec['category']}")
            print(f"      Issue: {rec['issue']}")
            print(f"      Action: {rec['action']}")
    
    # ==================== Advanced Keyword Gap Analysis ====================
    
    def _fetch_page_text(self, url):
        """Fetch page content and return clean text"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.get_text(" ", strip=True)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def advanced_keyword_gap_analysis(self, query, your_url, competitor_urls, lang='fa', use_mock_serp=True):
        """
        Advanced keyword gap analysis using new pipeline.
        
        Args:
            query: Search query
            your_url: Your website URL
            competitor_urls: List of competitor URLs
            lang: Language ('fa' or 'en')
            use_mock_serp: Whether to use mock SERP data
            
        Returns:
            Complete analysis results with both keyword gap and competitor analysis
        """
        try:
            print(f"\n🚀 Starting Advanced Keyword Gap Analysis...")
            print(f"Query: {query}")
            print(f"Your URL: {your_url}")
            print(f"Competitors: {len(competitor_urls)} URLs")
            
            # Import the new pipeline
            from pipeline.keyword_gap_pipeline import run_keyword_gap
            
            # Fetch your page content
            print(f"\n📥 Fetching your page content...")
            your_content = self._fetch_page_text(your_url)
            if not your_content:
                raise Exception(f"Failed to fetch content from {your_url}")
            
            # Fetch competitor page contents
            print(f"\n📥 Fetching competitor contents...")
            competitor_contents = []
            for i, url in enumerate(competitor_urls):
                print(f"  [{i+1}/{len(competitor_urls)}] Fetching {url}...")
                content = self._fetch_page_text(url)
                if content:
                    competitor_contents.append(content)
                else:
                    print(f"  ⚠️ Failed to fetch {url}")
            
            if not competitor_contents:
                raise Exception("No competitor content could be fetched")
            
            print(f"\n✅ Fetched {len(competitor_contents)} competitor pages")
            
            # Run the keyword gap pipeline
            print(f"\n🔍 Running keyword gap analysis pipeline...")
            gap_results = run_keyword_gap(
                query=query,
                your_doc=your_content,
                competitor_docs=competitor_contents,
                lang=lang,
                use_mock_serp=use_mock_serp
            )
            
            # Also run traditional competitor analysis for comprehensive results
            print(f"\n📊 Running comprehensive competitor analysis...")
            try:
                competitor_results = self.compare_competitors(competitor_urls, [query], your_url)
                print(f"✅ Competitor analysis completed successfully")
            except Exception as e:
                print(f"⚠️ Competitor analysis failed: {str(e)}")
                competitor_results = {'competitors': [], 'summary': {}, 'error': str(e)}
            
            # Combine results
            combined_results = {
                **gap_results,  # Keyword gap analysis results
                'raw_results': competitor_results,  # Traditional competitor analysis
                'your_url': your_url,
                'competitor_urls': competitor_urls
            }
            
            print(f"\n✅ Advanced analysis complete!")
            return combined_results
            
        except Exception as e:
            print(f"\n❌ Error in advanced keyword gap analysis: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'query': query,
                'your_url': your_url,
                'competitor_urls': competitor_urls
            }

    def print_advanced_gap_results(self, results):
        """
        Print advanced keyword gap analysis results in a formatted way.
        
        Args:
            results: Results from advanced_keyword_gap_analysis
        """
        if results.get('status') == 'error':
            print(f"\n❌ Analysis failed: {results.get('error', 'Unknown error')}")
            return
            
        print("\n" + "="*80)
        print("📋 ADVANCED KEYWORD GAP ANALYSIS RESULTS")
        print("="*80)
        
        print(f"\n🔍 Query: {results.get('query', 'N/A')}")
        print(f"🔤 Canonical: {results.get('keyword_canonical', 'N/A')}")
        print(f"🎯 Intent: {results.get('intent', 'N/A')}")
        print(f"📊 SERP Strength: {results.get('serp_strength', 'N/A')}")
        print(f"⏱️ Duration: {results.get('duration_seconds', 'N/A')}s")
        
        # Gap terms
        gap_terms = results.get('gap_terms', [])
        if gap_terms:
            print(f"\n📈 Gap Terms: {len(gap_terms)}")
            print("\nTop 5 gaps:")
            for i, term in enumerate(gap_terms[:5]):
                print(f"{i+1}. {term.get('term', 'N/A')} (score: {term.get('score', 0):.3f})")
                suggestions = term.get('suggestions', [])
                if suggestions:
                    for suggestion in suggestions:
                        print(f"     • {suggestion}")
        
        # Missing entities
        missing_entities = results.get('missing_entities', {})
        if missing_entities:
            print(f"\n🏷️ Missing Entities:")
            for entity_type, entities in missing_entities.items():
                print(f"  • {entity_type}: {', '.join(entities)}")
        
        # Actions
        actions = results.get('actions', {})
        if actions:
            print(f"\n🎯 Recommended Actions:")
            for category, action_list in actions.items():
                if action_list:
                    print(f"\n✏️ {category.upper()}: ({len(action_list)} actions)")
                    for action in action_list[:3]:  # Show top 3
                        priority = action.get('priority', 'medium')
                        emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                        print(f"  {emoji} {action.get('action', 'N/A')}")
        
        print("\n" + "="*80)


# ==================== Main Program ====================

def main():
    """
    Main function to run the SEO analyzer
    """
    print("\n" + "="*70)
    print("🚀 SEO ANALYZER TOOL")
    print("="*70)
    
    analyzer = SEOAnalyzer()
    
    # Example 1: Analyze competitors
    print("\n📌 EXAMPLE 1: Competitor Analysis")
    print("-" * 70)
    
    competitor_urls = [
        'https://www.takbook.com/book/mtcna-mikrotik/',
        'https://www.modir-shabake.com/product/فیلم-فارسی-آموزشی-میکروتیک-mikrotik-mtcna/',
        'https://afratik.ir/product/کاملترین-آموزش-mtcna-میکروتیک-با-نسخه-7-سیتم/'
    ]
    
    competitors_data = analyzer.compare_competitors(competitor_urls)
    analyzer.print_competitor_summary(competitors_data)
    
    # Export to JSON
    analyzer.export_to_json(competitors_data, 'competitor_analysis.json')
    
    # Example 2: Keyword Analysis
    print("\n📌 EXAMPLE 2: Keyword Analysis")
    print("-" * 70)
    
    target_keyword = "آموزش MTCNA"
    keyword_results = analyzer.keyword_analysis(target_keyword, competitors_data)
    
    print(f"\n🔑 Keyword '{target_keyword}' usage:")
    for result in keyword_results:
        print(f"\n   URL: {result['url'][:50]}...")
        print(f"   In Title: {'✅' if result['in_title'] else '❌'}")
        print(f"   In Meta: {'✅' if result['in_meta'] else '❌'}")
        print(f"   In H1: {'✅' if result['in_h1'] else '❌'}")
        print(f"   Total mentions: {result['total_mentions']}")
    
    # Example 3: Related Keywords
    print("\n📌 EXAMPLE 3: Related Keywords Suggestion")
    print("-" * 70)
    
    related_keywords = analyzer.suggest_related_keywords("mtcna", competitors_data)
    print("\n💡 Suggested related keywords:")
    for kw in related_keywords[:15]:
        print(f"   - {kw['keyword']} (frequency: {kw['frequency']})")
    
    # Example 4: Content Gap Analysis
    print("\n📌 EXAMPLE 4: Content Gap Analysis")
    print("-" * 70)
    print("Note: This requires YOUR website URL to compare")
    
    # Uncomment and add your URL to run content gap analysis
    # my_url = 'https://your-website.com/your-mtcna-page'
    # gaps = analyzer.content_gap_analysis(my_url, competitor_urls)
    # if gaps:
    #     analyzer.print_content_gaps(gaps)
    #     analyzer.export_to_json(gaps, 'content_gaps.json')
    
    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE!")
    print("="*70)
    print("\nGenerated files:")
    print("  - competitor_analysis.json")
    print("\nTo perform content gap analysis, uncomment lines in main() and add your URL")


    def advanced_keyword_gap_analysis(self, query, your_url, competitor_urls, lang='fa', use_mock_serp=True):
        """
        Advanced keyword gap analysis using new pipeline.
        
        Args:
            query: Search query
            your_url: Your website URL
            competitor_urls: List of competitor URLs
            lang: Language ('fa' or 'en')
            use_mock_serp: Whether to use mock SERP data
            
        Returns:
            Complete analysis results with both keyword gap and competitor analysis
        """
        try:
            print(f"\n🚀 Starting Advanced Keyword Gap Analysis...")
            print(f"Query: {query}")
            print(f"Your URL: {your_url}")
            print(f"Competitors: {len(competitor_urls)} URLs")
            
            # Import the new pipeline
            from pipeline.keyword_gap_pipeline import run_keyword_gap
            
            # Fetch your page content
            print(f"\n📥 Fetching your page content...")
            your_content = self._fetch_page_text(your_url)
            if not your_content:
                raise Exception(f"Failed to fetch content from {your_url}")
            
            # Fetch competitor page contents
            print(f"\n📥 Fetching competitor contents...")
            competitor_contents = []
            for i, url in enumerate(competitor_urls):
                print(f"  [{i+1}/{len(competitor_urls)}] Fetching {url}...")
                content = self._fetch_page_text(url)
                if content:
                    competitor_contents.append(content)
                else:
                    print(f"  ⚠️ Failed to fetch {url}")
            
            if not competitor_contents:
                raise Exception("No competitor content could be fetched")
            
            print(f"\n✅ Fetched {len(competitor_contents)} competitor pages")
            
            # Run the keyword gap pipeline
            print(f"\n🔍 Running keyword gap analysis pipeline...")
            gap_results = run_keyword_gap(
                query=query,
                your_doc=your_content,
                competitor_docs=competitor_contents,
                lang=lang,
                use_mock_serp=use_mock_serp
            )
            
            # Also run traditional competitor analysis for comprehensive results
            print(f"\n📊 Running comprehensive competitor analysis...")
            try:
                competitor_results = self.compare_competitors(competitor_urls, [query], your_url)
                print(f"✅ Competitor analysis completed successfully")
            except Exception as e:
                print(f"⚠️ Competitor analysis failed: {str(e)}")
                competitor_results = {'competitors': [], 'summary': {}, 'error': str(e)}
            
            # Combine results
            combined_results = {
                **gap_results,  # Keyword gap analysis results
                'raw_results': competitor_results,  # Traditional competitor analysis
                'your_url': your_url,
                'competitor_urls': competitor_urls
            }
            
            print(f"\n✅ Advanced analysis complete!")
            return combined_results
            
        except Exception as e:
            print(f"\n❌ Error in advanced keyword gap analysis: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'query': query,
                'your_url': your_url,
                'competitor_urls': competitor_urls
            }

    def print_advanced_gap_results(self, results):
        """
        Print advanced keyword gap analysis results in a formatted way.
        
        Args:
            results: Results from advanced_keyword_gap_analysis
        """
        if results.get('status') == 'error':
            print(f"\n❌ Analysis failed: {results.get('error', 'Unknown error')}")
            return
            
        print("\n" + "="*80)
        print("📋 ADVANCED KEYWORD GAP ANALYSIS RESULTS")
        print("="*80)
        
        print(f"\n🔍 Query: {results.get('query', 'N/A')}")
        print(f"🔤 Canonical: {results.get('keyword_canonical', 'N/A')}")
        print(f"🎯 Intent: {results.get('intent', 'N/A')}")
        print(f"📊 SERP Strength: {results.get('serp_strength', 'N/A')}")
        print(f"⏱️ Duration: {results.get('duration_seconds', 'N/A')}s")
        
        # Gap terms
        gap_terms = results.get('gap_terms', [])
        if gap_terms:
            print(f"\n📈 Gap Terms: {len(gap_terms)}")
            print("\nTop 5 gaps:")
            for i, term in enumerate(gap_terms[:5]):
                print(f"{i+1}. {term.get('term', 'N/A')} (score: {term.get('score', 0):.3f})")
                suggestions = term.get('suggestions', [])
                if suggestions:
                    for suggestion in suggestions:
                        print(f"     • {suggestion}")
        
        # Missing entities
        missing_entities = results.get('missing_entities', {})
        if missing_entities:
            print(f"\n🏷️ Missing Entities:")
            for entity_type, entities in missing_entities.items():
                print(f"  • {entity_type}: {', '.join(entities)}")
        
        # Actions
        actions = results.get('actions', {})
        if actions:
            print(f"\n🎯 Recommended Actions:")
            for category, action_list in actions.items():
                if action_list:
                    print(f"\n✏️ {category.upper()}: ({len(action_list)} actions)")
                    for action in action_list[:3]:  # Show top 3
                        priority = action.get('priority', 'medium')
                        emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                        print(f"  {emoji} {action.get('action', 'N/A')}")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    main()

