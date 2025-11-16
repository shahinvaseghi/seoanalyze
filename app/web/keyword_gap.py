from __future__ import annotations

from flask import Blueprint, render_template, request, flash, redirect, url_for
from .routes import login_required
import traceback

keyword_gap_bp = Blueprint("keyword_gap", __name__, url_prefix="/keyword-gap")

@keyword_gap_bp.route("/", methods=["GET", "POST"])
@login_required
def keyword_gap_index():
    """
    Keyword Gap Analysis page
    """
    if request.method == "POST":
        # Get form data
        own_website = request.form.get("own_website", "").strip()
        competitors = [c.strip() for c in request.form.getlist("competitors[]") if c.strip()]
        
        print(f"🔍 Keyword Gap Analysis Request:")
        print(f"   Own website: {own_website}")
        print(f"   Competitors: {competitors}")
        
        # Validation
        if not own_website:
            flash("Please enter your website URL", "error")
            return render_template("keyword_gap.html")
        
        if not competitors:
            flash("Please enter at least one competitor URL", "error")
            return render_template("keyword_gap.html")
        
        # Perform keyword gap analysis
        try:
            from app.core.keyword_gap_analyzer import KeywordGapAnalyzer
            
            print("🚀 Starting keyword gap analysis...")
            analyzer = KeywordGapAnalyzer()
            result = analyzer.analyze_keyword_gap(own_website, competitors)
            
            # Try to save results, but don't fail if it doesn't work
            try:
                filename = analyzer.save_analysis_result(result)
                print(f"💾 Results saved to: {filename}")
            except Exception as save_error:
                print(f"⚠️ Could not save results: {save_error}")
                filename = "keyword_gap_analysis.json"
            
            # Render results page
            return render_template("keyword_gap_result_minimal.html", 
                                 result=result, 
                                 filename=filename)
            
        except Exception as e:
            print(f"❌ Error in keyword gap analysis: {e}")
            traceback.print_exc()
            flash(f"Analysis failed: {str(e)}", "error")
            return render_template("keyword_gap.html")
    
    return render_template("keyword_gap.html")
