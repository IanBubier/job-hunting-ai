"""Adzuna API integration service."""

from typing import List, Dict, Optional
import os
import time
import requests
from backend.models.job_model import Job
import logging

logger = logging.getLogger(__name__)


def _env_flag(name: str, default: str = "1") -> bool:
    """Interpret common truthy/falsey env values."""
    val = os.getenv(name, default)
    return str(val).strip().lower() in ("1", "true", "yes", "on")


class AdzunaService:
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_key: Optional[str] = None,
        country: str = "us",
    ):
        self.app_id = app_id or os.getenv("ADZUNA_APP_ID")
        self.app_key = app_key or os.getenv("ADZUNA_APP_KEY")
        self.country = (country or os.getenv("ADZUNA_COUNTRY", "us")).lower()

        # USE_MOCK from env (default = 1/mock). Set USE_MOCK=0 to go LIVE.
        self.use_mock = _env_flag("USE_MOCK", default="1")
        if not self.app_id or not self.app_key:
            self.use_mock = True

        self.rate_limit_delay = 0.1  # seconds between requests
        self.last_request_time = 0.0

    def _rate_limit(self) -> None:
        """Simple rate limiting to respect external API limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def search_jobs(
        self,
        keywords: Optional[str],
        location: Optional[str],
        distance: Optional[str],
        max_results: int = 50,
        page: int = 1,
    ) -> List[Job]:
        """
        Search for jobs using the Adzuna API.
        Returns a list of `Job` objects. On error returns an empty list.
        """
        if self.use_mock:
            return []

        self._rate_limit()

        url = f"{self.BASE_URL}/{self.country}/search/{page}"

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": min(max_results, 50),
            "what": keywords,
            "where": location,
            "distance": distance,
        }

        try:
            response = requests.get(
                url,
                params=params,
                headers={"content-type": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return self._parse_jobs(data.get("results", []))

        except requests.exceptions.RequestException:
            logger.exception(
                "adzuna.fetch_failed", extra={"ctx": {"url": url, "params": params}}
            )
            return []

    def _parse_jobs(self, raw_jobs: List[Dict]) -> List[Job]:
        """Convert Adzuna API response items to `Job` objects."""
        jobs: List[Job] = []

        for raw_job in raw_jobs:
            job = Job(
                id=raw_job.get("id", ""),
                title=raw_job.get("title", "Untitled"),
                company=(raw_job.get("company", {}).get("display_name", "Unknown")),
                location=(raw_job.get("location", {}).get("display_name", "Unknown")),
                description=raw_job.get("description", ""),
                salary_min=raw_job.get("salary_min"),
                salary_max=raw_job.get("salary_max"),
                url=raw_job.get("redirect_url", ""),
                posted_date=raw_job.get("created", ""),
            )
            jobs.append(job)

        return jobs
