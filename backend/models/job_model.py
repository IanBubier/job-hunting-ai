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
        return self.__dict__


@dataclass
class MatchedJob:
    job: Job
    similarity_score: float
    matching_skills: List[str]

    def to_dict(self):
        data = self.job.to_dict()
        data.update(
            {
                "match_score": round(self.similarity_score * 100, 2),
                "matching_skills": self.matching_skills,
            }
        )
        return data
