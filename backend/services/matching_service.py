"""Matching service implementation based on the design doc."""
from typing import List, Dict
import re

from models.job_model import Job, MatchedJob


class MatchingService:
    def __init__(self, ml_service):
        self.ml_service = ml_service

    def create_user_profile(
        self, skills: List[str], keywords: str, experience: str
    ) -> str:
        """Create comprehensive user profile text for embedding."""
        profile_parts = []

        if skills:
            profile_parts.append(f"Skills: {', '.join(skills)}")

        if keywords:
            profile_parts.append(f"Looking for: {keywords}")

        experience_map = {
            'entry': 'Entry level position, 0-2 years experience',
            'mid': 'Mid-level position, 3-5 years experience',
            'senior': 'Senior position, 5+ years experience'
        }
        profile_parts.append(experience_map.get(experience, ''))

        return ' '.join([p for p in profile_parts if p])

    def create_job_profile(self, job: Job) -> str:
        """Create comprehensive job description for embedding."""
        return f"{job.title} at {job.company}. {job.description[:500]}"

    def extract_matching_skills(
        self, user_skills: List[str], job_description: str
    ) -> List[str]:
        """Find which user skills appear in job description."""
        job_lower = job_description.lower()
        matching = []

        for skill in user_skills:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, job_lower):
                matching.append(skill)

        return matching

    def rank_jobs(
        self, user_data: Dict, jobs: List[Job], top_k: int = 20
    ) -> List[MatchedJob]:
        """Main ranking function using semantic similarity."""
        # Create user profile embedding
        user_profile = self.create_user_profile(
            user_data.get('skills', []),
            user_data.get('keywords', ''),
            user_data.get('experience', 'entry')
        )
        user_embedding = self.ml_service.encode_text(user_profile)

        # Create job embeddings
        job_profiles = [self.create_job_profile(job) for job in jobs]
        job_embeddings = [
            self.ml_service.encode_text(profile) for profile in job_profiles
        ]

        # Calculate similarities
        similarities = self.ml_service.batch_similarity(
            user_embedding, job_embeddings
        )

        # Create matched jobs with scores
        matched_jobs = []
        for job, similarity in zip(jobs, similarities):
            matching_skills = self.extract_matching_skills(
                user_data.get('skills', []), job.description
            )

            matched_jobs.append(MatchedJob(
                job=job,
                similarity_score=similarity,
                matching_skills=matching_skills
            ))

        # Sort by similarity and return top K
        matched_jobs.sort(key=lambda x: x.similarity_score, reverse=True)
        return matched_jobs[:top_k]
