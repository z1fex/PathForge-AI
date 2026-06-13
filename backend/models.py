"""Pydantic schemas — the typed mirror of spec/API_CONTRACT.md.
Field names here ARE the contract. Do not rename without updating the contract."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# ---------- /api/health ----------
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0"
    mock_mode: bool = False


# ---------- /api/roadmap request ----------
class RoadmapRequest(BaseModel):
    # job_title may be omitted when mock=true (mock falls back to a default title).
    job_title: Optional[str] = None
    mock: bool = False


# ---------- nested roadmap shapes ----------
class SalaryRange(BaseModel):
    min: int = 0
    max: int = 0


class ExpectedSalary(BaseModel):
    min: int = 0
    max: int = 0
    currency: str = "USD"
    note: str = ""


class Milestone(BaseModel):
    order: int
    title: str
    duration: str
    description: str
    skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    expected_salary: ExpectedSalary = Field(default_factory=ExpectedSalary)


class Skill(BaseModel):
    name: str
    level: str = "Beginner"
    why: str = ""


class Certification(BaseModel):
    name: str
    provider: str = ""
    url: str = ""
    free: bool = False


class Company(BaseModel):
    name: str
    role: str = ""
    location: str = ""
    url: str = ""
    source: str = ""


class Course(BaseModel):
    title: str
    provider: str = ""
    url: str = ""
    free: bool = False


class YouTubeRec(BaseModel):
    channel: str
    title: str = ""
    url: str = ""
    why: str = ""


class SalaryOverview(BaseModel):
    entry: SalaryRange = Field(default_factory=SalaryRange)
    mid: SalaryRange = Field(default_factory=SalaryRange)
    senior: SalaryRange = Field(default_factory=SalaryRange)
    currency: str = "USD"
    sources: List[str] = Field(default_factory=list)


# ---------- /api/roadmap response ----------
class RoadmapResponse(BaseModel):
    job_title: str
    summary: str = ""
    background_required: str = ""
    milestones: List[Milestone] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    companies_hiring: List[Company] = Field(default_factory=list)
    recommended_courses: List[Course] = Field(default_factory=list)
    youtube: List[YouTubeRec] = Field(default_factory=list)
    salary_overview: SalaryOverview = Field(default_factory=SalaryOverview)
    generated_at: str = ""
    mock: bool = False


# ---------- /api/chat ----------
class ChatRequest(BaseModel):
    job_title: Optional[str] = None
    message: str
    history: List[dict] = Field(default_factory=list)


class ChatSource(BaseModel):
    title: str = ""
    url: str = ""


class ChatResponse(BaseModel):
    answer: str
    sources: List[ChatSource] = Field(default_factory=list)


# ---------- shared error shape ----------
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None