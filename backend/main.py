"""CareerPath backend — FastAPI spine (Agent 1).

Routes (see spec/API_CONTRACT.md):
  GET  /api/health    -> {status, version, mock_mode}
  POST /api/roadmap   -> full roadmap payload (assembles Agents 1+2+3)
  POST /api/chat      -> thin proxy to n8n RAG webhook (Agent 4), with stub fallback

Golden rule: /api/roadmap NEVER 500s because a sub-module failed. Every external
call is wrapped + bounded; on failure we substitute []/{} and continue. If the core
roadmap engine itself hard-fails, we serve the mock payload so the demo never dies.
"""
from __future__ import annotations

import concurrent.futures
import logging
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from mock_data import mock_roadmap
from models import (
    Certification,
    ChatRequest,
    ChatResponse,
    Company,
    Course,
    HealthResponse,
    Milestone,
    RoadmapRequest,
    RoadmapResponse,
    Skill,
    YouTubeRec,
)
from services.roadmap import generate_roadmap

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("careerpath")

VERSION = "1.0"
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=6)


# --------------------------------------------------------------------------- #
# Defensive imports of Agent 2 & 3 modules. Until they land (or if they break),
# fall back to no-op stubs so Agent 1 can build, test, and demo immediately.
# --------------------------------------------------------------------------- #
try:
    from services.jobs_salary import (  # type: ignore
        get_companies_hiring,
        get_milestone_salaries,
        get_salary_overview,
    )
except Exception as e:  # ImportError today, anything tomorrow
    log.warning("jobs_salary unavailable (%s) — using stubs", e)

    def get_companies_hiring(job_title: str) -> List[dict]:  # type: ignore
        return []

    def get_salary_overview(job_title: str) -> dict:  # type: ignore
        return {}

    def get_milestone_salaries(job_title: str, milestones: List[dict]) -> List[dict]:  # type: ignore
        return milestones

try:
    from services.learning import get_courses, get_youtube  # type: ignore
except Exception as e:
    log.warning("learning unavailable (%s) — using stubs", e)

    def get_courses(job_title: str, skills: List[str]) -> List[dict]:  # type: ignore
        return []

    def get_youtube(job_title: str, skills: List[str]) -> List[dict]:  # type: ignore
        return []


# --------------------------------------------------------------------------- #
# App
# --------------------------------------------------------------------------- #
app = FastAPI(title="PathForge AI", version=VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _mock_forced() -> bool:
    return os.getenv("MOCK", "0") == "1"


def _safe(fn: Callable[..., Any], default: Any, *args: Any, timeout: float = 12.0) -> Any:
    """Run a sub-module call with a hard timeout; on ANY failure return `default`.
    This is the wall between flaky sub-modules and our endpoint never 500ing."""
    try:
        future = _executor.submit(fn, *args)
        return future.result(timeout=timeout)
    except Exception as e:
        log.warning("sub-call %s failed (%s) — degrading to default", getattr(fn, "__name__", fn), e)
        return default


def _gather(future: "concurrent.futures.Future", default: Any, timeout: float = 20.0) -> Any:
    """Wait on an ALREADY-submitted future; on timeout/failure return `default`.
    Used to fan out sub-modules concurrently (submit all first, then gather)."""
    try:
        return future.result(timeout=timeout)
    except Exception as e:
        log.warning("sub-call failed (%s) — degrading to default", e)
        return default


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=VERSION, mock_mode=_mock_forced())


@app.post("/api/roadmap")
def roadmap(req: RoadmapRequest) -> JSONResponse:
    use_mock = req.mock or _mock_forced()
    job_title = (req.job_title or "").strip()

    if not use_mock and not job_title:
        return JSONResponse(
            status_code=400,
            content={"error": "job_title is required", "detail": "Send {\"job_title\": \"...\"} or {\"mock\": true}."},
        )

    # ---- Mock-mode: instant, offline, contract-valid ----
    if use_mock:
        payload = mock_roadmap(job_title or "Data Scientist")
        payload["generated_at"] = _now_iso()
        payload["mock"] = True
        return JSONResponse(content=_validate(payload))

    # ---- Live: core engine + assembly ----
    try:
        core = generate_roadmap(job_title)  # summary, background_required, milestones, skills, certs
    except Exception as e:
        # Core failed — serve mock so the frontend/demo never breaks. Still mark mock=true (honest).
        log.error("roadmap engine failed for %r (%s) — serving mock fallback", job_title, e)
        payload = mock_roadmap(job_title)
        payload["generated_at"] = _now_iso()
        payload["mock"] = True
        return JSONResponse(content=_validate(payload))

    skill_names = [s["name"] for s in core.get("skills", []) if isinstance(s, dict) and s.get("name")]
    milestones = core.get("milestones", [])

    # Fan out Agents 2 & 3 TRULY concurrently: submit all first, THEN gather.
    # (Previously these ran sequentially -> ~40s and starved get_courses of its window.)
    fut_companies = _executor.submit(get_companies_hiring, job_title)
    fut_salary = _executor.submit(get_salary_overview, job_title)
    fut_bands = _executor.submit(get_milestone_salaries, job_title, milestones)
    fut_courses = _executor.submit(get_courses, job_title, skill_names)
    fut_youtube = _executor.submit(get_youtube, job_title, skill_names)

    companies = _gather(fut_companies, [], timeout=20)
    salary_overview = _gather(fut_salary, {}, timeout=20)
    salary_bands = _gather(fut_bands, [], timeout=20)
    courses = _gather(fut_courses, [], timeout=25)
    youtube = _gather(fut_youtube, [], timeout=25)

    # Merge salary bands into each milestone's expected_salary — do NOT replace the
    # milestones (the old `milestones = get_milestone_salaries(...)` wiped title/duration
    # /description, so every milestone was dropped in validation -> empty roadmap).
    for ms, band in zip(milestones, salary_bands or []):
        if isinstance(ms, dict) and isinstance(band, dict):
            ms["expected_salary"] = {
                "min": band.get("min", 0),
                "max": band.get("max", 0),
                "currency": band.get("currency", "USD"),
                "note": band.get("note", ""),
            }

    payload: Dict[str, Any] = {
        "job_title": job_title,
        "summary": core.get("summary", ""),
        "background_required": core.get("background_required", ""),
        "milestones": milestones,
        "skills": core.get("skills", []),
        "certifications": core.get("certifications", []),
        "companies_hiring": companies or [],
        "recommended_courses": courses or [],
        "youtube": youtube or [],
        "salary_overview": salary_overview or {},
        "generated_at": _now_iso(),
        "mock": False,
    }
    return JSONResponse(content=_validate(payload))


def _validate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Coerce the assembled dict through the Pydantic contract so the frontend
    always receives every field in the right shape (fills defaults for gaps).

    Hardened: a malformed item from a teammate's module (e.g. a course missing
    `title`) must NOT 500 the whole response. We try the full payload first; on a
    validation error we drop the offending items from each list and retry, so a
    single bad row degrades to fewer rows instead of a crashed endpoint."""
    try:
        return RoadmapResponse(**payload).model_dump()
    except Exception as e:
        log.warning("payload validation failed (%s) — sanitizing sub-lists", e)
        item_models = {
            "milestones": Milestone, "skills": Skill, "certifications": Certification,
            "companies_hiring": Company, "recommended_courses": Course, "youtube": YouTubeRec,
        }
        clean = dict(payload)
        for field, Model in item_models.items():
            kept = []
            for item in clean.get(field, []) or []:
                try:
                    kept.append(Model(**item).model_dump())
                except Exception:
                    continue  # drop just this bad row
            clean[field] = kept
        try:
            return RoadmapResponse(**clean).model_dump()
        except Exception as e2:  # last resort: never 500 — serve mock instead
            log.error("payload unrecoverable (%s) — serving mock", e2)
            fallback = mock_roadmap(payload.get("job_title") or "Data Scientist")
            fallback["generated_at"] = _now_iso()
            fallback["mock"] = True
            return RoadmapResponse(**fallback).model_dump()


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    webhook = os.getenv("N8N_WEBHOOK_URL", "").strip()
    stub = ChatResponse(answer="Chat is warming up — try again shortly.", sources=[])

    if not webhook:
        return stub

    try:
        resp = httpx.post(
            webhook,
            json={"job_title": req.job_title, "message": req.message, "history": req.history},
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        # Pass through n8n's shape; coerce to contract so the frontend never breaks.
        return ChatResponse(answer=data.get("answer", ""), sources=data.get("sources", []) or [])
    except Exception as e:
        log.warning("chat proxy to n8n failed (%s) — returning stub", e)
        return stub


@app.get("/")
def root() -> dict:
    return {"name": "PathForge AI", "version": VERSION, "docs": "/docs", "health": "/api/health"}