from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

from .models import NoteHit, NoteSearchResult, TaskRecord, VisionResult


_WORD = re.compile(r"[\w\-]+", re.UNICODE)


def _tokens(text: str) -> set[str]:
    return {m.group(0).lower() for m in _WORD.finditer(text)}


def search_notes(query: str, notes_dir: str | None = None, limit: int = 5) -> NoteSearchResult:
    root = Path(notes_dir or os.getenv("MERT_NOTES_DIR", "./notes")).expanduser()
    if not root.exists():
        return NoteSearchResult(query=query, count=0, hits=[])

    q_tokens = _tokens(query)
    if not q_tokens:
        return NoteSearchResult(query=query, count=0, hits=[])

    hits: list[NoteHit] = []
    for path in root.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        title = next((line.lstrip("# ").strip() for line in text.splitlines() if line.startswith("#")), path.stem)
        haystack_tokens = _tokens(f"{title}\n{text}")
        overlap = len(q_tokens & haystack_tokens)
        if overlap == 0:
            continue

        score = overlap / len(q_tokens)
        lowered = text.lower()
        first_term = next((term for term in q_tokens if term in lowered), "")
        idx = lowered.find(first_term) if first_term else 0
        start = max(0, idx - 120)
        end = min(len(text), idx + 280)
        excerpt = " ".join(text[start:end].split())
        hits.append(NoteHit(path=str(path), title=title, excerpt=excerpt, score=score))

    hits.sort(key=lambda x: x.score, reverse=True)
    selected = hits[: max(1, min(limit, 20))]
    return NoteSearchResult(query=query, count=len(selected), hits=selected)


def create_task(title: str, due_at: str | None = None, task_file: str | None = None) -> TaskRecord:
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("Task title cannot be empty.")

    due: datetime | None = None
    if due_at:
        due = datetime.fromisoformat(due_at.replace("Z", "+00:00"))

    record = TaskRecord(
        id=str(uuid.uuid4()),
        title=clean_title,
        due_at=due,
        created_at=datetime.now(timezone.utc),
    )

    target = Path(task_file or os.getenv("MERT_TASK_FILE", "./data/tasks.jsonl")).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as f:
        f.write(record.model_dump_json() + "\n")
    return record


def analyze_image(image_path: str, instruction: str = "Describe the important visible facts in this image.") -> VisionResult:
    path = Path(image_path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for analyze_image.")

    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    client = OpenAI(api_key=api_key)

    response = client.responses.parse(
        model=os.getenv("MERT_VISION_MODEL", "gpt-5.6"),
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": instruction},
                    {"type": "input_image", "image_url": f"data:{mime};base64,{encoded}"},
                ],
            }
        ],
        text_format=VisionResult,
    )
    if response.output_parsed is None:
        raise RuntimeError("Vision model returned no structured result.")
    return response.output_parsed
