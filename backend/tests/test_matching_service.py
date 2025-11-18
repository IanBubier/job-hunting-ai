import pytest
from backend.services.ml_service import MLService
from backend.services.matching_service import MatchingService
from backend.models.job_model import Job, MatchedJob  # Import the Job models


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(scope="module")
def ml_service():
    """
    Fixture that creates ML service once for all tests
    Using scope="module" so model is loaded only once (faster tests)
    """
    return MLService()


@pytest.fixture
def matching_service(ml_service):
    """
    Fixture to create matching service
    """
    return MatchingService(ml_service)


@pytest.fixture
def sample_jobs():
    """
    Fixture with sample Job objects
    """
    return [
        Job(
            id="1",
            title="Junior Data Scientist",
            company="Tech Corp",
            location="San Francisco, CA",
            description="Python and Machine Learning required. Entry level position.",
            salary_min=80000.0,
            salary_max=100000.0,
            url="https://example.com/job1",
            posted_date="2025-10-01",
        ),
        Job(
            id="2",
            title="Senior Java Developer",
            company="Enterprise Inc",
            location="New York, NY",
            description="Java, Spring Boot, and microservices. 5+ years experience.",
            salary_min=120000.0,
            salary_max=150000.0,
            url="https://example.com/job2",
            posted_date="2025-10-02",
        ),
        Job(
            id="3",
            title="Frontend Developer",
            company="Web Agency",
            location="Austin, TX",
            description="React, JavaScript, and CSS. Mid-level position.",
            salary_min=90000.0,
            salary_max=110000.0,
            url="https://example.com/job3",
            posted_date="2025-10-03",
        ),
    ]


# ============================================================================
# TEST CREATE_USER_PROFILE
# ============================================================================


class TestCreateUserProfile:
    """
    Test user profile text generation
    """

    def test_basic_profile_creation(self, matching_service):
        """
        Test basic profile with all fields
        """
        skills = ["Python", "SQL", "Docker"]
        keywords = "Backend Developer"
        experience = "4"

        profile = matching_service.create_user_profile(skills, keywords, experience)

        assert "Python" in profile
        assert "SQL" in profile
        assert "Docker" in profile
        assert "Backend Developer" in profile
        assert isinstance(profile, str)

    def test_profile_with_empty_skills(self, matching_service):
        """
        Test profile creation with no skills
        """
        skills = []
        keywords = "Data Scientist"
        experience = "1"

        profile = matching_service.create_user_profile(skills, keywords, experience)

        assert "Data Scientist" in profile
        assert profile != ""

    def test_experience_level_mapping(self, matching_service):
        """
        Test all experience levels are properly mapped to descriptive text
        """
        skills = ["Python"]
        keywords = "Developer"

        # Test entry level
        profile_entry = matching_service.create_user_profile(skills, keywords, "1")
        assert "entry" in profile_entry.lower() or "0-2" in profile_entry

        # Test mid level
        profile_mid = matching_service.create_user_profile(skills, keywords, "4")
        assert "mid" in profile_mid.lower() or "3-5" in profile_mid

        # Test senior level
        profile_senior = matching_service.create_user_profile(skills, keywords, "10")
        assert "senior" in profile_senior.lower() or "5+" in profile_senior


# ============================================================================
# TEST CREATE_JOB_PROFILE
# ============================================================================


class TestCreateJobProfile:
    """
    Test job profile text generation
    """

    def test_basic_job_profile(self, matching_service):
        """
        Test basic job profile creation using Job object
        """
        job = Job(
            id="1",
            title="Senior Python Developer",
            company="Tech Corp",
            location="San Francisco, CA",
            description="We are looking for an experienced Python developer...",
            salary_min=100000.0,
            salary_max=130000.0,
            url="https://example.com/job1",
            posted_date="2025-10-01",
        )

        profile = matching_service.create_job_profile(job)

        assert job.title in profile
        assert job.company in profile
        assert job.description in profile
        assert isinstance(profile, str)

    def test_long_description_truncation(self, matching_service):
        """
        Test that long descriptions are truncated
        """
        job = Job(
            id="1",
            title="Developer",
            company="Company",
            location="City, ST",
            description="X" * 1000,  # Very long description
            salary_min=80000.0,
            salary_max=100000.0,
            url="https://example.com/job1",
            posted_date="2025-10-01",
        )

        profile = matching_service.create_job_profile(job)

        # Should be truncated (500 chars description + title + company)
        assert len(profile) < 600

    def test_short_description_not_truncated(self, matching_service):
        """
        Test that short descriptions are kept intact
        """
        job = Job(
            id="1",
            title="Developer",
            company="Company",
            location="City, ST",
            description="Short description here",
            salary_min=80000.0,
            salary_max=100000.0,
            url="https://example.com/job1",
            posted_date="2025-10-01",
        )

        profile = matching_service.create_job_profile(job)

        assert job.description in profile

    def test_job_profile_with_all_fields(self, matching_service):
        """
        Test that profile is generated even with optional fields as None
        """
        job = Job(
            id="1",
            title="Developer",
            company="Company",
            location="Remote",
            description="Remote developer position",
            salary_min=None,  # Optional field
            salary_max=None,  # Optional field
            url="https://example.com/job1",
            posted_date="2025-10-01",
        )

        profile = matching_service.create_job_profile(job)

        assert isinstance(profile, str)
        assert len(profile) > 0


# ============================================================================
# TEST EXTRACT_MATCHING_SKILLS
# ============================================================================


class TestExtractMatchingSkills:
    """
    Test skill extraction from job descriptions
    """

    def test_basic_skill_matching(self, matching_service):
        """
        Test exact skill matches
        """
        user_skills = ["Python", "SQL", "JavaScript"]
        job_description = "We need Python and SQL experience."

        matching = matching_service.extract_matching_skills(
            user_skills, job_description
        )

        assert "Python" in matching
        assert "SQL" in matching
        assert "JavaScript" not in matching

    def test_case_insensitive_matching(self, matching_service):
        """
        Test case insensitivity
        """
        user_skills = ["Python", "React"]
        job_description = "PYTHON and react experience required."

        matching = matching_service.extract_matching_skills(
            user_skills, job_description
        )

        assert len(matching) == 2

    def test_special_characters(self, matching_service):
        """
        Test skills with special characters
        """
        user_skills = ["C++", "C#", ".NET"]
        job_description = "C++, C# and .NET developer needed."

        matching = matching_service.extract_matching_skills(
            user_skills, job_description
        )

        assert "C++" in matching
        assert "C#" in matching
        assert ".NET" in matching

    def test_multi_word_skills(self, matching_service):
        """
        Test multi-word skills
        """
        user_skills = ["Machine Learning", "Data Science"]
        job_description = "Machine Learning and Data Science experience required."

        matching = matching_service.extract_matching_skills(
            user_skills, job_description
        )

        assert "Machine Learning" in matching
        assert "Data Science" in matching


# ============================================================================
# TEST RANK_JOBS (MAIN FUNCTIONALITY)
# ============================================================================


class TestRankJobs:
    """
    Test the main ranking functionality
    """

    def test_basic_ranking(self, matching_service, sample_jobs):
        """
        Test basic job ranking returns correct structure
        """
        user_data = {
            "skills": ["Python", "Machine Learning"],
            "keywords": "Data Scientist",
            "experience": "1",
        }

        ranked = matching_service.rank_jobs(user_data, sample_jobs[:2], top_k=2)

        # Check that MatchedJob objects are returned
        assert len(ranked) == 2
        assert all(isinstance(job, MatchedJob) for job in ranked)

        # Check structure
        for matched_job in ranked:
            assert isinstance(matched_job.job, Job)
            assert isinstance(matched_job.similarity_score, float)
            assert isinstance(matched_job.matching_skills, list)
            assert isinstance(matched_job.final_score, float)
            assert 0 <= matched_job.similarity_score <= 1
            assert 0 <= matched_job.final_score <= 1

    def test_ranking_order(self, matching_service):
        """
        Test that relevant jobs are ranked higher
        """
        user_data = {
            "skills": ["Python", "Machine Learning", "Data Analysis"],
            "keywords": "Data Scientist",
            "experience": "1",
        }

        jobs = [
            Job(
                id="1",
                title="Senior Java Architect",
                company="Big Corp",
                location="NYC",
                description="Java enterprise architecture experience required.",
                salary_min=150000.0,
                salary_max=180000.0,
                url="https://example.com/job1",
                posted_date="2025-10-01",
            ),
            Job(
                id="2",
                title="Junior Data Scientist",
                company="ML Startup",
                location="SF",
                description="Python, Machine Learning, and Data Analysis. "
                "Entry level position.",
                salary_min=80000.0,
                salary_max=100000.0,
                url="https://example.com/job2",
                posted_date="2025-10-02",
            ),
            Job(
                id="3",
                title="Frontend Developer",
                company="Web Agency",
                location="Austin",
                description="React and JavaScript experience needed.",
                salary_min=90000.0,
                salary_max=110000.0,
                url="https://example.com/job3",
                posted_date="2025-10-03",
            ),
        ]

        ranked = matching_service.rank_jobs(user_data, jobs, top_k=3)

        # The Data Scientist job should be ranked first
        assert ranked[0].job.id == "2"
        assert ranked[0].similarity_score > ranked[1].similarity_score
        assert ranked[0].similarity_score > ranked[2].similarity_score

    def test_top_k_limiting(self, matching_service):
        """
        Test that top_k parameter limits results
        """
        user_data = {"skills": ["Python"], "keywords": "Developer", "experience": "3"}

        jobs = [
            Job(
                id=str(i),
                title=f"Python Developer {i}",
                company="Company",
                location="Remote",
                description="Python developer needed",
                salary_min=80000.0,
                salary_max=100000.0,
                url=f"https://example.com/job{i}",
                posted_date="2025-10-01",
            )
            for i in range(50)
        ]

        ranked_5 = matching_service.rank_jobs(user_data, jobs, top_k=5)
        assert len(ranked_5) == 5

        ranked_10 = matching_service.rank_jobs(user_data, jobs, top_k=10)
        assert len(ranked_10) == 10

        ranked_20 = matching_service.rank_jobs(user_data, jobs, top_k=20)
        assert len(ranked_20) == 20

    def test_matching_skills_extracted(self, matching_service):
        """
        Test that matching skills are properly extracted in results
        """
        user_data = {
            "skills": ["Python", "Docker", "AWS"],
            "keywords": "Backend Developer",
            "experience": "4",
        }

        jobs = [
            Job(
                id="1",
                title="Backend Developer",
                company="Tech Co",
                location="SF",
                description="We need Python and Docker experience. AWS is a plus.",
                salary_min=100000.0,
                salary_max=120000.0,
                url="https://example.com/job1",
                posted_date="2025-10-01",
            )
        ]

        ranked = matching_service.rank_jobs(user_data, jobs, top_k=1)

        matching_skills = ranked[0].matching_skills

        assert "Python" in matching_skills
        assert "Docker" in matching_skills
        assert "AWS" in matching_skills

    def test_empty_jobs_list(self, matching_service):
        """
        Test with no jobs
        """
        user_data = {
            "skills": ["Python"],
            "keywords": "Developer",
            "experience": "1",
        }

        ranked = matching_service.rank_jobs(user_data, [], top_k=10)

        assert len(ranked) == 0
        assert ranked == []

    def test_matched_job_to_dict(self, matching_service):
        """
        Test that MatchedJob can be converted to dict for API response
        """
        user_data = {
            "skills": ["Python"],
            "keywords": "Developer",
            "experience": "1",
        }

        jobs = [
            Job(
                id="1",
                title="Python Developer",
                company="Company",
                location="Remote",
                description="Python experience required.",
                salary_min=80000.0,
                salary_max=100000.0,
                url="https://example.com/job1",
                posted_date="2025-10-01",
            )
        ]

        ranked = matching_service.rank_jobs(user_data, jobs, top_k=1)

        # Convert to dict (as would be done for API response)
        job_dict = ranked[0].to_dict()

        assert "id" in job_dict
        assert "title" in job_dict
        assert "company" in job_dict
        assert "similarity_score" in job_dict
        assert "matching_skills" in job_dict
        assert "final_score" in job_dict
        assert isinstance(job_dict["similarity_score"], (int, float))
        assert isinstance(job_dict["final_score"], (int, float))


# ============================================================================
# TEST JOB MODEL INTEGRATION
# ============================================================================


class TestJobModel:
    """
    Test Job model integration
    """

    def test_job_creation(self):
        """
        Test creating Job objects
        """
        job = Job(
            id="123",
            title="Software Engineer",
            company="Tech Corp",
            location="San Francisco, CA",
            description="Great opportunity",
            salary_min=100000.0,
            salary_max=130000.0,
            url="https://example.com/job",
            posted_date="2025-10-01",
        )

        assert job.id == "123"
        assert job.title == "Software Engineer"
        assert job.company == "Tech Corp"

    def test_job_to_dict(self):
        """
        Test Job.to_dict() method
        """
        job = Job(
            id="123",
            title="Developer",
            company="Company",
            location="Remote",
            description="Description",
            salary_min=80000.0,
            salary_max=100000.0,
            url="https://example.com/job",
            posted_date="2025-10-01",
        )

        job_dict = job.to_dict()

        assert job_dict["id"] == "123"
        assert job_dict["title"] == "Developer"
        assert job_dict["company"] == "Company"
        assert "salary" in job_dict
        assert "$80,000 - $100,000" in job_dict["salary"]

    def test_job_optional_salary(self):
        """
        Test Job with no salary info
        """
        job = Job(
            id="123",
            title="Developer",
            company="Company",
            location="Remote",
            description="Description",
            salary_min=None,
            salary_max=None,
            url="https://example.com/job",
            posted_date="2025-10-01",
        )

        job_dict = job.to_dict()
        assert job_dict["salary"] == "Not specified"

    def test_matched_job_creation(self):
        """
        Test MatchedJob creation
        """
        job = Job(
            id="1",
            title="Developer",
            company="Company",
            location="Remote",
            description="Python required",
            salary_min=80000.0,
            salary_max=100000.0,
            url="https://example.com/job",
            posted_date="2025-10-01",
        )

        matched_job = MatchedJob(
            job=job, similarity_score=0.85, matching_skills=["Python"], final_score=0.9
        )

        assert matched_job.job == job
        assert matched_job.similarity_score == 0.85
        assert matched_job.matching_skills == ["Python"]
        assert matched_job.final_score == 0.9

    def test_matched_job_to_dict(self):
        """
        Test MatchedJob.to_dict() includes all fields
        """
        job = Job(
            id="1",
            title="Developer",
            company="Company",
            location="Remote",
            description="Python required",
            salary_min=80000.0,
            salary_max=100000.0,
            url="https://example.com/job",
            posted_date="2025-10-01",
        )

        matched_job = MatchedJob(
            job=job,
            similarity_score=0.953,
            matching_skills=["Python", "SQL"],
            final_score=0.92,
        )

        matched_dict = matched_job.to_dict()

        # Should include all Job fields
        assert matched_dict["id"] == "1"
        assert matched_dict["title"] == "Developer"
        assert matched_dict["company"] == "Company"

        # Should include matching fields
        assert matched_dict["similarity_score"] == 95.3  # Rounded to 2 decimals
        assert matched_dict["matching_skills"] == ["Python", "SQL"]
        assert matched_dict["final_score"] == 92.0  # Rounded to 2 decimals


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """
    Integration tests for the full matching pipeline
    """

    def test_realistic_scenario_data_science(self, matching_service):
        """
        Test realistic data science job search scenario
        """
        user_data = {
            "skills": ["Python", "Machine Learning", "Pandas", "SQL"],
            "keywords": "Data Scientist Machine Learning",
            "experience": "1",
        }

        jobs = [
            Job(
                id="1",
                title="Junior Data Scientist",
                company="ML Startup",
                location="San Francisco, CA",
                description="Entry level data scientist position. Python, Pandas, SQL, "
                "and Machine Learning required.",
                salary_min=80000.0,
                salary_max=100000.0,
                url="https://example.com/job1",
                posted_date="2025-10-01",
            ),
            Job(
                id="2",
                title="Senior Backend Engineer",
                company="Enterprise Corp",
                location="New York, NY",
                description="Java and Spring Boot. 5+ years experience required.",
                salary_min=130000.0,
                salary_max=160000.0,
                url="https://example.com/job2",
                posted_date="2025-10-02",
            ),
            Job(
                id="3",
                title="Data Analyst",
                company="Analytics Co",
                location="Austin, TX",
                description="SQL and Excel. Python is a plus.",
                salary_min=70000.0,
                salary_max=85000.0,
                url="https://example.com/job3",
                posted_date="2025-10-03",
            ),
            Job(
                id="4",
                title="Machine Learning Engineer",
                company="AI Company",
                location="Seattle, WA",
                description="Machine Learning and Python experience. "
                "Entry level welcome.",
                salary_min=90000.0,
                salary_max=110000.0,
                url="https://example.com/job4",
                posted_date="2025-10-04",
            ),
        ]

        ranked = matching_service.rank_jobs(user_data, jobs, top_k=4)

        # Jobs 1 and 4 should be top ranked (data science focused)
        top_2_ids = {ranked[0].job.id, ranked[1].job.id}
        assert "1" in top_2_ids or "4" in top_2_ids

        # Job 2 (Java backend) should be ranked last
        assert ranked[-1].job.id == "2"

        # Top job should have high similarity
        assert ranked[0].similarity_score > 0.7
