import os
import time
from flask import Blueprint, jsonify, request

from backend.services.adzuna_service import AdzunaService
from backend.services.ml_service import MLService
from backend.services.matching_service import MatchingService
from backend.utils.validators import validate_search_request


job_bp = Blueprint("jobs", __name__)

# Initialize services (in production, replace with DI)
ml_service = MLService()
matching_service = MatchingService(ml_service)
adzuna_service = AdzunaService(
    app_id=os.getenv("ADZUNA_APP_ID"), app_key=os.getenv("ADZUNA_APP_KEY")
)


@job_bp.route("/search", methods=["POST"])
def search_jobs():
    start_time = time.time()

    try:
        data = request.get_json() or {}

        # Validate request
        is_valid, error = validate_search_request(data)
        if not is_valid:
            return jsonify({"success": False, "error": error}), 400

        # Fetch jobs from Adzuna
        jobs = adzuna_service.search_jobs(
            keywords=data.get("keywords", ""),
            location=data.get("location", ""),
            max_results=data.get("max_results", 50),
        )

        if not jobs:
            return jsonify(
                {
                    "success": True,
                    "count": 0,
                    "results": [],
                    "message": "No jobs found matching criteria",
                }
            )

        # Rank jobs using ML
        matched_jobs = matching_service.rank_jobs(
            user_data=data, jobs=jobs, top_k=data.get("max_results", 20)
        )

        # Format response
        query_time = int((time.time() - start_time) * 1000)

        return jsonify(
            {
                "success": True,
                "count": len(matched_jobs),
                "query_time_ms": query_time,
                "results": [job.to_dict() for job in matched_jobs],
            }
        )

    except Exception as e:
        print(f"Error in search endpoint: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                    },
                }
            ),
            500,
        )
