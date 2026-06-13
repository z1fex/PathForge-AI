"""Offline, contract-valid sample payload for /api/roadmap.

Powers two things:
  1) Mock-mode ({"mock": true} or MOCK=1) so the partner's frontend can integrate
     before live calls exist — and as a demo safety net if Gemini is down.
  2) The graceful fallback when the live roadmap engine hard-fails.

Self-contained: requires NO API keys and makes NO network calls.
"""
from __future__ import annotations

from typing import Any, Dict


def mock_roadmap(job_title: str = "Data Scientist") -> Dict[str, Any]:
    """Return a full, contract-shaped roadmap dict. `generated_at`/`mock` are
    stamped by the caller (main.py) so this stays a pure data factory."""
    return {
        "job_title": job_title or "Data Scientist",
        "summary": (
            "A Data Scientist turns raw data into decisions — cleaning data, building "
            "models, and communicating insight. The path runs from Python + statistics "
            "foundations to deployed ML; it is very achievable self-taught with a portfolio."
        ),
        "background_required": (
            "No specific degree is required to start. A background in CS, statistics, or a "
            "quantitative field helps, but a strong project portfolio and demonstrated SQL/Python "
            "skill increasingly outweigh formal credentials for entry-level roles."
        ),
        "milestones": [
            {
                "order": 1,
                "title": "Foundations: Python, Stats & SQL",
                "duration": "0-3 months",
                "description": "Learn Python, core statistics, and SQL. Manipulate data with pandas and pull data with queries.",
                "skills": ["Python", "Statistics", "SQL", "pandas"],
                "certifications": ["Google Data Analytics"],
                "expected_salary": {"min": 0, "max": 45000, "currency": "USD", "note": "intern/entry while learning"},
            },
            {
                "order": 2,
                "title": "Data Analysis & Visualization",
                "duration": "3-6 months",
                "description": "Explore datasets, build dashboards, and tell stories with data using matplotlib, seaborn, and BI tools.",
                "skills": ["Exploratory Data Analysis", "Data Visualization", "matplotlib", "Tableau"],
                "certifications": [],
                "expected_salary": {"min": 50000, "max": 70000, "currency": "USD", "note": "junior data analyst roles"},
            },
            {
                "order": 3,
                "title": "Machine Learning Core",
                "duration": "6-10 months",
                "description": "Master supervised/unsupervised learning, model evaluation, and feature engineering with scikit-learn.",
                "skills": ["scikit-learn", "Machine Learning", "Feature Engineering", "Model Evaluation"],
                "certifications": [],
                "expected_salary": {"min": 70000, "max": 95000, "currency": "USD", "note": "entry data scientist"},
            },
            {
                "order": 4,
                "title": "Portfolio & Specialization",
                "duration": "10-14 months",
                "description": "Ship 3-4 end-to-end projects (NLP, forecasting, or CV). Specialize and publish on GitHub.",
                "skills": ["Project Design", "Git/GitHub", "Deep Learning", "Storytelling"],
                "certifications": ["DeepLearning.AI Machine Learning Specialization"],
                "expected_salary": {"min": 85000, "max": 110000, "currency": "USD", "note": "competitive entry/mid"},
            },
            {
                "order": 5,
                "title": "Production & Hired",
                "duration": "14-18 months",
                "description": "Deploy models, learn MLOps basics, interview prep on SQL/ML system design, and land the role.",
                "skills": ["MLOps", "Cloud (AWS/GCP)", "A/B Testing", "Interviewing"],
                "certifications": [],
                "expected_salary": {"min": 95000, "max": 130000, "currency": "USD", "note": "mid-level data scientist"},
            },
        ],
        "skills": [
            {"name": "Python", "level": "Beginner", "why": "Core language for data manipulation, modeling, and automation."},
            {"name": "SQL", "level": "Beginner", "why": "Almost every data job requires pulling and joining data from databases."},
            {"name": "Statistics", "level": "Intermediate", "why": "Underpins experiment design, inference, and trustworthy models."},
            {"name": "Machine Learning", "level": "Intermediate", "why": "Building predictive models is the defining skill of the role."},
            {"name": "Data Visualization", "level": "Intermediate", "why": "Insight is worthless if you can't communicate it to stakeholders."},
            {"name": "MLOps", "level": "Advanced", "why": "Turning models into reliable production systems separates senior talent."},
        ],
        "certifications": [
            {"name": "Google Data Analytics", "provider": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-data-analytics", "free": False},
            {"name": "DeepLearning.AI Machine Learning Specialization", "provider": "Coursera", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "free": False},
            {"name": "IBM Data Science Professional Certificate", "provider": "Coursera", "url": "https://www.coursera.org/professional-certificates/ibm-data-science", "free": False},
        ],
        "companies_hiring": [
            {"name": "Spotify", "role": "Junior Data Scientist", "location": "Remote (EU)", "url": "https://www.lifeatspotify.com/jobs", "source": "mock"},
            {"name": "Zalando", "role": "Data Scientist (Entry)", "location": "Berlin, DE", "url": "https://jobs.zalando.com", "source": "mock"},
            {"name": "Acme Analytics", "role": "Data Scientist I", "location": "Remote", "url": "https://example.com/jobs", "source": "mock"},
        ],
        "recommended_courses": [
            {"title": "Python for Everybody", "provider": "freeCodeCamp / Coursera", "url": "https://www.coursera.org/specializations/python", "free": True},
            {"title": "Intro to Machine Learning", "provider": "Kaggle Learn", "url": "https://www.kaggle.com/learn/intro-to-machine-learning", "free": True},
            {"title": "SQL for Data Science", "provider": "Coursera (UC Davis)", "url": "https://www.coursera.org/learn/sql-for-data-science", "free": True},
        ],
        "youtube": [
            {"channel": "StatQuest with Josh Starmer", "title": "Machine Learning playlist", "url": "https://www.youtube.com/c/joshstarmer", "why": "Best intuition for the statistics and ML behind the models."},
            {"channel": "freeCodeCamp.org", "title": "Data Science full courses", "url": "https://www.youtube.com/c/Freecodecamp", "why": "Free multi-hour project-based courses end to end."},
            {"channel": "Ken Jee", "title": "Data Science career advice", "url": "https://www.youtube.com/c/KenJee1", "why": "Practical portfolio and job-hunt guidance for breaking in."},
        ],
        "salary_overview": {
            "entry": {"min": 60000, "max": 90000},
            "mid": {"min": 95000, "max": 130000},
            "senior": {"min": 140000, "max": 200000},
            "currency": "USD",
            "sources": ["https://www.levels.fyi/", "https://www.glassdoor.com/Salaries/data-scientist-salary-SRCH_KO0,14.htm"],
        },
    }
