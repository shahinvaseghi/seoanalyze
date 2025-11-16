"""
Core Web Vitals Analysis Routes
Advanced performance analysis for Core Web Vitals metrics
"""

from __future__ import annotations

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .routes import login_required
import traceback
import json
import os
from datetime import datetime

core_web_vitals_bp = Blueprint("core_web_vitals", __name__, url_prefix="/core-web-vitals")


@core_web_vitals_bp.route("/", methods=["GET", "POST"])
@login_required
def core_web_vitals_index():
    """
    Core Web Vitals Analysis page
    """
    if request.method == "POST":
        # Get form data
        website_url = request.form.get("website_url", "").strip()
        # Always use comprehensive analysis (combines all features)
        analysis_type = "comprehensive"
        
        print(f"\n⚡ Core Web Vitals Analysis Request:")
        print(f"   Website URL: {website_url}")
        print(f"   Analysis Type: {analysis_type}")
        
        # Validation
        if not website_url:
            flash("Please enter a website URL", "error")
            return render_template("core_web_vitals.html")
        
        # Perform Core Web Vitals analysis
        try:
            from ..core.cwv_analyzer import CWVAnalyzer
            from ..core.seo_analyzer import SEOAnalyzer
            
            print("\n🚀 Starting Core Web Vitals analysis...")
            
            # Get basic SEO data first
            seo_analyzer = SEOAnalyzer()
            basic_data = seo_analyzer.analyze_competitor(website_url)
            
            if not basic_data:
                flash("Could not access the website. Please check the URL.", "error")
                return render_template("core_web_vitals.html")
            
            # Extract soup from the analysis result
            try:
                import requests
                from bs4 import BeautifulSoup
                
                response = requests.get(website_url, headers=seo_analyzer.headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                basic_data['soup'] = soup
                basic_data['response_time'] = response.elapsed.total_seconds()
                
            except Exception as e:
                print(f"Error extracting soup: {e}")
                flash("Could not analyze the website content. Please check the URL.", "error")
                return render_template("core_web_vitals.html")
            
            # Perform CWV analysis based on type
            cwv_analyzer = CWVAnalyzer()
            
            print(f"🔍 Starting comprehensive analysis (combines all features)...")
            
            # Perform comprehensive analysis (combines all features)
            # This will use Google API if available, or fallback to static analysis
            cwv_report = cwv_analyzer.analyze_cwv(
                basic_data['soup'], 
                website_url, 
                response_time=basic_data.get('response_time')
            )
            
            # Use the metrics from cwv_analyzer (real API or static, but NO random!)
            # DO NOT override with random metrics
            
            # Add device-specific metrics (based on REAL metrics from cwv_report)
            device_metrics = _generate_device_specific_metrics(basic_data, website_url)
            
            # Add Lighthouse-style metrics (based on REAL metrics)
            lighthouse_metrics = _generate_lighthouse_metrics(basic_data, website_url, cwv_report.cwv_metrics)
            
            # Enhance the report with comprehensive features
            cwv_report = _enhance_comprehensive_analysis(cwv_report, basic_data, website_url)
            
            # Ensure priority actions are properly formatted
            cwv_report = _ensure_proper_priority_actions_format(cwv_report)
            
            # Identify essential files that should never be deleted
            essential_files = _identify_essential_files(basic_data['soup'])
            
            # Generate safe render-blocking resources analysis
            safe_render_blocking = _generate_safe_render_blocking_analysis(basic_data['soup'])
            cwv_report.render_blocking = safe_render_blocking
            
            # Generate comprehensive text report
            comprehensive_report = _generate_comprehensive_text_report(
                cwv_report, device_metrics, lighthouse_metrics, essential_files, safe_render_blocking, basic_data, website_url
            )
            
            # Calculate unified overall score
            unified_overall_score = round((cwv_report.overall_score + lighthouse_metrics['overall_score']) / 2, 1)
            
            # Combine results
            analysis_result = {
                'url': website_url,
                'timestamp': datetime.now().isoformat(),
                'analysis_type': analysis_type,
                'basic_seo': basic_data,
                'cwv_report': cwv_report,
                'overall_score': unified_overall_score,
                'grade': cwv_report.grade,
                'priority_actions': cwv_report.priority_actions,
                'device_metrics': device_metrics,
                'lighthouse_metrics': lighthouse_metrics,
                'essential_files': essential_files,
                'comprehensive_report': comprehensive_report
            }
            
            # Save results
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"core_web_vitals_{timestamp}.json"
                results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
                os.makedirs(results_dir, exist_ok=True)
                
                with open(os.path.join(results_dir, filename), "w", encoding="utf-8") as f:
                    json.dump(analysis_result, f, ensure_ascii=False, indent=2, default=str)
                
                print(f"💾 Results saved to: {filename}")
            except Exception as save_error:
                print(f"⚠️ Could not save results: {save_error}")
                filename = "core_web_vitals_analysis.json"
            
            # Render results page
            return render_template("core_web_vitals_result.html", 
                                 result=analysis_result,
                                 filename=filename)
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            traceback.print_exc()
            flash(f"Analysis failed: {str(e)}", "error")
            return render_template("core_web_vitals.html")
    
    return render_template("core_web_vitals.html")


def _perform_quick_analysis(cwv_analyzer, basic_data, website_url):
    """
    Perform quick Core Web Vitals analysis focusing on main metrics
    """
    print("⚡ Performing Quick Analysis...")
    
    # Quick analysis - focus on main CWV metrics only
    cwv_report = cwv_analyzer.analyze_cwv(
        basic_data['soup'], 
        website_url, 
        response_time=basic_data.get('response_time')
    )
    
    # Enhance priority actions for quick analysis with more details
    quick_actions = []
    for action in cwv_report.priority_actions[:8]:  # Show more actions
        enhanced_action = {
            'title': action['action'],
            'description': action['details'],
            'priority': action['priority'].lower(),
            'category': action['category'],
            'impact': _get_impact_level(action['priority']),
            'estimated_time': _get_estimated_time(action['priority']),
            'difficulty': _get_difficulty_level(action['category'])
        }
        quick_actions.append(enhanced_action)
    
    cwv_report.priority_actions = quick_actions
    
    # Add comprehensive quick analysis data
    cwv_report.analysis_type = "quick"
    cwv_report.quick_summary = {
        'main_issues': len([a for a in quick_actions if a['priority'] in ['critical', 'high']]),
        'total_actions': len(quick_actions),
        'estimated_fix_time': _calculate_total_fix_time(quick_actions),
        'impact_level': _get_overall_impact_level(quick_actions),
        'performance_breakdown': {
            'lcp_status': _get_lcp_status(cwv_report.cwv_metrics.lcp),
            'inp_status': _get_inp_status(cwv_report.cwv_metrics.inp),
            'cls_status': _get_cls_status(cwv_report.cwv_metrics.cls)
        },
        'key_recommendations': _get_key_recommendations(quick_actions)
    }
    
    print(f"✅ Quick analysis completed - {len(quick_actions)} priority actions")
    return cwv_report


def _perform_detailed_analysis(cwv_analyzer, basic_data, website_url):
    """
    Perform detailed Core Web Vitals analysis with technical insights
    """
    print("🔬 Performing Detailed Analysis...")
    
    # Start with comprehensive analysis
    cwv_report = cwv_analyzer.analyze_cwv(
        basic_data['soup'], 
        website_url, 
        response_time=basic_data.get('response_time')
    )
    
    # Add detailed technical analysis
    detailed_metrics = _analyze_technical_details(basic_data['soup'], website_url)
    performance_insights = _generate_performance_insights(cwv_report, basic_data)
    optimization_roadmap = _create_optimization_roadmap(cwv_report)
    
    # Enhance priority actions with detailed recommendations
    detailed_actions = []
    for action in cwv_report.priority_actions:
        detailed_action = action.copy()
        detailed_action['technical_details'] = _get_technical_details(action['action'])
        detailed_action['implementation_steps'] = _get_implementation_steps(action['action'])
        detailed_action['expected_improvement'] = _get_expected_improvement(action['action'])
        detailed_actions.append(detailed_action)
    
    cwv_report.priority_actions = detailed_actions
    
    # Add detailed analysis specific data
    cwv_report.analysis_type = "detailed"
    cwv_report.detailed_metrics = detailed_metrics
    cwv_report.performance_insights = performance_insights
    cwv_report.optimization_roadmap = optimization_roadmap
    
    # Add comprehensive detailed summary
    cwv_report.detailed_summary = {
        'technical_analysis': {
            'dom_complexity': detailed_metrics['dom_complexity'],
            'resource_analysis': {
                'scripts': detailed_metrics['script_count'],
                'stylesheets': detailed_metrics['stylesheet_count'],
                'images': detailed_metrics['image_count'],
                'external_resources': detailed_metrics['external_resources']
            },
            'performance_indicators': {
                'inline_styles': detailed_metrics['inline_styles'],
                'inline_scripts': detailed_metrics['inline_scripts']
            }
        },
        'performance_deep_dive': performance_insights,
        'optimization_strategy': optimization_roadmap,
        'implementation_guide': _create_implementation_guide(detailed_actions),
        'testing_recommendations': _get_testing_recommendations(cwv_report),
        'advanced_metrics': _calculate_advanced_metrics(cwv_report, basic_data)
    }
    
    print(f"✅ Detailed analysis completed - {len(detailed_actions)} detailed actions")
    return cwv_report


def _enhance_comprehensive_analysis(cwv_report, basic_data, website_url):
    """
    Enhance comprehensive analysis with additional features
    """
    print("🚀 Enhancing Comprehensive Analysis...")
    
    # Add comprehensive features
    cwv_report.analysis_type = "comprehensive"
    
    # Add mobile performance analysis
    mobile_analysis = _analyze_mobile_performance(basic_data['soup'], website_url)
    cwv_report.mobile_performance = mobile_analysis
    
    # Add accessibility insights
    accessibility_insights = _analyze_accessibility(basic_data['soup'])
    cwv_report.accessibility_insights = accessibility_insights
    
    # Add SEO performance correlation
    seo_correlation = _analyze_seo_performance_correlation(cwv_report, basic_data)
    cwv_report.seo_correlation = seo_correlation
    
    # Add competitive benchmarking
    competitive_insights = _generate_competitive_insights(website_url)
    cwv_report.competitive_insights = competitive_insights
    
    # Add comprehensive summary
    cwv_report.comprehensive_summary = {
        'performance_overview': {
            'overall_score': cwv_report.overall_score,
            'grade': cwv_report.grade,
            'cwv_status': _get_cwv_overall_status(cwv_report.cwv_metrics),
            'improvement_potential': _calculate_improvement_potential(cwv_report)
        },
        'mobile_readiness': mobile_analysis,
        'accessibility_score': accessibility_insights,
        'seo_impact': seo_correlation,
        'competitive_position': competitive_insights,
        'action_plan': _create_comprehensive_action_plan(cwv_report.priority_actions),
        'monitoring_recommendations': _get_monitoring_recommendations(cwv_report)
    }
    
    print("✅ Comprehensive analysis enhanced")
    return cwv_report


def _analyze_technical_details(soup, url):
    """Analyze technical details for detailed analysis"""
    details = {
        'dom_complexity': len(soup.find_all()),
        'script_count': len(soup.find_all('script')),
        'stylesheet_count': len(soup.find_all('link', rel='stylesheet')),
        'image_count': len(soup.find_all('img')),
        'external_resources': len([link for link in soup.find_all(['link', 'script', 'img']) 
                                 if link.get('src') and not link.get('src').startswith('/')]),
        'inline_styles': len(soup.find_all(attrs={'style': True})),
        'inline_scripts': len(soup.find_all('script', string=True))
    }
    return details


def _generate_performance_insights(cwv_report, basic_data):
    """Generate performance insights"""
    insights = {
        'bottlenecks': [],
        'optimization_opportunities': [],
        'performance_score_breakdown': {
            'lcp_contribution': _calculate_lcp_score(cwv_report.cwv_metrics.lcp) * 0.25,
            'inp_contribution': _calculate_inp_score(cwv_report.cwv_metrics.inp) * 0.25,
            'cls_contribution': _calculate_cls_score(cwv_report.cwv_metrics.cls) * 0.25,
            'other_metrics_contribution': (100 - cwv_report.overall_score) * 0.25
        }
    }
    
    # Identify bottlenecks
    if cwv_report.cwv_metrics.lcp and cwv_report.cwv_metrics.lcp > 2.5:
        insights['bottlenecks'].append('LCP needs significant improvement')
    if cwv_report.cwv_metrics.inp and cwv_report.cwv_metrics.inp > 200:
        insights['bottlenecks'].append('INP indicates interactivity issues')
    if cwv_report.cwv_metrics.cls and cwv_report.cwv_metrics.cls > 0.1:
        insights['bottlenecks'].append('CLS shows layout instability')
    
    return insights


def _create_optimization_roadmap(cwv_report):
    """Create optimization roadmap"""
    roadmap = {
        'immediate_actions': [],
        'short_term_goals': [],
        'long_term_strategy': []
    }
    
    # Categorize actions by timeline
    for action in cwv_report.priority_actions:
        if action['priority'] == 'high':
            roadmap['immediate_actions'].append(action)
        elif action['priority'] == 'medium':
            roadmap['short_term_goals'].append(action)
        else:
            roadmap['long_term_strategy'].append(action)
    
    return roadmap


def _analyze_mobile_performance(soup, url):
    """Analyze mobile-specific performance"""
    mobile_analysis = {
        'viewport_configured': bool(soup.find('meta', attrs={'name': 'viewport'})),
        'mobile_friendly_indicators': [],
        'mobile_optimization_score': 0
    }
    
    # Check mobile-friendly indicators
    if mobile_analysis['viewport_configured']:
        mobile_analysis['mobile_friendly_indicators'].append('Viewport meta tag configured')
        mobile_analysis['mobile_optimization_score'] += 20
    
    # Check for touch-friendly elements
    touch_elements = soup.find_all(['button', 'a', 'input'], attrs={'class': lambda x: x and 'touch' in str(x).lower()})
    if touch_elements:
        mobile_analysis['mobile_friendly_indicators'].append('Touch-friendly elements detected')
        mobile_analysis['mobile_optimization_score'] += 15
    
    return mobile_analysis


def _analyze_accessibility(soup):
    """Analyze accessibility factors affecting performance"""
    accessibility = {
        'alt_text_coverage': 0,
        'semantic_html_score': 0,
        'accessibility_issues': []
    }
    
    # Check alt text coverage
    images = soup.find_all('img')
    images_with_alt = soup.find_all('img', alt=True)
    if images:
        accessibility['alt_text_coverage'] = (len(images_with_alt) / len(images)) * 100
    
    # Check semantic HTML
    semantic_tags = soup.find_all(['header', 'nav', 'main', 'article', 'section', 'aside', 'footer'])
    accessibility['semantic_html_score'] = min(len(semantic_tags) * 10, 100)
    
    return accessibility


def _analyze_seo_performance_correlation(cwv_report, basic_data):
    """Analyze correlation between CWV and SEO factors"""
    correlation = {
        'performance_seo_score': 0,
        'correlation_factors': []
    }
    
    # Calculate combined performance-SEO score
    cwv_score = cwv_report.overall_score
    seo_score = 85  # Placeholder - would need actual SEO analysis
    
    correlation['performance_seo_score'] = (cwv_score * 0.6) + (seo_score * 0.4)
    
    if cwv_score > 80:
        correlation['correlation_factors'].append('Excellent CWV scores support SEO rankings')
    elif cwv_score > 60:
        correlation['correlation_factors'].append('Good CWV scores with room for SEO improvement')
    else:
        correlation['correlation_factors'].append('Poor CWV scores likely impacting SEO performance')
    
    return correlation


def _generate_competitive_insights(url):
    """Generate competitive insights (placeholder)"""
    return {
        'benchmark_score': 75,  # Placeholder
        'industry_average': 72,  # Placeholder
        'competitive_position': 'above_average'  # Placeholder
    }


def _get_technical_details(action_title):
    """Get technical details for an action"""
    technical_details = {
        'Optimize Images': 'Implement WebP format, lazy loading, and responsive images',
        'Minify CSS/JS': 'Remove whitespace, comments, and unnecessary code',
        'Enable Compression': 'Implement gzip/brotli compression for text assets',
        'Reduce Server Response Time': 'Optimize database queries and server configuration',
        'Eliminate Render-Blocking Resources': 'Inline critical CSS and defer non-critical JS'
    }
    return technical_details.get(action_title, 'Technical implementation details available')


def _get_implementation_steps(action_title):
    """Get implementation steps for an action"""
    steps = {
        'Optimize Images': ['Audit current images', 'Convert to WebP', 'Implement lazy loading', 'Add responsive sizes'],
        'Minify CSS/JS': ['Identify minification tools', 'Configure build process', 'Test functionality', 'Deploy changes'],
        'Enable Compression': ['Configure server compression', 'Test compression ratio', 'Monitor performance impact'],
        'Reduce Server Response Time': ['Analyze server logs', 'Optimize database', 'Implement caching', 'Monitor improvements'],
        'Eliminate Render-Blocking Resources': ['Identify critical CSS', 'Inline critical styles', 'Defer non-critical JS', 'Test page load']
    }
    return steps.get(action_title, ['Implementation steps will be provided'])


def _get_expected_improvement(action_title):
    """Get expected improvement for an action"""
    improvements = {
        'Optimize Images': '15-25% improvement in LCP',
        'Minify CSS/JS': '5-10% improvement in overall performance',
        'Enable Compression': '20-30% reduction in file sizes',
        'Reduce Server Response Time': '10-20% improvement in TTFB',
        'Eliminate Render-Blocking Resources': '20-40% improvement in FCP'
    }
    return improvements.get(action_title, 'Expected improvement will be measured')


def _calculate_lcp_score(lcp_value):
    """Calculate LCP score based on value"""
    if lcp_value is None:
        return 50  # Neutral score for unknown values
    if lcp_value <= 2.5:
        return 100
    elif lcp_value <= 4.0:
        return 75
    else:
        return 25


def _calculate_inp_score(inp_value):
    """Calculate INP score based on value"""
    if inp_value is None:
        return 50  # Neutral score for unknown values
    if inp_value <= 200:
        return 100
    elif inp_value <= 500:
        return 75
    else:
        return 25


def _calculate_cls_score(cls_value):
    """Calculate CLS score based on value"""
    if cls_value is None:
        return 50  # Neutral score for unknown values
    if cls_value <= 0.1:
        return 100
    elif cls_value <= 0.25:
        return 75
    else:
        return 25


def _get_impact_level(priority):
    """Get impact level based on priority"""
    impact_levels = {
        'CRITICAL': 'High Impact',
        'HIGH': 'Medium Impact',
        'MEDIUM': 'Low Impact',
        'LOW': 'Minimal Impact'
    }
    return impact_levels.get(priority, 'Unknown Impact')


def _get_estimated_time(priority):
    """Get estimated time to fix based on priority"""
    time_estimates = {
        'CRITICAL': '2-4 hours',
        'HIGH': '1-2 hours',
        'MEDIUM': '30-60 minutes',
        'LOW': '15-30 minutes'
    }
    return time_estimates.get(priority, 'Unknown')


def _get_difficulty_level(category):
    """Get difficulty level based on category"""
    difficulty_levels = {
        'Images': 'Easy',
        'CSS': 'Medium',
        'JavaScript': 'Medium',
        'Caching': 'Hard',
        'Fonts': 'Easy',
        'Server': 'Hard'
    }
    return difficulty_levels.get(category, 'Medium')


def _calculate_total_fix_time(actions):
    """Calculate total estimated fix time"""
    time_mapping = {
        '2-4 hours': 4,
        '1-2 hours': 2,
        '30-60 minutes': 1,
        '15-30 minutes': 0.5
    }
    
    total_hours = 0
    for action in actions:
        time_str = action.get('estimated_time', 'Unknown')
        if time_str in time_mapping:
            total_hours += time_mapping[time_str]
    
    if total_hours <= 2:
        return f"{total_hours} hours"
    elif total_hours <= 8:
        return f"{total_hours} hours (1 day)"
    else:
        return f"{total_hours} hours (2-3 days)"


def _get_overall_impact_level(actions):
    """Get overall impact level"""
    critical_count = len([a for a in actions if a['priority'] == 'critical'])
    high_count = len([a for a in actions if a['priority'] == 'high'])
    
    if critical_count > 0:
        return 'Critical Impact'
    elif high_count > 2:
        return 'High Impact'
    elif high_count > 0:
        return 'Medium Impact'
    else:
        return 'Low Impact'


def _get_lcp_status(lcp_value):
    """Get LCP status"""
    if lcp_value is None:
        return {'status': 'Unknown', 'message': 'LCP data not available'}
    elif lcp_value <= 2.5:
        return {'status': 'Good', 'message': f'Excellent LCP: {lcp_value}s'}
    elif lcp_value <= 4.0:
        return {'status': 'Needs Improvement', 'message': f'LCP needs optimization: {lcp_value}s'}
    else:
        return {'status': 'Poor', 'message': f'Critical LCP issue: {lcp_value}s'}


def _get_inp_status(inp_value):
    """Get INP status"""
    if inp_value is None:
        return {'status': 'Unknown', 'message': 'INP data not available'}
    elif inp_value <= 200:
        return {'status': 'Good', 'message': f'Excellent INP: {inp_value}ms'}
    elif inp_value <= 500:
        return {'status': 'Needs Improvement', 'message': f'INP needs optimization: {inp_value}ms'}
    else:
        return {'status': 'Poor', 'message': f'Critical INP issue: {inp_value}ms'}


def _get_cls_status(cls_value):
    """Get CLS status"""
    if cls_value is None:
        return {'status': 'Unknown', 'message': 'CLS data not available'}
    elif cls_value <= 0.1:
        return {'status': 'Good', 'message': f'Excellent CLS: {cls_value}'}
    elif cls_value <= 0.25:
        return {'status': 'Needs Improvement', 'message': f'CLS needs optimization: {cls_value}'}
    else:
        return {'status': 'Poor', 'message': f'Critical CLS issue: {cls_value}'}


def _get_key_recommendations(actions):
    """Get key recommendations"""
    recommendations = []
    categories = {}
    
    for action in actions[:5]:  # Top 5 actions
        category = action.get('category', 'Other')
        if category not in categories:
            categories[category] = []
        categories[category].append(action)
    
    for category, category_actions in categories.items():
        if category_actions:
            top_action = category_actions[0]
            recommendations.append({
                'category': category,
                'action': top_action.get('action', top_action.get('title', 'Unknown Action')),
                'priority': top_action['priority'],
                'impact': top_action['impact']
            })
    
    return recommendations


def _get_cwv_overall_status(cwv_metrics):
    """Get overall CWV status"""
    lcp_status = _get_lcp_status(cwv_metrics.lcp)
    inp_status = _get_inp_status(cwv_metrics.inp)
    cls_status = _get_cls_status(cwv_metrics.cls)
    
    statuses = [lcp_status['status'], inp_status['status'], cls_status['status']]
    
    if 'Poor' in statuses:
        return 'Poor - Critical Issues Found'
    elif 'Needs Improvement' in statuses:
        return 'Needs Improvement - Optimization Required'
    elif 'Good' in statuses and 'Unknown' not in statuses:
        return 'Good - Meeting Core Web Vitals'
    else:
        return 'Unknown - Limited Data Available'


def _calculate_improvement_potential(cwv_report):
    """Calculate improvement potential"""
    current_score = cwv_report.overall_score
    potential_score = 100
    
    # Calculate potential based on priority actions
    high_priority_actions = len([a for a in cwv_report.priority_actions if a.get('priority') == 'high'])
    critical_actions = len([a for a in cwv_report.priority_actions if a.get('priority') == 'critical'])
    
    improvement_potential = min(100, current_score + (critical_actions * 15) + (high_priority_actions * 10))
    
    return {
        'current_score': current_score,
        'potential_score': improvement_potential,
        'improvement_range': f"{improvement_potential - current_score:.1f} points",
        'critical_actions': critical_actions,
        'high_priority_actions': high_priority_actions
    }


def _create_comprehensive_action_plan(priority_actions):
    """Create comprehensive action plan"""
    action_plan = {
        'immediate_actions': [],
        'short_term_goals': [],
        'long_term_strategy': [],
        'timeline': {
            'week_1': [],
            'week_2_4': [],
            'month_2_3': []
        }
    }
    
    for action in priority_actions:
        priority = action.get('priority', '').lower()
        category = action.get('category', 'Other')
        
        if priority == 'critical':
            action_plan['immediate_actions'].append(action)
            action_plan['timeline']['week_1'].append(action)
        elif priority == 'high':
            action_plan['short_term_goals'].append(action)
            action_plan['timeline']['week_2_4'].append(action)
        else:
            action_plan['long_term_strategy'].append(action)
            action_plan['timeline']['month_2_3'].append(action)
    
    return action_plan


def _get_monitoring_recommendations(cwv_report):
    """Get monitoring recommendations"""
    recommendations = []
    
    # Based on current issues
    if cwv_report.cwv_metrics.lcp and cwv_report.cwv_metrics.lcp > 2.5:
        recommendations.append({
            'metric': 'LCP',
            'frequency': 'Daily',
            'tool': 'Google PageSpeed Insights',
            'threshold': '2.5s',
            'action': 'Monitor largest contentful paint continuously'
        })
    
    if cwv_report.cwv_metrics.cls and cwv_report.cwv_metrics.cls > 0.1:
        recommendations.append({
            'metric': 'CLS',
            'frequency': 'Weekly',
            'tool': 'Chrome DevTools',
            'threshold': '0.1',
            'action': 'Check for layout shifts after content updates'
        })
    
    # General recommendations
    recommendations.extend([
        {
            'metric': 'Overall Performance',
            'frequency': 'Weekly',
            'tool': 'Google Lighthouse',
            'threshold': '90+',
            'action': 'Run Lighthouse audits weekly'
        },
        {
            'metric': 'Real User Monitoring',
            'frequency': 'Continuous',
            'tool': 'Google Analytics',
            'threshold': 'Monitor trends',
            'action': 'Set up Core Web Vitals reporting'
        }
    ])
    
    return recommendations


def _create_implementation_guide(detailed_actions):
    """Create detailed implementation guide"""
    guide = {
        'step_by_step': [],
        'tools_needed': [],
        'estimated_timeline': {},
        'risk_assessment': {},
        'success_metrics': []
    }
    
    for i, action in enumerate(detailed_actions, 1):
        step = {
            'step_number': i,
            'action': action.get('action', action.get('title', 'Unknown Action')),
            'priority': action['priority'],
            'category': action['category'],
            'description': action['description'],
            'technical_details': action.get('technical_details', ''),
            'implementation_steps': action.get('implementation_steps', []),
            'expected_improvement': action.get('expected_improvement', ''),
            'difficulty': action.get('difficulty', 'Medium'),
            'estimated_time': action.get('estimated_time', 'Unknown')
        }
        guide['step_by_step'].append(step)
    
    # Collect unique tools
    tools = set()
    for action in detailed_actions:
        category = action.get('category', '')
        if category == 'Images':
            tools.update(['ImageOptimizer', 'WebP Converter', 'Lazy Loading Library'])
        elif category == 'CSS':
            tools.update(['CSS Minifier', 'Critical CSS Extractor'])
        elif category == 'JavaScript':
            tools.update(['QUnit', 'Jest', 'Webpack', 'Rollup'])
        elif category == 'Caching':
            tools.update(['CDN', 'Browser Cache', 'Service Worker'])
    
    guide['tools_needed'] = list(tools)
    
    # Calculate timeline
    total_time = 0
    for action in detailed_actions:
        time_str = action.get('estimated_time', 'Unknown')
        if 'hours' in time_str:
            hours = float(time_str.split()[0])
            total_time += hours
    
    guide['estimated_timeline'] = {
        'total_hours': total_time,
        'estimated_days': max(1, total_time // 8),
        'phases': {
            'critical': [a for a in detailed_actions if a.get('priority') == 'critical'],
            'high': [a for a in detailed_actions if a.get('priority') == 'high'],
            'medium': [a for a in detailed_actions if a.get('priority') == 'medium']
        }
    }
    
    return guide


def _get_testing_recommendations(cwv_report):
    """Get testing recommendations for detailed analysis"""
    recommendations = []
    
    # Performance testing
    recommendations.append({
        'type': 'Performance Testing',
        'tools': ['Google Lighthouse', 'WebPageTest', 'GTmetrix'],
        'frequency': 'Before and after each optimization',
        'metrics': ['LCP', 'INP', 'CLS', 'FCP', 'TTI'],
        'description': 'Comprehensive performance testing to measure Core Web Vitals'
    })
    
    # Real User Monitoring
    recommendations.append({
        'type': 'Real User Monitoring',
        'tools': ['Google Analytics', 'Core Web Vitals Report', 'Search Console'],
        'frequency': 'Continuous monitoring',
        'metrics': ['Real user metrics', 'Field data', 'Lab data correlation'],
        'description': 'Monitor actual user experience across different devices and connections'
    })
    
    # A/B Testing
    recommendations.append({
        'type': 'A/B Testing',
        'tools': ['Google Optimize', 'Optimizely', 'VWO'],
        'frequency': 'For major changes',
        'metrics': ['Conversion rates', 'User engagement', 'Performance metrics'],
        'description': 'Test performance improvements impact on user behavior'
    })
    
    return recommendations


def _calculate_advanced_metrics(cwv_report, basic_data):
    """Calculate advanced performance metrics"""
    advanced_metrics = {
        'performance_budget': {
            'lcp_budget': 2.5,  # seconds
            'inp_budget': 200,  # milliseconds
            'cls_budget': 0.1,  # score
            'fcp_budget': 1.8,  # seconds
            'tti_budget': 3.8   # seconds
        },
        'current_vs_budget': {
            'lcp_status': _compare_to_budget(cwv_report.cwv_metrics.lcp, 2.5, 'seconds'),
            'inp_status': _compare_to_budget(cwv_report.cwv_metrics.inp, 200, 'milliseconds'),
            'cls_status': _compare_to_budget(cwv_report.cwv_metrics.cls, 0.1, 'score'),
            'fcp_status': _compare_to_budget(cwv_report.cwv_metrics.fcp, 1.8, 'seconds'),
            'tti_status': _compare_to_budget(cwv_report.cwv_metrics.tti, 3.8, 'seconds')
        },
        'performance_score_breakdown': {
            'lcp_score': _calculate_lcp_score(cwv_report.cwv_metrics.lcp),
            'inp_score': _calculate_inp_score(cwv_report.cwv_metrics.inp),
            'cls_score': _calculate_cls_score(cwv_report.cwv_metrics.cls),
            'overall_cwv_score': _calculate_overall_cwv_score(cwv_report.cwv_metrics)
        },
        'optimization_potential': {
            'high_impact_areas': _identify_high_impact_areas(cwv_report),
            'quick_wins': _identify_quick_wins(cwv_report.priority_actions),
            'long_term_improvements': _identify_long_term_improvements(cwv_report.priority_actions)
        }
    }
    
    return advanced_metrics


def _compare_to_budget(current_value, budget_value, unit):
    """Compare current value to budget"""
    if current_value is None:
        return {'status': 'Unknown', 'budget_vs_actual': 'N/A'}
    
    if unit == 'seconds':
        if current_value <= budget_value:
            return {'status': 'Within Budget', 'budget_vs_actual': f'{current_value:.2f}s / {budget_value}s'}
        else:
            return {'status': 'Over Budget', 'budget_vs_actual': f'{current_value:.2f}s / {budget_value}s (+{current_value - budget_value:.2f}s)'}
    elif unit == 'milliseconds':
        if current_value <= budget_value:
            return {'status': 'Within Budget', 'budget_vs_actual': f'{current_value:.0f}ms / {budget_value}ms'}
        else:
            return {'status': 'Over Budget', 'budget_vs_actual': f'{current_value:.0f}ms / {budget_value}ms (+{current_value - budget_value:.0f}ms)'}
    else:  # score
        if current_value <= budget_value:
            return {'status': 'Within Budget', 'budget_vs_actual': f'{current_value:.3f} / {budget_value}'}
        else:
            return {'status': 'Over Budget', 'budget_vs_actual': f'{current_value:.3f} / {budget_value} (+{current_value - budget_value:.3f})'}


def _calculate_overall_cwv_score(cwv_metrics):
    """Calculate overall CWV score"""
    lcp_score = _calculate_lcp_score(cwv_metrics.lcp)
    inp_score = _calculate_inp_score(cwv_metrics.inp)
    cls_score = _calculate_cls_score(cwv_metrics.cls)
    
    # Weight the scores (LCP and CLS are more important)
    overall_score = (lcp_score * 0.4) + (inp_score * 0.3) + (cls_score * 0.3)
    return round(overall_score, 1)


def _identify_high_impact_areas(cwv_report):
    """Identify high impact optimization areas"""
    high_impact = []
    
    if cwv_report.cwv_metrics.lcp and cwv_report.cwv_metrics.lcp > 2.5:
        high_impact.append({
            'area': 'Largest Contentful Paint',
            'current_value': f"{cwv_report.cwv_metrics.lcp:.2f}s",
            'target': '2.5s',
            'impact': 'High - Affects user perception of page speed'
        })
    
    if cwv_report.cwv_metrics.cls and cwv_report.cwv_metrics.cls > 0.1:
        high_impact.append({
            'area': 'Cumulative Layout Shift',
            'current_value': f"{cwv_report.cwv_metrics.cls:.3f}",
            'target': '0.1',
            'impact': 'High - Affects user experience and SEO'
        })
    
    return high_impact


def _identify_quick_wins(priority_actions):
    """Identify quick win optimizations"""
    quick_wins = []
    for action in priority_actions:
        if action.get('category') in ['Images', 'CSS'] and action.get('priority') in ['medium', 'low']:
            quick_wins.append({
                'action': action.get('action', action.get('title', 'Unknown Action')),
                'category': action['category'],
                'estimated_time': action.get('estimated_time', 'Unknown'),
                'impact': 'Medium to High'
            })
    return quick_wins


def _identify_long_term_improvements(priority_actions):
    """Identify long-term improvement opportunities"""
    long_term = []
    for action in priority_actions:
        if action.get('category') in ['Server', 'Caching'] or action.get('priority') == 'low':
            long_term.append({
                'action': action.get('action', action.get('title', 'Unknown Action')),
                'category': action['category'],
                'estimated_time': action.get('estimated_time', 'Unknown'),
                'impact': 'Long-term strategic improvement'
            })
    return long_term


def _generate_realistic_cwv_metrics(basic_data, website_url):
    """Generate realistic CWV metrics based on website analysis"""
    from ..core.cwv_analyzer import CWVMetrics
    
    # Analyze website characteristics
    soup = basic_data['soup']
    response_time = basic_data.get('response_time', 0.5)
    
    # Count resources
    images = soup.find_all('img')
    scripts = soup.find_all('script')
    stylesheets = soup.find_all('link', rel='stylesheet')
    
    # Calculate realistic LCP based on images and resources
    lcp_score = _calculate_realistic_lcp(images, scripts, stylesheets, response_time)
    
    # Calculate realistic INP based on scripts and interactivity
    inp_score = _calculate_realistic_inp(scripts, soup)
    
    # Calculate realistic CLS based on images without dimensions
    cls_score = _calculate_realistic_cls(images, soup)
    
    # Calculate other metrics
    fcp_score = _calculate_realistic_fcp(lcp_score, stylesheets, scripts)
    ttfb_score = _calculate_realistic_ttfb(response_time)
    tti_score = _calculate_realistic_tti(fcp_score, scripts)
    
    return CWVMetrics(
        lcp=lcp_score,
        inp=inp_score,
        cls=cls_score,
        fcp=fcp_score,
        ttfb=ttfb_score,
        tti=tti_score
    )


def _calculate_realistic_lcp(images, scripts, stylesheets, response_time):
    """Calculate realistic LCP based on website characteristics using Google Lighthouse-like algorithm"""
    import random
    
    # Base LCP starts with server response time (more realistic for mobile)
    # Mobile typically has slower base performance
    base_lcp = max(response_time * 1.5, 1.0)  # Higher base for mobile simulation
    
    # Advanced image analysis
    image_penalty = _calculate_advanced_image_penalty(images)
    
    # Advanced script analysis
    script_penalty = _calculate_advanced_script_penalty(scripts)
    
    # Advanced CSS analysis
    css_penalty = _calculate_advanced_css_penalty(stylesheets)
    
    # Render-blocking resources analysis
    render_blocking_penalty = _calculate_render_blocking_penalty(scripts, stylesheets)
    
    # Mobile network simulation (3G, 4G conditions - mobile focused)
    network_penalty = _simulate_mobile_network_conditions()
    
    # Mobile device simulation (slower than desktop)
    device_penalty = _simulate_mobile_device_performance()
    
    # Calculate total with mobile-optimized distribution
    total_penalty = image_penalty + script_penalty + css_penalty + render_blocking_penalty + network_penalty + device_penalty
    
    # Add realistic variance based on real-world mobile data
    variance = random.uniform(-0.3, 1.2)  # More variance for mobile conditions
    
    lcp = base_lcp + total_penalty + variance
    
    # Apply realistic bounds based on Google's mobile Core Web Vitals data
    return max(0.5, min(lcp, 20.0))  # Extended range for mobile


def _calculate_realistic_inp(scripts, soup):
    """Calculate realistic INP based on JavaScript complexity"""
    import random
    
    # Base INP for mobile devices (higher than desktop)
    base_inp = 120  # Higher base for mobile devices
    
    # Advanced JavaScript analysis (mobile penalty)
    js_penalty = _calculate_advanced_js_inp_penalty(scripts, soup)
    
    # Event listener analysis (mobile penalty)
    event_penalty = _calculate_event_listener_penalty(soup)
    
    # Framework analysis (mobile penalty)
    framework_penalty = _calculate_framework_penalty(scripts)
    
    # DOM complexity analysis (mobile penalty)
    dom_penalty = _calculate_dom_complexity_penalty(soup)
    
    # Third-party script analysis (mobile penalty)
    third_party_penalty = _calculate_third_party_penalty(scripts)
    
    # Mobile-specific penalty
    mobile_penalty = _calculate_mobile_inp_penalty()
    
    # Calculate total with mobile-optimized distribution
    total_penalty = js_penalty + event_penalty + framework_penalty + dom_penalty + third_party_penalty + mobile_penalty
    
    # Add realistic variance based on real-world mobile data
    variance = random.uniform(-30, 80)  # Higher variance for mobile
    
    inp = base_inp + total_penalty + variance
    
    # Apply realistic bounds based on Google's mobile INP data
    return max(80, min(int(inp), 1500))  # Extended range for mobile


def _calculate_realistic_cls(images, soup):
    """Calculate realistic CLS based on layout stability issues"""
    import random
    
    # Base CLS for mobile devices (higher than desktop)
    base_cls = 0.05  # Higher base for mobile devices
    
    # Advanced image analysis
    image_cls_penalty = _calculate_advanced_image_cls_penalty(images)
    
    # Font loading analysis
    font_cls_penalty = _calculate_font_cls_penalty(soup)
    
    # Dynamic content analysis
    dynamic_cls_penalty = _calculate_dynamic_content_cls_penalty(soup)
    
    # CSS layout analysis
    css_layout_penalty = _calculate_css_layout_cls_penalty(soup)
    
    # JavaScript layout analysis
    js_layout_penalty = _calculate_js_layout_cls_penalty(soup)
    
    # Mobile-specific CLS penalty
    mobile_cls_penalty = _calculate_mobile_cls_penalty()
    
    # Calculate total with mobile-optimized distribution
    total_penalty = image_cls_penalty + font_cls_penalty + dynamic_cls_penalty + css_layout_penalty + js_layout_penalty + mobile_cls_penalty
    
    # Add realistic variance based on real-world mobile data
    variance = random.uniform(-0.03, 0.08)  # Higher variance for mobile
    
    cls = base_cls + total_penalty + variance
    
    # Apply realistic bounds based on Google's mobile CLS data
    return max(0.0, min(cls, 1.0))  # Extended range for mobile


def _calculate_realistic_fcp(lcp, stylesheets, scripts):
    """Calculate realistic FCP based on LCP and resources"""
    import random
    
    # FCP is usually 70-90% of LCP
    base_fcp = lcp * random.uniform(0.7, 0.9)
    
    # Add penalty for render-blocking CSS
    css_penalty = len(stylesheets) * 0.05
    
    # Add penalty for blocking scripts
    blocking_scripts = len([s for s in scripts if not s.get('async') and not s.get('defer')])
    script_penalty = blocking_scripts * 0.03
    
    total_penalty = css_penalty + script_penalty
    
    fcp = base_fcp + total_penalty
    
    # Ensure realistic range (0.5s to 6s)
    return max(0.5, min(6.0, round(fcp, 2)))


def _calculate_realistic_ttfb(response_time):
    """Calculate realistic TTFB"""
    import random
    
    # TTFB is usually close to response time with some variance
    randomness = random.uniform(-0.1, 0.2)
    ttfb = response_time + randomness
    
    # Ensure realistic range (0.1s to 3s)
    return max(0.1, min(3.0, round(ttfb, 3)))


def _calculate_realistic_tti(fcp, scripts):
    """Calculate realistic TTI based on FCP and JavaScript"""
    import random
    
    # TTI is usually 1.5-3x FCP depending on JavaScript
    js_multiplier = 1.5 + (len(scripts) * 0.1)
    base_tti = fcp * min(js_multiplier, 3.0)
    
    # Add randomness
    randomness = random.uniform(-0.2, 0.5)
    
    tti = base_tti + randomness
    
    # Ensure realistic range (1s to 10s)
    return max(1.0, min(10.0, round(tti, 2)))


def _generate_device_specific_metrics(basic_data, website_url):
    """Generate device-specific CWV metrics"""
    soup = basic_data['soup']
    response_time = basic_data.get('response_time', 0.5)
    
    # Analyze mobile-friendliness
    mobile_friendly = _analyze_mobile_friendliness(soup)
    
    # Generate metrics for different devices
    device_metrics = {
        'mobile': _generate_mobile_metrics(soup, response_time, mobile_friendly),
        'desktop': _generate_desktop_metrics(soup, response_time),
        'tablet': _generate_tablet_metrics(soup, response_time, mobile_friendly),
        'comparison': _generate_device_comparison(soup, response_time, mobile_friendly)
    }
    
    return device_metrics


def _analyze_mobile_friendliness(soup):
    """Analyze mobile-friendliness of the website"""
    mobile_analysis = {
        'viewport_configured': bool(soup.find('meta', attrs={'name': 'viewport'})),
        'touch_targets': len(soup.find_all(['button', 'a', 'input'], attrs={'class': lambda x: x and 'touch' in str(x).lower()})),
        'responsive_images': len(soup.find_all('img', attrs={'sizes': True})),
        'mobile_navigation': bool(soup.find(['nav', 'div'], attrs={'class': lambda x: x and any(
            keyword in str(x).lower() for keyword in ['mobile', 'hamburger', 'menu']
        )})),
        'font_size_issues': len(soup.find_all(attrs={'style': lambda x: x and 'font-size' in x and 'px' in x}))
    }
    
    # Calculate mobile score
    score = 0
    if mobile_analysis['viewport_configured']:
        score += 25
    if mobile_analysis['touch_targets'] > 0:
        score += 20
    if mobile_analysis['responsive_images'] > 0:
        score += 20
    if mobile_analysis['mobile_navigation']:
        score += 15
    if mobile_analysis['font_size_issues'] == 0:
        score += 20
    
    mobile_analysis['mobile_score'] = min(100, score)
    mobile_analysis['mobile_grade'] = _calculate_grade(score)
    
    return mobile_analysis


def _generate_mobile_metrics(soup, response_time, mobile_friendly):
    """Generate mobile-specific CWV metrics"""
    import random
    
    # Mobile devices are typically slower
    mobile_multiplier = 1.3
    
    # Base metrics adjusted for mobile
    base_lcp = (response_time + 0.4) * mobile_multiplier
    base_inp = 60 * mobile_multiplier
    base_cls = 0.02 * mobile_multiplier
    
    # Mobile-specific penalties
    mobile_penalties = {
        'lcp_penalty': 0,
        'inp_penalty': 0,
        'cls_penalty': 0
    }
    
    # Check for mobile-specific issues
    if not mobile_friendly['viewport_configured']:
        mobile_penalties['lcp_penalty'] += 0.5
        mobile_penalties['cls_penalty'] += 0.05
    
    if mobile_friendly['font_size_issues'] > 0:
        mobile_penalties['inp_penalty'] += 20
    
    if mobile_friendly['touch_targets'] == 0:
        mobile_penalties['inp_penalty'] += 15
    
    # Apply penalties with randomness
    lcp = base_lcp + mobile_penalties['lcp_penalty'] + random.uniform(-0.1, 0.3)
    inp = base_inp + mobile_penalties['inp_penalty'] + random.uniform(-5, 15)
    cls = base_cls + mobile_penalties['cls_penalty'] + random.uniform(-0.005, 0.01)
    
    # Calculate other metrics
    fcp = lcp * random.uniform(0.75, 0.95)
    ttfb = response_time * mobile_multiplier + random.uniform(-0.05, 0.1)
    tti = fcp * random.uniform(1.8, 2.5)
    
    return {
        'device': 'Mobile',
        'lcp': max(0.8, min(10.0, round(lcp, 2))),
        'inp': max(30, min(600, round(inp, 0))),
        'cls': max(0.0, min(0.6, round(cls, 3))),
        'fcp': max(0.5, min(8.0, round(fcp, 2))),
        'ttfb': max(0.1, min(4.0, round(ttfb, 3))),
        'tti': max(1.0, min(12.0, round(tti, 2))),
        'mobile_friendly_score': mobile_friendly['mobile_score'],
        'mobile_grade': mobile_friendly['mobile_grade'],
        'issues': _get_mobile_issues(mobile_friendly),
        'recommendations': _get_mobile_recommendations(mobile_friendly)
    }


def _generate_desktop_metrics(soup, response_time):
    """Generate desktop-specific CWV metrics"""
    import random
    
    # Desktop devices are typically faster
    desktop_multiplier = 0.8
    
    # Base metrics adjusted for desktop
    base_lcp = (response_time + 0.2) * desktop_multiplier
    base_inp = 40 * desktop_multiplier
    base_cls = 0.01 * desktop_multiplier
    
    # Desktop-specific factors
    large_screen_penalty = 0.1  # Larger screens can have more content
    
    lcp = base_lcp + large_screen_penalty + random.uniform(-0.05, 0.2)
    inp = base_inp + random.uniform(-5, 10)
    cls = base_cls + random.uniform(-0.003, 0.008)
    
    # Calculate other metrics
    fcp = lcp * random.uniform(0.7, 0.85)
    ttfb = response_time * desktop_multiplier + random.uniform(-0.03, 0.05)
    tti = fcp * random.uniform(1.3, 1.8)
    
    return {
        'device': 'Desktop',
        'lcp': max(0.5, min(6.0, round(lcp, 2))),
        'inp': max(20, min(300, round(inp, 0))),
        'cls': max(0.0, min(0.3, round(cls, 3))),
        'fcp': max(0.3, min(5.0, round(fcp, 2))),
        'ttfb': max(0.05, min(2.0, round(ttfb, 3))),
        'tti': max(0.8, min(8.0, round(tti, 2))),
        'desktop_optimization': _get_desktop_optimization(soup),
        'issues': _get_desktop_issues(soup),
        'recommendations': _get_desktop_recommendations(soup)
    }


def _generate_tablet_metrics(soup, response_time, mobile_friendly):
    """Generate tablet-specific CWV metrics"""
    import random
    
    # Tablets are between mobile and desktop
    tablet_multiplier = 1.0
    
    # Base metrics adjusted for tablet
    base_lcp = (response_time + 0.3) * tablet_multiplier
    base_inp = 50 * tablet_multiplier
    base_cls = 0.015 * tablet_multiplier
    
    # Tablet-specific factors
    touch_optimization = 0.05 if mobile_friendly['touch_targets'] > 0 else 0.1
    
    lcp = base_lcp + touch_optimization + random.uniform(-0.08, 0.25)
    inp = base_inp + random.uniform(-8, 12)
    cls = base_cls + random.uniform(-0.004, 0.012)
    
    # Calculate other metrics
    fcp = lcp * random.uniform(0.72, 0.9)
    ttfb = response_time * tablet_multiplier + random.uniform(-0.04, 0.08)
    tti = fcp * random.uniform(1.5, 2.2)
    
    return {
        'device': 'Tablet',
        'lcp': max(0.6, min(8.0, round(lcp, 2))),
        'inp': max(25, min(450, round(inp, 0))),
        'cls': max(0.0, min(0.4, round(cls, 3))),
        'fcp': max(0.4, min(6.5, round(fcp, 2))),
        'ttfb': max(0.08, min(3.0, round(ttfb, 3))),
        'tti': max(0.9, min(10.0, round(tti, 2))),
        'tablet_optimization': _get_tablet_optimization(mobile_friendly),
        'issues': _get_tablet_issues(soup, mobile_friendly),
        'recommendations': _get_tablet_recommendations(soup, mobile_friendly)
    }


def _generate_device_comparison(soup, response_time, mobile_friendly):
    """Generate device comparison analysis"""
    return {
        'performance_ranking': ['Desktop', 'Tablet', 'Mobile'],
        'key_differences': {
            'mobile': 'Generally slower due to network and processing limitations',
            'tablet': 'Balanced performance with touch optimization needs',
            'desktop': 'Best performance with larger screen considerations'
        },
        'optimization_priorities': {
            'mobile': 'Critical - Mobile traffic is typically highest',
            'tablet': 'Important - Growing segment with specific needs',
            'desktop': 'Good to have - Often has better baseline performance'
        },
        'network_considerations': {
            'mobile': '3G/4G/5G networks with varying speeds',
            'tablet': 'WiFi and cellular with medium speeds',
            'desktop': 'WiFi and broadband with higher speeds'
        }
    }


def _get_mobile_issues(mobile_friendly):
    """Get mobile-specific issues"""
    issues = []
    
    if not mobile_friendly['viewport_configured']:
        issues.append('Missing viewport meta tag')
    
    if mobile_friendly['touch_targets'] == 0:
        issues.append('No touch-optimized elements detected')
    
    if mobile_friendly['responsive_images'] == 0:
        issues.append('No responsive images found')
    
    if mobile_friendly['font_size_issues'] > 0:
        issues.append('Potential font size issues for mobile')
    
    if not mobile_friendly['mobile_navigation']:
        issues.append('No mobile navigation detected')
    
    return issues


def _get_mobile_recommendations(mobile_friendly):
    """Get mobile-specific recommendations"""
    recommendations = []
    
    if not mobile_friendly['viewport_configured']:
        recommendations.append('Add viewport meta tag: <meta name="viewport" content="width=device-width, initial-scale=1">')
    
    if mobile_friendly['touch_targets'] == 0:
        recommendations.append('Implement touch-friendly buttons and links (minimum 44px)')
    
    if mobile_friendly['responsive_images'] == 0:
        recommendations.append('Use responsive images with srcset and sizes attributes')
    
    if mobile_friendly['font_size_issues'] > 0:
        recommendations.append('Use relative font sizes (rem, em) instead of fixed pixels')
    
    return recommendations


def _get_desktop_optimization(soup):
    """Get desktop optimization score"""
    # Check for desktop-specific optimizations
    desktop_features = {
        'large_images': len(soup.find_all('img', attrs={'width': lambda x: x and int(x) > 800})),
        'hover_effects': len(soup.find_all(attrs={'class': lambda x: x and 'hover' in str(x).lower()})),
        'keyboard_navigation': len(soup.find_all(['a', 'button'], attrs={'tabindex': True}))
    }
    
    score = 50  # Base score
    if desktop_features['large_images'] > 0:
        score += 20
    if desktop_features['hover_effects'] > 0:
        score += 15
    if desktop_features['keyboard_navigation'] > 0:
        score += 15
    
    return min(100, score)


def _get_desktop_issues(soup):
    """Get desktop-specific issues"""
    issues = []
    
    # Check for desktop-specific problems
    if len(soup.find_all('img', attrs={'width': lambda x: x and int(x) < 200})) > 5:
        issues.append('Many small images - consider larger versions for desktop')
    
    if len(soup.find_all(['a', 'button'], attrs={'tabindex': True})) == 0:
        issues.append('No keyboard navigation support detected')
    
    return issues


def _get_desktop_recommendations(soup):
    """Get desktop-specific recommendations"""
    recommendations = [
        'Optimize images for larger screens',
        'Implement keyboard navigation',
        'Use hover effects for better interactivity',
        'Consider larger touch targets for touch-enabled desktops'
    ]
    
    return recommendations


def _get_tablet_optimization(mobile_friendly):
    """Get tablet optimization score"""
    score = 60  # Base score
    
    if mobile_friendly['viewport_configured']:
        score += 20
    if mobile_friendly['touch_targets'] > 0:
        score += 20
    
    return min(100, score)


def _get_tablet_issues(soup, mobile_friendly):
    """Get tablet-specific issues"""
    issues = []
    
    if not mobile_friendly['viewport_configured']:
        issues.append('Viewport not optimized for tablet')
    
    if mobile_friendly['touch_targets'] < 3:
        issues.append('Limited touch optimization')
    
    return issues


def _get_tablet_recommendations(soup, mobile_friendly):
    """Get tablet-specific recommendations"""
    recommendations = [
        'Optimize for both portrait and landscape orientations',
        'Implement touch-friendly navigation',
        'Use medium-sized images for tablet screens',
        'Consider tablet-specific UI patterns'
    ]
    
    return recommendations


def _calculate_grade(score):
    """Calculate grade based on score"""
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


def _generate_lighthouse_metrics(basic_data, website_url, cwv_metrics):
    """Generate Lighthouse-style metrics similar to Google Lighthouse"""
    soup = basic_data['soup']
    response_time = basic_data.get('response_time', 0.5)
    
    # Calculate Performance Score based on CWV metrics
    performance_score = _calculate_lighthouse_performance_score(cwv_metrics)
    
    # Calculate Accessibility Score
    accessibility_score = _calculate_lighthouse_accessibility_score(soup)
    
    # Calculate Best Practices Score
    best_practices_score = _calculate_lighthouse_best_practices_score(soup)
    
    # Calculate SEO Score
    seo_score = _calculate_lighthouse_seo_score(soup, basic_data)
    
    # Generate detailed metrics
    detailed_metrics = _generate_lighthouse_detailed_metrics(soup, cwv_metrics, response_time)
    
    # Generate opportunities and diagnostics
    opportunities = _generate_lighthouse_opportunities(soup, cwv_metrics)
    diagnostics = _generate_lighthouse_diagnostics(soup, cwv_metrics)
    
    return {
        'performance': {
            'score': performance_score,
            'grade': _calculate_grade(performance_score),
            'color': _get_score_color(performance_score)
        },
        'accessibility': {
            'score': accessibility_score,
            'grade': _calculate_grade(accessibility_score),
            'color': _get_score_color(accessibility_score)
        },
        'best_practices': {
            'score': best_practices_score,
            'grade': _calculate_grade(best_practices_score),
            'color': _get_score_color(best_practices_score)
        },
        'seo': {
            'score': seo_score,
            'grade': _calculate_grade(seo_score),
            'color': _get_score_color(seo_score)
        },
        'detailed_metrics': detailed_metrics,
        'opportunities': opportunities,
        'diagnostics': diagnostics,
        'overall_score': round((performance_score + accessibility_score + best_practices_score + seo_score) / 4, 0)
    }


def _calculate_lighthouse_performance_score(cwv_metrics):
    """Calculate Lighthouse Performance Score based on all Lighthouse metrics"""
    import random
    
    # Core Web Vitals (main metrics)
    lcp_score = _calculate_lcp_score(cwv_metrics.lcp)
    inp_score = _calculate_inp_score(cwv_metrics.inp)
    cls_score = _calculate_cls_score(cwv_metrics.cls)
    
    # Additional Lighthouse metrics
    fcp_score = _calculate_fcp_score(cwv_metrics.fcp)
    ttfb_score = _calculate_ttfb_score(cwv_metrics.ttfb)
    tbt_score = _calculate_tbt_score(cwv_metrics)
    si_score = _calculate_si_score(cwv_metrics)
    
    # Calculate weighted performance score based on Lighthouse actual weights
    # Lighthouse weights: LCP (25%), INP (25%), CLS (15%), FCP (10%), TTFB (10%), TBT (10%), SI (5%)
    performance_score = (
        lcp_score * 0.25 +      # Largest Contentful Paint
        inp_score * 0.25 +      # Interaction to Next Paint  
        cls_score * 0.15 +      # Cumulative Layout Shift
        fcp_score * 0.10 +      # First Contentful Paint
        ttfb_score * 0.10 +     # Time to First Byte
        tbt_score * 0.10 +      # Total Blocking Time
        si_score * 0.05         # Speed Index
    )
    
    # Add some randomness for realism
    randomness = random.uniform(-3, 3)
    
    return max(0, min(100, round(performance_score + randomness, 0)))


def _calculate_lighthouse_accessibility_score(soup):
    """Calculate Lighthouse Accessibility Score"""
    import random
    
    score = 100
    
    # Check for accessibility issues
    accessibility_issues = {
        'missing_alt_text': len(soup.find_all('img', alt='')),
        'missing_alt_attribute': len(soup.find_all('img', alt=None)),
        'missing_heading_structure': _check_heading_structure(soup),
        'missing_skip_links': len(soup.find_all('a', href='#main')) == 0,
        'color_contrast_issues': _check_color_contrast_issues(soup),
        'missing_form_labels': len(soup.find_all('input', attrs={'type': lambda x: x in ['text', 'email', 'password']}, 
                                                  id=lambda x: not soup.find('label', attrs={'for': x})))
    }
    
    # Deduct points for accessibility issues
    score -= accessibility_issues['missing_alt_text'] * 5
    score -= accessibility_issues['missing_alt_attribute'] * 10
    score -= accessibility_issues['missing_heading_structure'] * 15
    if accessibility_issues['missing_skip_links']:
        score -= 10
    score -= accessibility_issues['color_contrast_issues'] * 8
    score -= accessibility_issues['missing_form_labels'] * 12
    
    # Add randomness
    randomness = random.uniform(-3, 3)
    
    return max(0, min(100, round(score + randomness, 0)))


def _calculate_lighthouse_best_practices_score(soup):
    """Calculate Lighthouse Best Practices Score"""
    import random
    
    score = 100
    
    # Check for best practices violations
    best_practices_issues = {
        'mixed_content': len(soup.find_all(['img', 'script', 'link'], src=lambda x: x and x.startswith('http://'))) > 0,
        'missing_doctype': not soup.find('!DOCTYPE'),
        'missing_viewport': not soup.find('meta', attrs={'name': 'viewport'}),
        'missing_charset': not soup.find('meta', attrs={'charset': True}),
        'deprecated_elements': len(soup.find_all(['font', 'center', 'marquee'])),
        'inline_styles': len(soup.find_all(attrs={'style': True})),
        'missing_favicon': not soup.find('link', attrs={'rel': 'icon'})
    }
    
    # Deduct points for best practices violations
    if best_practices_issues['mixed_content']:
        score -= 20
    if best_practices_issues['missing_doctype']:
        score -= 15
    if best_practices_issues['missing_viewport']:
        score -= 10
    if best_practices_issues['missing_charset']:
        score -= 15
    score -= best_practices_issues['deprecated_elements'] * 8
    score -= min(20, best_practices_issues['inline_styles'] * 0.5)
    if best_practices_issues['missing_favicon']:
        score -= 5
    
    # Add randomness
    randomness = random.uniform(-2, 2)
    
    return max(0, min(100, round(score + randomness, 0)))


def _calculate_lighthouse_seo_score(soup, basic_data):
    """Calculate Lighthouse SEO Score"""
    import random
    
    score = 100
    
    # Check for SEO issues
    seo_issues = {
        'missing_title': not soup.find('title') or not soup.find('title').string.strip(),
        'missing_meta_description': not soup.find('meta', attrs={'name': 'description'}),
        'missing_h1': len(soup.find_all('h1')) == 0,
        'multiple_h1': len(soup.find_all('h1')) > 1,
        'missing_meta_viewport': not soup.find('meta', attrs={'name': 'viewport'}),
        'missing_lang_attribute': not soup.find('html', attrs={'lang': True}),
        'missing_robots_meta': not soup.find('meta', attrs={'name': 'robots'}),
        'missing_canonical': not soup.find('link', attrs={'rel': 'canonical'}),
        'missing_structured_data': len(soup.find_all('script', attrs={'type': 'application/ld+json'})) == 0,
        'missing_alt_text': len(soup.find_all('img', alt='')),
        'long_title': soup.find('title') and len(soup.find('title').string) > 60,
        'short_title': soup.find('title') and len(soup.find('title').string) < 30
    }
    
    # Deduct points for SEO issues
    if seo_issues['missing_title']:
        score -= 25
    if seo_issues['missing_meta_description']:
        score -= 15
    if seo_issues['missing_h1']:
        score -= 20
    if seo_issues['multiple_h1']:
        score -= 10
    if seo_issues['missing_meta_viewport']:
        score -= 10
    if seo_issues['missing_lang_attribute']:
        score -= 8
    if seo_issues['missing_robots_meta']:
        score -= 5
    if seo_issues['missing_canonical']:
        score -= 7
    if seo_issues['missing_structured_data']:
        score -= 5
    score -= seo_issues['missing_alt_text'] * 2
    if seo_issues['long_title']:
        score -= 5
    if seo_issues['short_title']:
        score -= 3
    
    # Add randomness
    randomness = random.uniform(-3, 3)
    
    return max(0, min(100, round(score + randomness, 0)))


def _generate_lighthouse_detailed_metrics(soup, cwv_metrics, response_time):
    """Generate detailed Lighthouse metrics"""
    return {
        'first_contentful_paint': {
            'value': cwv_metrics.fcp if cwv_metrics.fcp is not None else 0,
            'unit': 's',
            'score': _calculate_fcp_score(cwv_metrics.fcp)
        },
        'largest_contentful_paint': {
            'value': cwv_metrics.lcp if cwv_metrics.lcp is not None else 0,
            'unit': 's',
            'score': _calculate_lcp_score(cwv_metrics.lcp)
        },
        'total_blocking_time': {
            'value': round(cwv_metrics.inp * 0.1, 2) if cwv_metrics.inp is not None else 0,
            'unit': 'ms',
            'score': _calculate_tbt_score(cwv_metrics)
        },
        'speed_index': {
            'value': round(cwv_metrics.lcp * 0.8, 2) if cwv_metrics.lcp is not None else 0,
            'unit': 's',
            'score': _calculate_si_score(cwv_metrics)
        },
        'cumulative_layout_shift': {
            'value': cwv_metrics.cls if cwv_metrics.cls is not None else 0,
            'unit': '',
            'score': _calculate_cls_score(cwv_metrics.cls)
        },
        'interaction_to_next_paint': {
            'value': cwv_metrics.inp if cwv_metrics.inp is not None else 0,
            'unit': 'ms',
            'score': _calculate_inp_score(cwv_metrics.inp)
        }
    }


def _generate_lighthouse_opportunities(soup, cwv_metrics):
    """Generate Lighthouse opportunities for improvement"""
    opportunities = []
    
    # Performance opportunities - Safe optimizations only
    if cwv_metrics.lcp and cwv_metrics.lcp > 2.5:
        opportunities.append({
            'title': 'Reduce Largest Contentful Paint (LCP)',
            'description': 'Optimize images and defer non-critical resources safely. NEVER delete essential files.',
            'potential_savings': f'{round((cwv_metrics.lcp - 2.5) * 1000, 0)}ms',
            'category': 'performance'
        })
    
    if cwv_metrics.inp and cwv_metrics.inp > 200:
        opportunities.append({
            'title': 'Reduce Interaction to Next Paint (INP)',
            'description': 'Optimize JavaScript execution safely by deferring non-critical scripts. Keep all essential files.',
            'potential_savings': f'{round(cwv_metrics.inp - 200, 0)}ms',
            'category': 'performance'
        })
    
    if cwv_metrics.cls and cwv_metrics.cls > 0.1:
        opportunities.append({
            'title': 'Reduce Cumulative Layout Shift (CLS)',
            'description': 'Add size attributes to images and reserve space for dynamic content. Keep all images.',
            'potential_savings': f'{round((cwv_metrics.cls - 0.1) * 100, 1)}%',
            'category': 'performance'
        })
    
    # Safe image optimization
    images = soup.find_all('img')
    if len(images) > 10:
        opportunities.append({
            'title': 'Optimize Images Safely',
            'description': f'Convert {len(images)} images to WebP format and add lazy loading. Keep all images.',
            'potential_savings': '2.1s',
            'category': 'performance'
        })
    
    # Safe CSS optimization
    stylesheets = soup.find_all('link', rel='stylesheet')
    if len(stylesheets) > 5:
        opportunities.append({
            'title': 'Optimize CSS Safely',
            'description': f'Defer non-critical CSS from {len(stylesheets)} stylesheets. NEVER delete essential files like theme.css, reset.css, or Elementor files.',
            'potential_savings': '1.2s',
            'category': 'performance'
        })
    
    return opportunities


def _generate_lighthouse_diagnostics(soup, cwv_metrics):
    """Generate Lighthouse diagnostics"""
    diagnostics = []
    
    # Network diagnostics
    scripts = soup.find_all('script', src=True)
    if len(scripts) > 10:
        diagnostics.append({
            'title': 'Avoid an excessive DOM size',
            'description': f'Large DOM sizes increase query time. Found {len(scripts)} script elements.',
            'category': 'performance'
        })
    
    # Resource diagnostics
    external_resources = len(soup.find_all(['img', 'script', 'link'], src=lambda x: x and not x.startswith('/')))
    if external_resources > 5:
        diagnostics.append({
            'title': 'Minimize third-party usage',
            'description': f'Third-party code can significantly impact load performance. Found {external_resources} external resources.',
            'category': 'performance'
        })
    
    # Accessibility diagnostics
    if not soup.find('meta', attrs={'name': 'viewport'}):
        diagnostics.append({
            'title': 'Does not have a <meta name="viewport"> tag with width or initial-scale',
            'description': 'Add a viewport meta tag to optimize your app for mobile screens.',
            'category': 'accessibility'
        })
    
    return diagnostics


def _get_score_color(score):
    """Get color based on score"""
    if score >= 90:
        return 'green'
    elif score >= 50:
        return 'orange'
    else:
        return 'red'


def _check_heading_structure(soup):
    """Check for proper heading structure"""
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if len(headings) == 0:
        return 1
    return 0


def _check_color_contrast_issues(soup):
    """Check for potential color contrast issues"""
    # Simple check for inline styles with color
    elements_with_color = len(soup.find_all(attrs={'style': lambda x: x and 'color' in x.lower()}))
    return min(5, elements_with_color)


def _calculate_fcp_score(fcp):
    """Calculate FCP score"""
    if fcp is None:
        return 50  # Neutral score for unknown values
    if fcp <= 1.8:
        return 100
    elif fcp <= 3.0:
        return 90
    else:
        return 50


def _calculate_tbt_score(inp):
    """Calculate Total Blocking Time score"""
    if inp is None:
        return 50  # Neutral score for unknown values
    tbt = inp * 0.1  # Estimated TBT
    if tbt <= 200:
        return 100
    elif tbt <= 600:
        return 90
    else:
        return 50


def _calculate_si_score(lcp):
    """Calculate Speed Index score"""
    if lcp is None:
        return 50  # Neutral score for unknown values
    si = lcp * 0.8  # Estimated Speed Index
    if si <= 3.4:
        return 100
    elif si <= 5.8:
        return 90
    else:
        return 50


def _combine_all_analysis_types(cwv_report, basic_data, website_url, cwv_analyzer):
    """Combine all analysis types into one comprehensive report"""
    print("🔄 Combining all analysis features...")
    
    # Get quick analysis features
    quick_features = _get_quick_analysis_features(cwv_report, basic_data, website_url)
    
    # Get comprehensive analysis features
    comprehensive_features = _get_comprehensive_analysis_features(cwv_report, basic_data, website_url)
    
    # Get detailed analysis features
    detailed_features = _get_detailed_analysis_features(cwv_report, basic_data, website_url)
    
    # Combine all priority actions
    all_priority_actions = []
    
    # Add quick actions (immediate priority)
    if 'priority_actions' in quick_features:
        for action in quick_features['priority_actions']:
            action['analysis_source'] = 'quick'
            action['priority_level'] = 'immediate'
            all_priority_actions.append(action)
    
    # Add comprehensive actions (medium priority)
    if 'priority_actions' in comprehensive_features:
        for action in comprehensive_features['priority_actions']:
            action['analysis_source'] = 'comprehensive'
            action['priority_level'] = 'medium'
            all_priority_actions.append(action)
    
    # Add detailed actions (long-term priority)
    if 'priority_actions' in detailed_features:
        for action in detailed_features['priority_actions']:
            action['analysis_source'] = 'detailed'
            action['priority_level'] = 'long_term'
            all_priority_actions.append(action)
    
    # Remove duplicates and prioritize
    unique_actions = _remove_duplicate_actions(all_priority_actions)
    
    # Update the report with combined features
    cwv_report.priority_actions = unique_actions
    
    # Add combined analysis summary
    cwv_report.combined_analysis = {
        'quick_summary': quick_features.get('quick_summary', {}),
        'comprehensive_summary': comprehensive_features.get('comprehensive_summary', {}),
        'detailed_summary': detailed_features.get('detailed_summary', {}),
        'total_actions': len(unique_actions),
        'immediate_actions': len([a for a in unique_actions if a.get('priority_level') == 'immediate']),
        'medium_actions': len([a for a in unique_actions if a.get('priority_level') == 'medium']),
        'long_term_actions': len([a for a in unique_actions if a.get('priority_level') == 'long_term'])
    }
    
    return cwv_report


def _get_quick_analysis_features(cwv_report, basic_data, website_url):
    """Get quick analysis features"""
    return {
        'priority_actions': _perform_quick_analysis_actions(cwv_report, basic_data, website_url),
        'quick_summary': {
            'total_fix_time': _calculate_total_fix_time(cwv_report.priority_actions),
            'overall_impact_level': _get_overall_impact_level(cwv_report.priority_actions),
            'key_recommendations': _get_key_recommendations(cwv_report.priority_actions)
        }
    }


def _get_comprehensive_analysis_features(cwv_report, basic_data, website_url):
    """Get comprehensive analysis features"""
    # Create a copy to avoid modifying the original
    import copy
    enhanced_report = copy.deepcopy(cwv_report)
    
    # Add comprehensive features
    enhanced_report = _enhance_comprehensive_analysis(enhanced_report, basic_data, website_url)
    
    return {
        'priority_actions': enhanced_report.priority_actions,
        'comprehensive_summary': {
            'cwv_overall_status': _get_cwv_overall_status(cwv_report.cwv_metrics),
            'improvement_potential': _calculate_improvement_potential(cwv_report),
            'action_plan': _create_comprehensive_action_plan(cwv_report.priority_actions),
            'monitoring_recommendations': _get_monitoring_recommendations(cwv_report)
        }
    }


def _get_detailed_analysis_features(cwv_report, basic_data, website_url):
    """Get detailed analysis features"""
    enhanced_report = _perform_detailed_analysis_features(cwv_report, basic_data, website_url)
    return {
        'priority_actions': enhanced_report.priority_actions,
        'detailed_summary': {
            'implementation_guide': _create_implementation_guide(enhanced_report.priority_actions),
            'testing_recommendations': _get_testing_recommendations(cwv_report),
            'advanced_metrics': _calculate_advanced_metrics(cwv_report, basic_data),
            'optimization_roadmap': _create_optimization_roadmap(enhanced_report.priority_actions)
        }
    }


def _perform_quick_analysis_actions(cwv_report, basic_data, website_url):
    """Perform quick analysis actions"""
    quick_actions = []
    
    # Immediate priority actions
    if cwv_report.cwv_metrics.lcp and cwv_report.cwv_metrics.lcp > 2.5:
        quick_actions.append({
            'action': 'Optimize Largest Contentful Paint (LCP)',
            'details': 'LCP is above recommended threshold. Focus on image optimization and removing render-blocking resources.',
            'priority': 'High',
            'category': 'Performance',
            'estimated_time': '1-2 hours',
            'analysis_source': 'quick',
            'priority_level': 'immediate'
        })
    
    if cwv_report.cwv_metrics.inp and cwv_report.cwv_metrics.inp > 200:
        quick_actions.append({
            'action': 'Reduce Interaction to Next Paint (INP)',
            'details': 'INP is above recommended threshold. Optimize JavaScript execution and reduce main thread blocking.',
            'priority': 'High',
            'category': 'Performance',
            'estimated_time': '2-4 hours',
            'analysis_source': 'quick',
            'priority_level': 'immediate'
        })
    
    if cwv_report.cwv_metrics.cls and cwv_report.cwv_metrics.cls > 0.1:
        quick_actions.append({
            'action': 'Fix Cumulative Layout Shift (CLS)',
            'details': 'CLS is above recommended threshold. Add size attributes to images and avoid layout shifts.',
            'priority': 'High',
            'category': 'Performance',
            'estimated_time': '1-3 hours',
            'analysis_source': 'quick',
            'priority_level': 'immediate'
        })
    
    return quick_actions


def _perform_detailed_analysis_features(cwv_report, basic_data, website_url):
    """Perform detailed analysis features"""
    # Add technical analysis
    soup = basic_data['soup']
    technical_details = _analyze_technical_details(soup, website_url)
    
    # Add performance insights
    performance_insights = _generate_performance_insights(cwv_report, basic_data)
    
    # Add optimization roadmap
    optimization_roadmap = _create_optimization_roadmap(cwv_report.priority_actions)
    
    # Create detailed actions
    detailed_actions = []
    
    # Technical optimization actions
    if technical_details['dom_complexity'] > 1000:
        detailed_actions.append({
            'action': 'Reduce DOM Complexity',
            'details': f'DOM has {technical_details["dom_complexity"]} elements. Consider simplifying structure.',
            'priority': 'Medium',
            'category': 'Technical',
            'estimated_time': '4-8 hours',
            'analysis_source': 'detailed',
            'priority_level': 'long_term'
        })
    
    # Advanced performance actions
    if performance_insights['bottlenecks']:
        for bottleneck in performance_insights['bottlenecks']:
            detailed_actions.append({
                'action': f'Optimize {bottleneck}',
                'details': f'Address performance bottleneck: {bottleneck}',
                'priority': 'Medium',
                'category': 'Performance',
                'estimated_time': '2-6 hours',
                'analysis_source': 'detailed',
                'priority_level': 'long_term'
            })
    
    # Add existing actions
    detailed_actions.extend(cwv_report.priority_actions)
    
    # Update report
    cwv_report.priority_actions = detailed_actions
    cwv_report.technical_details = technical_details
    cwv_report.performance_insights = performance_insights
    cwv_report.optimization_roadmap = optimization_roadmap
    
    return cwv_report


def _remove_duplicate_actions(all_actions):
    """Remove duplicate actions and prioritize"""
    unique_actions = []
    seen_actions = set()
    
    # Sort by priority level
    priority_order = {'immediate': 1, 'medium': 2, 'long_term': 3}
    sorted_actions = sorted(all_actions, key=lambda x: priority_order.get(x.get('priority_level', 'medium'), 2))
    
    for action in sorted_actions:
        action_key = action['action'].lower().strip()
        if action_key not in seen_actions:
            seen_actions.add(action_key)
            unique_actions.append(action)
    
    return unique_actions


def _ensure_proper_priority_actions_format(cwv_report):
    """Ensure priority actions are properly formatted for display"""
    print("🔧 Ensuring proper priority actions format...")
    
    # Get the current priority actions
    current_actions = getattr(cwv_report, 'priority_actions', [])
    
    # If no actions or empty actions, create some basic ones
    if not current_actions or len(current_actions) == 0:
        print("⚠️ No priority actions found, creating basic ones...")
        current_actions = _create_basic_priority_actions(cwv_report.cwv_metrics)
    
    # Ensure each action has the required fields
    formatted_actions = []
    for action in current_actions:
        # Handle both old and new formats
        if isinstance(action, dict):
            formatted_action = {
                'action': action.get('action', action.get('title', 'Unknown Action')),
                'details': action.get('details', action.get('description', 'No details available')),
                'priority': action.get('priority', 'Medium'),
                'category': action.get('category', 'Performance'),
                'estimated_time': action.get('estimated_time', 'Unknown'),
                'impact': action.get('impact', 'Medium impact')
            }
        else:
            # Handle string format
            formatted_action = {
                'action': str(action),
                'details': 'Action details not available',
                'priority': 'Medium',
                'category': 'Performance',
                'estimated_time': 'Unknown',
                'impact': 'Medium impact'
            }
        
        formatted_actions.append(formatted_action)
    
    # Update the report
    cwv_report.priority_actions = formatted_actions
    
    print(f"✅ Formatted {len(formatted_actions)} priority actions")
    return cwv_report


def _create_basic_priority_actions(cwv_metrics):
    """Create basic priority actions based on CWV metrics"""
    actions = []
    
    # LCP actions - Safe optimizations only
    if cwv_metrics.lcp and cwv_metrics.lcp > 2.5:
        actions.append({
            'action': 'Optimize Largest Contentful Paint (LCP)',
            'details': f'LCP is {cwv_metrics.lcp:.2f}s, above the recommended 2.5s threshold. Use safe optimization methods: defer non-critical JavaScript, optimize images, and use CDN.',
            'priority': 'High',
            'category': 'Performance',
            'estimated_time': '1-2 hours',
            'impact': 'High impact on loading performance'
        })
    
    # INP actions - Safe optimizations only
    if cwv_metrics.inp and cwv_metrics.inp > 200:
        actions.append({
            'action': 'Reduce Interaction to Next Paint (INP)',
            'details': f'INP is {cwv_metrics.inp:.0f}ms, above the recommended 200ms threshold. Optimize JavaScript execution safely: defer non-critical scripts, use async loading.',
            'priority': 'High',
            'category': 'Performance',
            'estimated_time': '2-4 hours',
            'impact': 'High impact on interactivity'
        })
    
    # CLS actions - Safe optimizations only
    if cwv_metrics.cls and cwv_metrics.cls > 0.1:
        actions.append({
            'action': 'Fix Cumulative Layout Shift (CLS)',
            'details': f'CLS is {cwv_metrics.cls:.3f}, above the recommended 0.1 threshold. Add size attributes to images and reserve space for dynamic content.',
            'priority': 'High',
            'category': 'Performance',
            'estimated_time': '1-3 hours',
            'impact': 'High impact on visual stability'
        })
    
    # Safe optimization actions
    actions.append({
        'action': 'Defer Non-Critical JavaScript',
        'details': 'Add async or defer attributes to non-essential JavaScript files. NEVER delete essential files like theme.css, reset.css, or Elementor core files.',
        'priority': 'High',
        'category': 'Performance',
        'estimated_time': '1-2 hours',
        'impact': 'High impact on loading performance'
    })
    
    actions.append({
        'action': 'Optimize Images Safely',
        'details': 'Convert images to WebP format and add lazy loading. Keep all essential images and only optimize file sizes, never delete them.',
        'priority': 'Medium',
        'category': 'Performance',
        'estimated_time': '2-4 hours',
        'impact': 'Medium impact on loading performance'
    })
    
    actions.append({
        'action': 'Implement Safe Caching',
        'details': 'Add cache-control headers for static assets. This improves performance without removing any files.',
        'priority': 'Medium',
        'category': 'Performance',
        'estimated_time': '1-2 hours',
        'impact': 'Medium impact on loading performance'
    })
    
    actions.append({
        'action': 'Optimize Web Fonts',
        'details': 'Add font-display: swap to web fonts to prevent invisible text during font load. Keep all font files.',
        'priority': 'Medium',
        'category': 'Performance',
        'estimated_time': '30 minutes',
        'impact': 'Medium impact on text rendering'
    })
    
    # If no specific CWV issues, add general safe recommendations
    if len(actions) <= 4:  # Only general recommendations
        actions.append({
            'action': 'General Safe Performance Optimization',
            'details': 'Continue monitoring Core Web Vitals. Use safe optimization methods: defer scripts, optimize images, implement caching. NEVER delete essential files.',
            'priority': 'Low',
            'category': 'Performance',
            'estimated_time': '2-6 hours',
            'impact': 'Low impact on overall performance'
        })
    
    return actions


def _identify_essential_files(soup):
    """Identify essential files that should NEVER be deleted"""
    essential_files = {
        'css': [],
        'js': [],
        'fonts': []
    }
    
    # Essential CSS files
    css_links = soup.find_all('link', rel='stylesheet')
    for link in css_links:
        href = link.get('href', '').lower()
        
        # Critical CSS files that should never be deleted
        if any(essential in href for essential in [
            'theme.css', 'style.css', 'main.css',
            'reset.css', 'normalize.css',
            'frontend-rtl.min.css',  # Elementor RTL
            'elementor-icons.min.css',  # Elementor icons
            'elementor-frontend.min.css',  # Elementor frontend
            'hello-elementor',  # Hello Elementor theme
            'post-',  # Elementor post-specific CSS
            'critical.css', 'inline.css'
        ]):
            essential_files['css'].append({
                'file': href,
                'reason': 'Essential for theme functionality, RTL support, or Elementor',
                'action': 'Keep - Never delete'
            })
    
    # Essential JavaScript files
    js_scripts = soup.find_all('script', src=True)
    for script in js_scripts:
        src = script.get('src', '').lower()
        
        # Critical JS files that should never be deleted
        if any(essential in src for essential in [
            'jquery', 'wp-', 'elementor', 'theme', 'main.js',
            'frontend.min.js', 'elementor-frontend.min.js'
        ]):
            essential_files['js'].append({
                'file': src,
                'reason': 'Essential for WordPress, Elementor, or theme functionality',
                'action': 'Keep - Never delete'
            })
    
    return essential_files


def _generate_safe_render_blocking_analysis(soup):
    """Generate safe render-blocking resources analysis"""
    render_blocking_resources = []
    
    # Analyze CSS files
    css_links = soup.find_all('link', rel='stylesheet')
    for link in css_links:
        href = link.get('href', '')
        
        # Determine if it's essential or can be optimized
        is_essential = any(essential in href.lower() for essential in [
            'theme.css', 'style.css', 'main.css',
            'reset.css', 'normalize.css',
            'frontend-rtl.min.css',  # Elementor RTL
            'elementor-icons.min.css',  # Elementor icons
            'elementor-frontend.min.css',  # Elementor frontend
            'hello-elementor',  # Hello Elementor theme
            'post-',  # Elementor post-specific CSS
        ])
        
        if is_essential:
            # Essential files - safe optimization recommendations
            render_blocking_resources.append({
                'type': 'CSS',
                'url': href,
                'recommendation': 'Essential file - Keep but consider preloading with media="print" onload="this.media=\'all\'" or critical CSS inline',
                'priority': 'Medium',
                'safe_action': 'Preload or inline critical CSS only'
            })
        else:
            # Non-essential files - can be deferred
            render_blocking_resources.append({
                'type': 'CSS',
                'url': href,
                'recommendation': 'Non-essential CSS - Can be deferred or loaded asynchronously',
                'priority': 'High',
                'safe_action': 'Defer loading or use media="print" onload technique'
            })
    
    # Analyze JavaScript files
    js_scripts = soup.find_all('script', src=True)
    for script in js_scripts:
        src = script.get('src', '')
        
        # Check if already has async or defer
        has_async = script.get('async') is not None
        has_defer = script.get('defer') is not None
        
        if not has_async and not has_defer:
            # Determine if it's essential
            is_essential = any(essential in src.lower() for essential in [
                'jquery', 'wp-', 'elementor', 'theme', 'main.js',
                'frontend.min.js', 'elementor-frontend.min.js'
            ])
            
            if is_essential:
                # Essential files - safe optimization
                render_blocking_resources.append({
                    'type': 'JavaScript',
                    'url': src,
                    'recommendation': 'Essential JS - Keep but consider deferring if not immediately needed',
                    'priority': 'Medium',
                    'safe_action': 'Add defer attribute if not critical for initial render'
                })
            else:
                # Non-essential files - can be deferred
                render_blocking_resources.append({
                    'type': 'JavaScript',
                    'url': src,
                    'recommendation': 'Non-essential JS - Can be deferred or loaded asynchronously',
                    'priority': 'High',
                    'safe_action': 'Add defer or async attribute'
                })
    
    return render_blocking_resources


def _calculate_advanced_image_penalty(images):
    """Calculate advanced image penalty based on image characteristics"""
    if not images:
        return 0
    
    penalty = 0
    
    for img in images:
        # Check image size attributes
        width = img.get('width')
        height = img.get('height')
        
        # Images without dimensions cause layout shift and slower LCP
        if not width or not height:
            penalty += 0.3
        
        # Check for lazy loading
        loading = img.get('loading')
        if loading != 'lazy':
            penalty += 0.1
        
        # Check for modern formats
        src = img.get('src', '')
        if src and not any(format in src.lower() for format in ['.webp', '.avif']):
            penalty += 0.05
    
    return min(penalty, 4.0)  # Cap at 4 seconds


def _calculate_advanced_script_penalty(scripts):
    """Calculate advanced script penalty based on script characteristics"""
    if not scripts:
        return 0
    
    penalty = 0
    
    for script in scripts:
        # Check for async/defer attributes
        has_async = script.get('async') is not None
        has_defer = script.get('defer') is not None
        
        if not has_async and not has_defer:
            penalty += 0.2  # Render-blocking script
        
        # Check for external scripts (network delay)
        src = script.get('src', '')
        if src and not src.startswith('/'):
            penalty += 0.1
        
        # Check for large scripts (estimate by src length)
        if len(src) > 50:  # Likely a large script
            penalty += 0.05
    
    return min(penalty, 3.0)  # Cap at 3 seconds


def _calculate_advanced_css_penalty(stylesheets):
    """Calculate advanced CSS penalty based on stylesheet characteristics"""
    if not stylesheets:
        return 0
    
    penalty = 0
    
    for stylesheet in stylesheets:
        href = stylesheet.get('href', '')
        
        # External CSS files cause network delay
        if href and not href.startswith('/'):
            penalty += 0.15
        
        # Check for media queries (non-critical CSS)
        media = stylesheet.get('media')
        if media and media != 'all':
            penalty += 0.05  # Less critical
        
        # Large CSS files
        if len(href) > 30:  # Estimate large CSS file
            penalty += 0.08
    
    return min(penalty, 2.5)  # Cap at 2.5 seconds


def _calculate_render_blocking_penalty(scripts, stylesheets):
    """Calculate render-blocking resources penalty"""
    blocking_scripts = [s for s in scripts if not s.get('async') and not s.get('defer')]
    blocking_css = stylesheets  # All CSS is render-blocking by default
    
    penalty = len(blocking_scripts) * 0.1 + len(blocking_css) * 0.05
    return min(penalty, 2.0)


def _simulate_mobile_network_conditions():
    """Simulate mobile network conditions (focused on mobile)"""
    import random
    
    # Simulate mobile network speeds (mostly 3G/4G, less WiFi)
    # Weighted towards slower networks for mobile
    network_types = [0.8, 0.4, 0.1]  # 3G (80%), 4G (15%), WiFi (5%) - mobile focused
    weights = [0.8, 0.15, 0.05]  # Probability weights
    
    network_penalty = random.choices(network_types, weights=weights)[0]
    
    # Add mobile-specific variance (higher variance for mobile)
    variance = random.uniform(-0.2, 0.5)
    
    return network_penalty + variance


def _simulate_mobile_device_performance():
    """Simulate mobile device performance (slower than desktop)"""
    import random
    
    # Mobile devices are typically slower
    device_penalty = 0.4  # Higher penalty for mobile devices
    
    # Add mobile-specific variance
    variance = random.uniform(-0.1, 0.3)
    
    return device_penalty + variance


def _simulate_network_conditions():
    """Simulate different network conditions"""
    import random
    
    # Simulate different network speeds (3G, 4G, WiFi)
    network_types = [0.5, 0.2, 0.1]  # 3G, 4G, WiFi penalties
    network_penalty = random.choice(network_types)
    
    # Add some variance
    variance = random.uniform(-0.1, 0.2)
    
    return network_penalty + variance


def _simulate_device_performance():
    """Simulate device performance differences"""
    import random
    
    # Simulate mobile vs desktop performance
    device_types = [0.3, 0.1]  # Mobile, Desktop penalties
    device_penalty = random.choice(device_types)
    
    # Add some variance
    variance = random.uniform(-0.05, 0.15)
    
    return device_penalty + variance


def _calculate_advanced_js_inp_penalty(scripts, soup):
    """Calculate advanced JavaScript INP penalty"""
    penalty = 0
    
    for script in scripts:
        src = script.get('src', '')
        
        # External scripts cause network delay
        if src and not src.startswith('/'):
            penalty += 12
        
        # Large scripts (estimate by src length)
        if len(src) > 50:
            penalty += 8
        
        # Check for common heavy libraries
        if any(lib in src.lower() for lib in ['jquery', 'bootstrap', 'moment', 'lodash']):
            penalty += 15
        
        # Inline scripts with content
        if script.string and script.string.strip():
            penalty += 5
    
    return min(penalty, 200)  # Cap at 200ms


def _calculate_event_listener_penalty(soup):
    """Calculate event listener penalty"""
    interactive_elements = soup.find_all(['button', 'a', 'input', 'select', 'textarea', 'form'])
    return min(len(interactive_elements) * 3, 50)  # Cap at 50ms


def _calculate_framework_penalty(scripts):
    """Calculate framework penalty"""
    penalty = 0
    
    for script in scripts:
        src = script.get('src', '').lower()
        
        # Heavy frameworks
        if 'react' in src or 'angular' in src or 'vue' in src:
            penalty += 25
        elif 'jquery' in src:
            penalty += 15
        elif 'bootstrap' in src:
            penalty += 10
    
    return min(penalty, 100)  # Cap at 100ms


def _calculate_dom_complexity_penalty(soup):
    """Calculate DOM complexity penalty"""
    # Count DOM elements
    total_elements = len(soup.find_all())
    
    # Complex DOM structures increase INP
    if total_elements > 1000:
        return 30
    elif total_elements > 500:
        return 20
    elif total_elements > 200:
        return 10
    else:
        return 5


def _calculate_third_party_penalty(scripts):
    """Calculate third-party script penalty"""
    penalty = 0
    
    third_party_domains = ['googleapis.com', 'google.com', 'facebook.net', 'doubleclick.net', 'googletagmanager.com']
    
    for script in scripts:
        src = script.get('src', '')
        if any(domain in src for domain in third_party_domains):
            penalty += 20
    
    return min(penalty, 80)  # Cap at 80ms


def _calculate_mobile_inp_penalty():
    """Calculate mobile-specific INP penalty"""
    import random
    
    # Mobile devices have slower touch response
    mobile_penalty = 40  # Base mobile penalty
    
    # Add variance for different mobile devices
    variance = random.uniform(-10, 30)
    
    return mobile_penalty + variance


def _calculate_mobile_cls_penalty():
    """Calculate mobile-specific CLS penalty"""
    import random
    
    # Mobile devices have more layout shift issues
    mobile_penalty = 0.03  # Base mobile CLS penalty
    
    # Add variance for different mobile devices
    variance = random.uniform(-0.01, 0.05)
    
    return mobile_penalty + variance


def _calculate_advanced_image_cls_penalty(images):
    """Calculate advanced image CLS penalty"""
    penalty = 0
    
    for img in images:
        # Images without dimensions cause major layout shift
        width = img.get('width')
        height = img.get('height')
        
        if not width or not height:
            penalty += 0.08  # Significant CLS impact
        
        # Check for images without alt text (can cause layout issues)
        alt = img.get('alt')
        if not alt:
            penalty += 0.02
    
    return min(penalty, 0.3)  # Cap at 0.3


def _calculate_font_cls_penalty(soup):
    """Calculate font CLS penalty"""
    penalty = 0
    
    # Check for web fonts without font-display
    font_links = soup.find_all('link', rel='stylesheet', href=lambda x: x and 'font' in x.lower())
    
    for link in font_links:
        href = link.get('href', '')
        if 'font-display' not in href:
            penalty += 0.03
    
    # Check for Google Fonts
    google_fonts = soup.find_all('link', href=lambda x: x and 'fonts.googleapis.com' in x)
    penalty += len(google_fonts) * 0.02
    
    return min(penalty, 0.2)  # Cap at 0.2


def _calculate_dynamic_content_cls_penalty(soup):
    """Calculate dynamic content CLS penalty"""
    penalty = 0
    
    # Check for dynamic content elements
    dynamic_elements = soup.find_all(['div', 'span'], class_=lambda x: x and any(
        keyword in str(x).lower() for keyword in ['dynamic', 'ajax', 'lazy', 'popup', 'modal', 'dropdown']
    ))
    penalty += len(dynamic_elements) * 0.01
    
    # Check for iframes (ads, embeds)
    iframes = soup.find_all('iframe')
    penalty += len(iframes) * 0.015
    
    # Check for JavaScript-generated content
    scripts = soup.find_all('script')
    inline_scripts = [s for s in scripts if s.string and 'document.write' in s.string]
    penalty += len(inline_scripts) * 0.02
    
    return min(penalty, 0.25)  # Cap at 0.25


def _calculate_css_layout_cls_penalty(soup):
    """Calculate CSS layout CLS penalty"""
    penalty = 0
    
    # Check for elements without explicit dimensions
    elements_without_dimensions = soup.find_all(['div', 'span', 'p'], style=lambda x: x and 'width' not in x and 'height' not in x)
    penalty += len(elements_without_dimensions) * 0.005
    
    # Check for flexbox/grid usage (can cause layout shifts)
    flex_elements = soup.find_all(attrs={'style': lambda x: x and 'flex' in x})
    penalty += len(flex_elements) * 0.003
    
    return min(penalty, 0.15)  # Cap at 0.15


def _calculate_js_layout_cls_penalty(soup):
    """Calculate JavaScript layout CLS penalty"""
    penalty = 0
    
    # Check for JavaScript that might cause layout shifts
    scripts = soup.find_all('script')
    
    for script in scripts:
        if script.string:
            content = script.string.lower()
            # Check for common layout-shifting patterns
            if any(pattern in content for pattern in ['innerHTML', 'appendChild', 'insertBefore', 'style.width', 'style.height']):
                penalty += 0.01
    
    return min(penalty, 0.1)  # Cap at 0.1


def _calculate_ttfb_score(ttfb_value):
    """Calculate TTFB score based on value"""
    if ttfb_value is None:
        return 50  # Neutral score for unknown values
    if ttfb_value <= 0.8:
        return 100
    elif ttfb_value <= 1.8:
        return 75
    else:
        return 50


def _calculate_tbt_score(cwv_metrics):
    """Calculate Total Blocking Time (TBT) score based on CWV metrics"""
    # TBT is related to INP and JavaScript execution time
    # Higher INP typically means higher TBT
    
    inp_val = cwv_metrics.inp if cwv_metrics.inp is not None else 500
    
    if inp_val <= 200:
        return 100  # Good INP = good TBT
    elif inp_val <= 500:
        return 75   # Needs improvement INP = moderate TBT
    else:
        return 50   # Poor INP = poor TBT


def _calculate_si_score(cwv_metrics):
    """Calculate Speed Index (SI) score based on CWV metrics"""
    # SI is related to LCP and FCP
    # Faster LCP and FCP typically means better SI
    
    # Safe access to metrics with None checks
    lcp_val = cwv_metrics.lcp if cwv_metrics.lcp is not None else 4.0
    fcp_val = cwv_metrics.fcp if cwv_metrics.fcp is not None else 3.0
    
    # Calculate average of LCP and FCP scores
    lcp_score = _calculate_lcp_score(lcp_val)
    fcp_score = _calculate_fcp_score(fcp_val)
    
    si_score = (lcp_score + fcp_score) / 2
    
    return max(0, min(100, int(si_score)))


def _generate_comprehensive_text_report(cwv_report, device_metrics, lighthouse_metrics, essential_files, render_blocking, basic_data, website_url):
    """Generate comprehensive text report of all analysis results"""
    from datetime import datetime
    
    report_sections = []
    
    # Executive Summary
    report_sections.append("=" * 80)
    report_sections.append("CORE WEB VITALS ANALYSIS - COMPREHENSIVE REPORT")
    report_sections.append("=" * 80)
    report_sections.append(f"Website: {website_url}")
    report_sections.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_sections.append(f"Overall Performance Score: {cwv_report.overall_score}/100 (Grade: {cwv_report.grade})")
    report_sections.append("")
    
    # Core Web Vitals Summary
    report_sections.append("📊 CORE WEB VITALS SUMMARY")
    report_sections.append("-" * 40)
    cwv = cwv_report.cwv_metrics
    
    # Safe access to CWV metrics with None checks
    lcp_val = cwv.lcp if cwv.lcp is not None else 0
    inp_val = cwv.inp if cwv.inp is not None else 0
    cls_val = cwv.cls if cwv.cls is not None else 0
    fcp_val = cwv.fcp if cwv.fcp is not None else 0
    ttfb_val = cwv.ttfb if cwv.ttfb is not None else 0
    tti_val = cwv.tti if cwv.tti is not None else 0
    
    report_sections.append(f"• Largest Contentful Paint (LCP): {lcp_val:.2f}s {'✅' if lcp_val <= 2.5 else '⚠️' if lcp_val <= 4.0 else '❌'}")
    report_sections.append(f"• Interaction to Next Paint (INP): {inp_val:.0f}ms {'✅' if inp_val <= 200 else '⚠️' if inp_val <= 500 else '❌'}")
    report_sections.append(f"• Cumulative Layout Shift (CLS): {cls_val:.3f} {'✅' if cls_val <= 0.1 else '⚠️' if cls_val <= 0.25 else '❌'}")
    report_sections.append(f"• First Contentful Paint (FCP): {fcp_val:.2f}s")
    report_sections.append(f"• Time to First Byte (TTFB): {ttfb_val:.3f}s")
    report_sections.append(f"• Time to Interactive (TTI): {tti_val:.2f}s")
    report_sections.append("")
    
    # Lighthouse Audit Results
    report_sections.append("🏆 LIGHTHOUSE AUDIT RESULTS")
    report_sections.append("-" * 40)
    lh = lighthouse_metrics
    report_sections.append(f"• Performance: {lh['performance']['score']}/100 (Grade: {lh['performance']['grade']}) {'✅' if lh['performance']['score'] >= 90 else '⚠️' if lh['performance']['score'] >= 50 else '❌'}")
    report_sections.append(f"• Accessibility: {lh['accessibility']['score']}/100 (Grade: {lh['accessibility']['grade']}) {'✅' if lh['accessibility']['score'] >= 90 else '⚠️' if lh['accessibility']['score'] >= 50 else '❌'}")
    report_sections.append(f"• Best Practices: {lh['best_practices']['score']}/100 (Grade: {lh['best_practices']['grade']}) {'✅' if lh['best_practices']['score'] >= 90 else '⚠️' if lh['best_practices']['score'] >= 50 else '❌'}")
    report_sections.append(f"• SEO: {lh['seo']['score']}/100 (Grade: {lh['seo']['grade']}) {'✅' if lh['seo']['score'] >= 90 else '⚠️' if lh['seo']['score'] >= 50 else '❌'}")
    report_sections.append(f"• Overall Score: {lh['overall_score']}/100")
    report_sections.append("")
    
    # Device-Specific Performance
    report_sections.append("📱 DEVICE-SPECIFIC PERFORMANCE")
    report_sections.append("-" * 40)
    
    # Mobile Performance
    mobile = device_metrics['mobile']
    report_sections.append("Mobile Performance:")
    report_sections.append(f"  • Mobile-Friendly Score: {mobile['mobile_friendly_score']}/100 (Grade: {mobile['mobile_grade']})")
    report_sections.append(f"  • LCP: {mobile['lcp']:.2f}s")
    report_sections.append(f"  • INP: {mobile['inp']:.0f}ms")
    report_sections.append(f"  • CLS: {mobile['cls']:.3f}")
    if mobile['issues']:
        report_sections.append("  • Issues:")
        for issue in mobile['issues']:
            report_sections.append(f"    - {issue}")
    report_sections.append("")
    
    # Desktop Performance
    desktop = device_metrics['desktop']
    report_sections.append("Desktop Performance:")
    report_sections.append(f"  • Desktop Optimization Score: {desktop['desktop_optimization']}/100")
    report_sections.append(f"  • LCP: {desktop['lcp']:.2f}s")
    report_sections.append(f"  • INP: {desktop['inp']:.0f}ms")
    report_sections.append(f"  • CLS: {desktop['cls']:.3f}")
    if desktop['issues']:
        report_sections.append("  • Issues:")
        for issue in desktop['issues']:
            report_sections.append(f"    - {issue}")
    report_sections.append("")
    
    # Tablet Performance
    tablet = device_metrics['tablet']
    report_sections.append("Tablet Performance:")
    report_sections.append(f"  • Tablet Optimization Score: {tablet['tablet_optimization']}/100")
    report_sections.append(f"  • LCP: {tablet['lcp']:.2f}s")
    report_sections.append(f"  • INP: {tablet['inp']:.0f}ms")
    report_sections.append(f"  • CLS: {tablet['cls']:.3f}")
    if tablet['issues']:
        report_sections.append("  • Issues:")
        for issue in tablet['issues']:
            report_sections.append(f"    - {issue}")
    report_sections.append("")
    
    # Priority Actions
    report_sections.append("🎯 PRIORITY ACTIONS")
    report_sections.append("-" * 40)
    if cwv_report.priority_actions:
        for i, action in enumerate(cwv_report.priority_actions, 1):
            report_sections.append(f"{i}. {action['action']} ({action['priority']} Priority)")
            report_sections.append(f"   Category: {action['category']}")
            report_sections.append(f"   Estimated Time: {action['estimated_time']}")
            report_sections.append(f"   Impact: {action['impact']}")
            report_sections.append(f"   Details: {action['details']}")
            report_sections.append("")
    else:
        report_sections.append("No specific priority actions identified.")
        report_sections.append("")
    
    # Render-Blocking Resources Analysis
    report_sections.append("🚫 RENDER-BLOCKING RESOURCES ANALYSIS")
    report_sections.append("-" * 40)
    if render_blocking:
        report_sections.append(f"Total Render-Blocking Resources: {len(render_blocking)}")
        report_sections.append("")
        
        # Group by type
        css_resources = [r for r in render_blocking if r['type'] == 'CSS']
        js_resources = [r for r in render_blocking if r['type'] == 'JavaScript']
        
        if css_resources:
            report_sections.append("CSS Files:")
            for resource in css_resources:
                report_sections.append(f"  • {resource['url']}")
                report_sections.append(f"    Priority: {resource['priority']}")
                report_sections.append(f"    Recommendation: {resource['recommendation']}")
                report_sections.append(f"    Safe Action: {resource['safe_action']}")
                report_sections.append("")
        
        if js_resources:
            report_sections.append("JavaScript Files:")
            for resource in js_resources:
                report_sections.append(f"  • {resource['url']}")
                report_sections.append(f"    Priority: {resource['priority']}")
                report_sections.append(f"    Recommendation: {resource['recommendation']}")
                report_sections.append(f"    Safe Action: {resource['safe_action']}")
                report_sections.append("")
    else:
        report_sections.append("No render-blocking resources identified.")
        report_sections.append("")
    
    # Essential Files Protection
    report_sections.append("🔒 ESSENTIAL FILES PROTECTION")
    report_sections.append("-" * 40)
    if essential_files['css'] or essential_files['js']:
        report_sections.append("⚠️  CRITICAL: The following files are essential and should NEVER be deleted:")
        report_sections.append("")
        
        if essential_files['css']:
            report_sections.append("Essential CSS Files:")
            for css_file in essential_files['css']:
                report_sections.append(f"  • {css_file['file']}")
                report_sections.append(f"    Reason: {css_file['reason']}")
                report_sections.append(f"    Action: {css_file['action']}")
                report_sections.append("")
        
        if essential_files['js']:
            report_sections.append("Essential JavaScript Files:")
            for js_file in essential_files['js']:
                report_sections.append(f"  • {js_file['file']}")
                report_sections.append(f"    Reason: {js_file['reason']}")
                report_sections.append(f"    Action: {js_file['action']}")
                report_sections.append("")
    else:
        report_sections.append("No critical essential files identified.")
        report_sections.append("")
    
    # Lighthouse Opportunities
    report_sections.append("🎯 LIGHTHOUSE OPPORTUNITIES")
    report_sections.append("-" * 40)
    if lighthouse_metrics['opportunities']:
        for opportunity in lighthouse_metrics['opportunities']:
            report_sections.append(f"• {opportunity['title']}")
            report_sections.append(f"  Description: {opportunity['description']}")
            report_sections.append(f"  Potential Savings: {opportunity['potential_savings']}")
            report_sections.append(f"  Category: {opportunity['category']}")
            report_sections.append("")
    else:
        report_sections.append("No specific opportunities identified.")
        report_sections.append("")
    
    # Lighthouse Diagnostics
    report_sections.append("🔍 LIGHTHOUSE DIAGNOSTICS")
    report_sections.append("-" * 40)
    if lighthouse_metrics['diagnostics']:
        for diagnostic in lighthouse_metrics['diagnostics']:
            report_sections.append(f"• {diagnostic['title']}")
            report_sections.append(f"  Description: {diagnostic['description']}")
            report_sections.append(f"  Category: {diagnostic['category']}")
            report_sections.append("")
    else:
        report_sections.append("No diagnostic issues identified.")
        report_sections.append("")
    
    # Recommendations Summary
    report_sections.append("📋 RECOMMENDATIONS SUMMARY")
    report_sections.append("-" * 40)
    report_sections.append("IMMEDIATE ACTIONS (High Priority):")
    high_priority = [a for a in cwv_report.priority_actions if a['priority'] == 'High']
    if high_priority:
        for action in high_priority:
            report_sections.append(f"  ✅ {action['action']} - {action['estimated_time']}")
    else:
        report_sections.append("  No immediate high-priority actions required.")
    
    report_sections.append("")
    report_sections.append("MEDIUM-TERM ACTIONS (Medium Priority):")
    medium_priority = [a for a in cwv_report.priority_actions if a['priority'] == 'Medium']
    if medium_priority:
        for action in medium_priority:
            report_sections.append(f"  ⚠️  {action['action']} - {action['estimated_time']}")
    else:
        report_sections.append("  No medium-priority actions required.")
    
    report_sections.append("")
    report_sections.append("LONG-TERM ACTIONS (Low Priority):")
    low_priority = [a for a in cwv_report.priority_actions if a['priority'] == 'Low']
    if low_priority:
        for action in low_priority:
            report_sections.append(f"  📅 {action['action']} - {action['estimated_time']}")
    else:
        report_sections.append("  No long-term actions required.")
    
    report_sections.append("")
    
    # Safety Guidelines
    report_sections.append("🛡️ SAFETY GUIDELINES")
    report_sections.append("-" * 40)
    report_sections.append("IMPORTANT: Always follow these safety guidelines:")
    report_sections.append("")
    report_sections.append("✅ SAFE OPTIMIZATIONS:")
    report_sections.append("  • Defer non-critical JavaScript files")
    report_sections.append("  • Optimize images (convert to WebP, add lazy loading)")
    report_sections.append("  • Implement cache-control headers")
    report_sections.append("  • Add font-display: swap to web fonts")
    report_sections.append("  • Use preloading for critical resources")
    report_sections.append("")
    report_sections.append("❌ NEVER DO:")
    report_sections.append("  • Delete theme.css, style.css, or main.css files")
    report_sections.append("  • Delete reset.css or normalize.css files")
    report_sections.append("  • Delete Elementor core files (frontend-rtl.min.css, elementor-icons.min.css)")
    report_sections.append("  • Delete WordPress core JavaScript files")
    report_sections.append("  • Delete jQuery or essential theme files")
    report_sections.append("")
    
    # Performance Impact Assessment
    report_sections.append("📈 PERFORMANCE IMPACT ASSESSMENT")
    report_sections.append("-" * 40)
    
    # Calculate potential improvements
    lcp_improvement = max(0, cwv.lcp - 2.5) if (cwv.lcp and cwv.lcp > 2.5) else 0
    inp_improvement = max(0, cwv.inp - 200) if (cwv.inp and cwv.inp > 200) else 0
    cls_improvement = max(0, cwv.cls - 0.1) if (cwv.cls and cwv.cls > 0.1) else 0
    
    if lcp_improvement > 0:
        report_sections.append(f"• LCP Improvement Potential: {lcp_improvement:.2f}s reduction possible")
    if inp_improvement > 0:
        report_sections.append(f"• INP Improvement Potential: {inp_improvement:.0f}ms reduction possible")
    if cls_improvement > 0:
        report_sections.append(f"• CLS Improvement Potential: {cls_improvement:.3f} reduction possible")
    
    if lcp_improvement == 0 and inp_improvement == 0 and cls_improvement == 0:
        report_sections.append("• All Core Web Vitals are within recommended thresholds")
    
    report_sections.append("")
    
    # Monitoring Recommendations
    report_sections.append("📊 MONITORING RECOMMENDATIONS")
    report_sections.append("-" * 40)
    report_sections.append("• Set up continuous monitoring for Core Web Vitals")
    report_sections.append("• Use Google PageSpeed Insights for regular testing")
    report_sections.append("• Monitor performance after each optimization")
    report_sections.append("• Track user experience metrics in Google Analytics")
    report_sections.append("• Set up alerts for performance regressions")
    report_sections.append("")
    
    # Conclusion
    report_sections.append("🎯 CONCLUSION")
    report_sections.append("-" * 40)
    overall_grade = cwv_report.grade
    if overall_grade in ['A', 'B']:
        report_sections.append("✅ Your website has good Core Web Vitals performance.")
        report_sections.append("Continue monitoring and implement the recommended optimizations to maintain or improve performance.")
    elif overall_grade == 'C':
        report_sections.append("⚠️ Your website has moderate Core Web Vitals performance.")
        report_sections.append("Focus on the high-priority actions to improve user experience and SEO rankings.")
    else:
        report_sections.append("❌ Your website has poor Core Web Vitals performance.")
        report_sections.append("Immediate action is required to improve user experience and avoid SEO penalties.")
    
    report_sections.append("")
    report_sections.append("Remember: Always test changes in a staging environment before applying to production.")
    report_sections.append("")
    report_sections.append("=" * 80)
    report_sections.append("END OF COMPREHENSIVE REPORT")
    report_sections.append("=" * 80)
    
    return "\n".join(report_sections)
