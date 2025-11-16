"""
Enhanced Keyword Gap Analysis Routes (v2.0)
Uses the new EnhancedKeywordGapAnalyzer with business intelligence.
"""

from __future__ import annotations

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .routes import login_required
import traceback
import json
import os
from datetime import datetime

keyword_gap_v2_bp = Blueprint("keyword_gap_v2", __name__, url_prefix="/keyword-gap-v2")


@keyword_gap_v2_bp.route("/", methods=["GET", "POST"])
@login_required
def keyword_gap_v2_index():
    """
    Enhanced Keyword Gap Analysis page with business context
    """
    if request.method == "POST":
        # Get form data
        own_website = request.form.get("own_website", "").strip()
        competitors = [c.strip() for c in request.form.getlist("competitors[]") if c.strip()]
        
        # Get business context
        industry = request.form.get("industry", "").strip()
        niche = request.form.get("niche", "").strip()
        services_text = request.form.get("services", "").strip()
        target_locations_text = request.form.get("target_locations", "").strip()
        
        print(f"\n🔍 Enhanced Keyword Gap Analysis Request:")
        print(f"   Own website: {own_website}")
        print(f"   Competitors: {competitors}")
        print(f"   Industry: {industry}")
        print(f"   Niche: {niche}")
        
        # Validation
        if not own_website:
            flash("Please enter your website URL", "error")
            return render_template("keyword_gap_v2.html")
        
        if not competitors:
            flash("Please enter at least one competitor URL", "error")
            return render_template("keyword_gap_v2.html")
        
        # Build business context
        business_context = None
        if industry or niche:
            from ..core.models import BusinessContext
            
            # Parse services (one per line)
            services = []
            if services_text:
                services = [s.strip() for s in services_text.split('\n') if s.strip()]
            
            # Parse locations (comma-separated)
            locations = []
            if target_locations_text:
                locations = [l.strip() for l in target_locations_text.split(',') if l.strip()]
            
            business_context = BusinessContext(
                industry=industry or "general",
                niche=niche or "general",
                services=services,
                products=[],  # Could be added later
                target_locations=locations,
                brand_keywords=[],  # Could be extracted from URL
                excluded_keywords=[]
            )
            
            print(f"   Business Context: {business_context.industry} - {business_context.niche}")
            print(f"   Services: {len(services)}")
            print(f"   Locations: {len(locations)}")
        
        # Perform enhanced keyword gap analysis
        try:
            from ..core.enhanced_keyword_gap_analyzer import EnhancedKeywordGapAnalyzer
            
            print("\n🚀 Starting enhanced keyword gap analysis...")
            analyzer = EnhancedKeywordGapAnalyzer(business_context=business_context)
            result = analyzer.analyze_keyword_gap(own_website, competitors, business_context)
            
            # Save results
            try:
                filename = analyzer.save_results(result)
                print(f"💾 Results saved to: {filename}")
            except Exception as save_error:
                print(f"⚠️ Could not save results: {save_error}")
                filename = "keyword_gap_analysis_v2.json"
            
            # Render enhanced results page
            return render_template("keyword_gap_result_v2.html", 
                                 result=result, 
                                 filename=filename,
                                 business_context=business_context)
            
        except Exception as e:
            print(f"❌ Error in enhanced keyword gap analysis: {e}")
            traceback.print_exc()
            flash(f"Analysis failed: {str(e)}", "error")
            return render_template("keyword_gap_v2.html")
    
    return render_template("keyword_gap_v2.html")

