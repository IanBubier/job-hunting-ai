from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Job:
    id: str
    title: str
    company: str
    location: str
    description: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    url: str = ""
    posted_date: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "salary": self.format_salary(),
            "url": self.url,
            "posted_date": self.posted_date,
        }

    def format_salary(self):
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,.0f} - ${self.salary_max:,.0f}"
        return "Not specified"


@dataclass
class MatchedJob:
    job: Job
    similarity_score: float
    matching_skills: List[str]
    final_score: float

    def to_dict(self):
        return {
            **self.job.to_dict(),
            "similarity_score": round(self.similarity_score * 100, 2),
            "matching_skills": self.matching_skills,
            "final_score": round(self.final_score * 100, 2),
        }
