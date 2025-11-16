from __future__ import annotations

from flask import Blueprint, render_template, request, flash, redirect, url_for
import json
import os
from datetime import datetime

from .routes import login_required


competitors_bp = Blueprint("competitors", __name__, url_prefix="/competitors")


@competitors_bp.route("/", methods=["GET", "POST"])
@login_required
def competitors_index():
    if request.method == "POST":
        # Expect multiple inputs for both competitors and keywords.
        # Frontend will submit arrays using input name="competitors[]" and name="keywords[]"
        competitors = [c.strip() for c in request.form.getlist("competitors[]") if c.strip()]
        keywords = [k.strip() for k in request.form.getlist("keywords[]") if k.strip()]
        
        print(f"Received competitors: {competitors}")
        print(f"Received keywords: {keywords}")
        print(f"All form data: {dict(request.form)}")
        print(f"Form method: {request.method}")
        print(f"Form content type: {request.content_type}")
        
        if not competitors:
            flash("Please enter at least one competitor URL", "error")
            return render_template("competitors.html")
        
        # Perform real analysis
        try:
            from app.core.seo_analyzer import SEOAnalyzer
            analyzer = SEOAnalyzer()
            
            # Analyze each competitor
            results = []
            for i, url in enumerate(competitors):
                try:
                    print(f"Starting analysis {i+1}/{len(competitors)} for: {url}")
                    analysis = analyzer.analyze_competitor(url, keywords=keywords)
                    if analysis:
                        results.append(analysis)
                        print(f"Analysis completed {i+1}/{len(competitors)} for: {url}")
                    else:
                        print(f"No analysis result {i+1}/{len(competitors)} for: {url}")
                except Exception as e:
                    print(f"Error analyzing {i+1}/{len(competitors)} {url}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Save results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"competitors_analysis_{timestamp}.json"
            results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
            os.makedirs(results_dir, exist_ok=True)
            
            with open(os.path.join(results_dir, filename), "w", encoding="utf-8") as f:
                json.dump({
                    "timestamp": timestamp,
                    "competitors": competitors,
                    "keywords": keywords,
                    "results": results
                }, f, ensure_ascii=False, indent=2)
            
            print(f"Analysis completed. Results count: {len(results)}")
            if not results:
                flash("No analysis results generated. Please check the URLs and try again.", "error")
                return render_template("competitors.html")
            
            return render_template(
                "competitors_result.html",
                competitors=competitors,
                keywords=keywords,
                results=results,
                filename=filename
            )
        except Exception as e:
            print(f"Analysis failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            flash(f"Analysis failed: {str(e)}", "error")
            return render_template("competitors.html")
    
    return render_template("competitors.html")


