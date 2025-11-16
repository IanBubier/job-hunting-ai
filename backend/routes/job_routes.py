import os
import time
from flask import Blueprint, jsonify, request, render_template
from backend.services.adzuna_service import AdzunaService
from backend.services.ml_service import MLService
from backend.services.matching_service import MatchingService
from backend.utils.validators import validate_search_request
import logging

logger = logging.getLogger(__name__)

jobs_bp = Blueprint("jobs_bp", __name__, url_prefix="/search")

# Initialize services (in production, replace with DI)
ml_service = MLService()
matching_service = MatchingService(ml_service)
adzuna_service = AdzunaService(
    app_id=os.getenv("ADZUNA_APP_ID"), app_key=os.getenv("ADZUNA_APP_KEY")
)


@jobs_bp.route("/")
def search():
    return render_template("search.html", page_name="Job Search")
@jobs_bp.route("/results")
def mock_results_page():
    results = {
    "success": True,
    "count": 3,
    "query_time_ms": 142,
    "results": [
        {
            "title": "Software Engineer (Backend)",
            "company": "OpenAI",
            "location": "San Francisco, CA",
            "salary_min": 130000,
            "salary_max": 180000,
            "description": "Work on high-performance backend systems that power our API platform and deploy cutting-edge models to production.",
            "url": "https://www.openai.com/careers/backend-engineer",
            "final_score": 96,
            "posted_date": "2025-11-05"
        },
        {
            "title": "Machine Learning Engineer",
            "company": "Google DeepMind",
            "location": "Mountain View, CA",
            "salary_min": 150000,
            "salary_max": 210000,
            "description": "Develop and optimize state-of-the-art machine learning algorithms for multimodal AI applications.",
            "url": "https://careers.google.com/jobs/ml-engineer-deepmind",
            "final_score": 91,
            "posted_date": "2025-11-03"
        },
        {
            "title": "Full Stack Developer",
            "company": "Blackhawk Network",
            "location": "Coppell, TX",
            "salary_min": 110000,
            "salary_max": 140000,
            "description": "Build and maintain scalable web applications integrating payment, gift card, and AI-powered recommendation systems.",
            "url": "https://blackhawknetwork.com/careers/fullstack-developer",
            "final_score": 88,
            "posted_date": "2025-11-07"
        }
    ]
}
    return render_template("results.html", page_name="Job Results", **results)

@jobs_bp.route("/results", methods=["POST"])
def search_jobs():
    start_time = time.time()

    data = request.get_json() or {}

    # Validate request
    is_valid, error = validate_search_request(data)
    if not is_valid:
        return jsonify({"success": False, "error": error}), 400

    # Fetch jobs from Adzuna
    jobs = adzuna_service.search_jobs(
        keywords=data.get("keywords", None),
        location=data.get("location", None),
        distance=data.get("distance", None),
        max_results=data.get("max_results", 50),
    )
    # process null searches
    if not jobs:
        results = {
            "success": True,
            "count": 0,
            "query_time_ms": int((time.time() - start_time)*1000),
            "results": []
        }
    return render_template("results.html", page_name="Job Results", **results)

    # Rank jobs using ML
    matched_jobs = matching_service.rank_jobs(
        user_data=data, jobs=jobs, top_k=data.get("max_results", 20)
    )

    # Format response
    query_time = int((time.time() - start_time) * 1000)

    results = {
            "success": True,
            "count": len(matched_jobs),
            "query_time_ms": query_time,
            "results": [job.to_dict() for job in matched_jobs]
    }

    logger.info("search_ok", extra={"ctx": {"count": results["count"], "query_time_ms": query_time}})

    return render_template("results.html", page_name="Job Results", **results)
4
