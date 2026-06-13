"""End-to-end API tests (Agent 1).

Offline by design: every test runs without network or API keys. The live roadmap
engine is monkeypatched so we test the spine + assembly + graceful-degrade paths
deterministically — Gemini quality is verified by the manual curl in the brief.

Run from app/:  python -m pytest tests/test_api.py -v
"""
import os
import sys

# Make `app/` importable whether pytest is run from app/ or the repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

import main  # noqa: E402

client = TestClient(main.app)

# Every top-level key the contract promises for /api/roadmap.
CONTRACT_KEYS = {
    "job_title", "summary", "background_required", "milestones", "skills",
    "certifications", "companies_hiring", "recommended_courses", "youtube",
    "salary_overview", "generated_at", "mock",
}


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["version"]
    assert isinstance(body["mock_mode"], bool)


def test_roadmap_mock_is_contract_valid():
    r = client.post("/api/roadmap", json={"mock": True})
    assert r.status_code == 200
    body = r.json()
    assert CONTRACT_KEYS.issubset(body.keys())
    assert body["mock"] is True
    assert body["generated_at"]
    # Substance, not just shape.
    assert len(body["milestones"]) >= 4
    m0 = body["milestones"][0]
    assert {"order", "title", "duration", "description", "skills", "certifications", "expected_salary"}.issubset(m0)
    assert {"min", "max", "currency", "note"}.issubset(m0["expected_salary"])
    assert len(body["skills"]) >= 1
    assert {"entry", "mid", "senior", "currency"}.issubset(body["salary_overview"])


def test_roadmap_missing_job_title_is_400():
    r = client.post("/api/roadmap", json={})
    assert r.status_code == 400
    assert "error" in r.json()


def test_roadmap_live_assembly_shape(monkeypatch):
    """Patch the engine; confirm assembly produces a full contract payload even
    when Agents 2/3 are absent (stubs return []/{})."""
    fake_core = {
        "summary": "S",
        "background_required": "B",
        "milestones": [
            {"order": 1, "title": "Foundations", "duration": "0-3 months",
             "description": "d", "skills": ["Python"], "certifications": [],
             "expected_salary": {"min": 0, "max": 0, "currency": "USD", "note": ""}},
        ],
        "skills": [{"name": "Python", "level": "Beginner", "why": "core"}],
        "certifications": [],
    }
    monkeypatch.setattr(main, "generate_roadmap", lambda jt: fake_core)
    # Isolate Agent 1's assembly from whatever Agents 2/3 currently do (present or not):
    # pin every sub-call to an empty result so this stays fast + deterministic.
    monkeypatch.setattr(main, "get_companies_hiring", lambda jt: [])
    monkeypatch.setattr(main, "get_salary_overview", lambda jt: {})
    monkeypatch.setattr(main, "get_milestone_salaries", lambda jt, ms: ms)
    monkeypatch.setattr(main, "get_courses", lambda jt, sk: [])
    monkeypatch.setattr(main, "get_youtube", lambda jt, sk: [])

    r = client.post("/api/roadmap", json={"job_title": "Data Scientist"})
    assert r.status_code == 200
    body = r.json()
    assert CONTRACT_KEYS.issubset(body.keys())
    assert body["mock"] is False
    assert body["job_title"] == "Data Scientist"
    assert body["summary"] == "S"
    # Empty sub-results assemble cleanly into the contract, not a crash.
    assert body["companies_hiring"] == []
    assert body["recommended_courses"] == []
    assert isinstance(body["youtube"], list)


def test_roadmap_never_500s_when_submodule_raises(monkeypatch):
    """Even if an Agent-2/3 function blows up, the endpoint degrades, not 500s."""
    monkeypatch.setattr(main, "generate_roadmap", lambda jt: {
        "summary": "S", "background_required": "B",
        "milestones": [{"order": 1, "title": "t", "duration": "d", "description": "d",
                        "skills": [], "certifications": [],
                        "expected_salary": {"min": 0, "max": 0, "currency": "USD", "note": ""}}],
        "skills": [], "certifications": [],
    })

    def boom(*a, **k):
        raise RuntimeError("simulated sub-module failure")

    # Every sub-call raises -> _safe() must catch all of them and degrade.
    monkeypatch.setattr(main, "get_companies_hiring", boom)
    monkeypatch.setattr(main, "get_salary_overview", boom)
    monkeypatch.setattr(main, "get_milestone_salaries", boom)
    monkeypatch.setattr(main, "get_courses", boom)
    monkeypatch.setattr(main, "get_youtube", boom)

    r = client.post("/api/roadmap", json={"job_title": "DevOps Engineer"})
    assert r.status_code == 200
    body = r.json()
    assert body["companies_hiring"] == []
    assert body["salary_overview"]["currency"] == "USD"  # default-filled by contract model


def test_roadmap_engine_failure_falls_back_to_mock(monkeypatch):
    def boom(jt):
        raise RuntimeError("gemini down")

    monkeypatch.setattr(main, "generate_roadmap", boom)
    r = client.post("/api/roadmap", json={"job_title": "Anything"})
    assert r.status_code == 200
    body = r.json()
    assert body["mock"] is True            # honest: this is the fallback payload
    assert len(body["milestones"]) >= 4


def test_roadmap_drops_malformed_subitems_not_500(monkeypatch):
    """A teammate returning a course with no `title` must drop that one row,
    not 500 the whole roadmap. Valid rows survive."""
    monkeypatch.setattr(main, "generate_roadmap", lambda jt: {
        "summary": "S", "background_required": "B",
        "milestones": [{"order": 1, "title": "t", "duration": "d", "description": "d",
                        "skills": [], "certifications": [],
                        "expected_salary": {"min": 0, "max": 0, "currency": "USD", "note": ""}}],
        "skills": [], "certifications": [],
    })
    monkeypatch.setattr(main, "get_companies_hiring", lambda jt: [])
    monkeypatch.setattr(main, "get_salary_overview", lambda jt: {})
    monkeypatch.setattr(main, "get_milestone_salaries", lambda jt, ms: ms)
    monkeypatch.setattr(main, "get_youtube", lambda jt, sk: [])
    # One valid course + one malformed (missing required `title`).
    monkeypatch.setattr(main, "get_courses", lambda jt, sk: [
        {"title": "Good Course", "provider": "X", "url": "https://x", "free": True},
        {"provider": "broken-no-title"},
    ])

    r = client.post("/api/roadmap", json={"job_title": "Data Scientist"})
    assert r.status_code == 200
    body = r.json()
    titles = [c["title"] for c in body["recommended_courses"]]
    assert titles == ["Good Course"]  # bad row dropped, good row kept


def test_chat_stub_when_no_webhook(monkeypatch):
    monkeypatch.delenv("N8N_WEBHOOK_URL", raising=False)
    r = client.post("/api/chat", json={"job_title": "Data Scientist", "message": "hi", "history": []})
    assert r.status_code == 200
    body = r.json()
    assert "answer" in body and isinstance(body["sources"], list)
