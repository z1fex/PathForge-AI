"""Roadmap engine (Agent 1).

Turns a job title into {summary, background_required, milestones[], skills[],
certifications[]} via Gemini in JSON mode.

Implementation note: we call the Gemini REST endpoint directly with httpx instead
of the google-generativeai SDK. Reasons (see tasks/lessons.md):
  - The provided key format (AQ.*) authenticates cleanly via the `x-goog-api-key`
    header / `?key=` param on REST (verified 200), which the SDK does not assume.
  - Avoids grpc/protobuf install fragility on the bleeding-edge Python here.
Model name is read from GEMINI_MODEL (never hardcode 2.0 — it is limit:0 on this key).
On rate-limit / transient failure we retry once with GEMINI_MODEL_FALLBACK.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict

import httpx

try:  # prompts.py lives one level up; support both package and flat import
    from prompts import render_prompt
except ImportError:  # pragma: no cover
    from app.prompts import render_prompt  # type: ignore

_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
_TIMEOUT = 45.0  # generous: roadmap generation + model thinking

# Keys the engine is responsible for (the rest are filled by Agents 2 & 3 / assembly).
_REQUIRED_KEYS = ("summary", "background_required", "milestones", "skills", "certifications")


class RoadmapError(RuntimeError):
    """Raised when both the primary and fallback model fail to produce valid JSON."""


def _model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _fallback_model() -> str:
    return os.getenv("GEMINI_MODEL_FALLBACK", "gemini-2.5-flash-lite")


def _keys() -> list[str]:
    """Primary key, then the fallback key (different account) for 429/quota failover."""
    ks = [os.getenv("GEMINI_API_KEY", ""), os.getenv("GEMINI_API_KEY_FALLBACK", "")]
    return [k for k in ks if k]


def _call_gemini(model: str, prompt: str, key: str) -> Dict[str, Any]:
    """One REST call to Gemini in JSON mode. Returns the parsed JSON object.
    Raises on HTTP error, empty/blocked response, or non-JSON text."""
    if not key:
        raise RoadmapError("GEMINI_API_KEY is not set")

    url = f"{_BASE}/{model}:generateContent"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7,
            "maxOutputTokens": 8192,
        },
    }
    resp = httpx.post(
        url,
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        json=body,
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()  # 429/5xx -> caught by caller, triggers fallback
    data = resp.json()

    candidates = data.get("candidates") or []
    if not candidates:
        raise RoadmapError(f"Gemini returned no candidates (promptFeedback={data.get('promptFeedback')})")

    parts = (candidates[0].get("content") or {}).get("parts") or []
    text = "".join(p.get("text", "") for p in parts).strip()
    if not text:
        finish = candidates[0].get("finishReason")
        raise RoadmapError(f"Gemini returned empty text (finishReason={finish})")

    return json.loads(text)  # JSON mode -> pure JSON; JSONDecodeError caught by caller


def _normalize(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Coerce the model's output into the contract shape for the 5 owned keys.
    Defensive: missing keys default empty; milestones get a zeroed expected_salary
    (Agent 2 fills it later)."""
    milestones = []
    for i, m in enumerate(raw.get("milestones") or [], start=1):
        if not isinstance(m, dict):
            continue
        es = m.get("expected_salary") or {}
        milestones.append(
            {
                "order": int(m.get("order", i) or i),
                "title": str(m.get("title", f"Milestone {i}")),
                "duration": str(m.get("duration", "")),
                "description": str(m.get("description", "")),
                "skills": [str(s) for s in (m.get("skills") or [])],
                "certifications": [str(c) for c in (m.get("certifications") or [])],
                "expected_salary": {
                    "min": int(es.get("min", 0) or 0),
                    "max": int(es.get("max", 0) or 0),
                    "currency": str(es.get("currency", "USD") or "USD"),
                    "note": str(es.get("note", "") or ""),
                },
            }
        )

    skills = []
    for s in raw.get("skills") or []:
        if isinstance(s, dict) and s.get("name"):
            skills.append(
                {
                    "name": str(s["name"]),
                    "level": str(s.get("level", "Beginner") or "Beginner"),
                    "why": str(s.get("why", "") or ""),
                }
            )

    certs = []
    for c in raw.get("certifications") or []:
        if isinstance(c, dict) and c.get("name"):
            certs.append(
                {
                    "name": str(c["name"]),
                    "provider": str(c.get("provider", "") or ""),
                    "url": str(c.get("url", "") or ""),
                    "free": bool(c.get("free", False)),
                }
            )

    return {
        "summary": str(raw.get("summary", "") or ""),
        "background_required": str(raw.get("background_required", "") or ""),
        "milestones": milestones,
        "skills": skills,
        "certifications": certs,
    }


def generate_roadmap(job_title: str) -> Dict[str, Any]:
    """Generate the core roadmap for `job_title`.

    Returns a dict with exactly: summary, background_required, milestones[],
    skills[], certifications[].
    Tries the primary model, then the fallback model once. Raises RoadmapError if
    both fail — main.py catches this and serves the mock payload (demo safety net).
    """
    prompt = render_prompt("roadmap_generation", job_title=job_title)

    keys = _keys()
    if not keys:
        raise RoadmapError("no Gemini API key configured")

    last_err: Exception | None = None
    # Failover matrix: each key × (primary model, fallback model).
    # Primary key first; on quota/429 it falls through to the fallback key.
    for key in keys:
        for model in (_model(), _fallback_model()):
            try:
                raw = _call_gemini(model, prompt, key)
                result = _normalize(raw)
                if not result["milestones"]:
                    raise RoadmapError("model produced zero milestones")
                return result
            except Exception as e:  # HTTP/JSON/shape error -> next model, then next key
                last_err = e
                continue

    raise RoadmapError(f"roadmap generation failed (last error: {last_err})")
