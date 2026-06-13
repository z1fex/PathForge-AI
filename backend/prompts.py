"""Shared prompt loader. Prompts live as markdown in /prompts (judged separately),
never inlined in code. Variables are written {{like_this}} and substituted by callers."""
from __future__ import annotations

from pathlib import Path

# /prompts sits next to /app, i.e. one level up from this file's directory.
_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(name: str) -> str:
    """Read prompts/<name>.md and return its raw text.

    Raises FileNotFoundError if the prompt is missing — callers should treat a
    missing prompt as a hard config error (fail loud at startup, not at request time).
    """
    path = _PROMPTS_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8")


def render_prompt(name: str, **vars: str) -> str:
    """Load a prompt and substitute {{var}} placeholders. Unknown vars are ignored."""
    text = load_prompt(name)
    for key, value in vars.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text
