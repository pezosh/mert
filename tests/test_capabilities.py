from pathlib import Path

from mert_tools.capabilities import create_task, search_notes


def test_search_notes_finds_markdown(tmp_path: Path) -> None:
    (tmp_path / "dreams.md").write_text("# Dream Research\nREM sleep dream report dataset", encoding="utf-8")
    (tmp_path / "other.md").write_text("# Shopping\ncoffee beans", encoding="utf-8")

    result = search_notes("dream REM", notes_dir=str(tmp_path), limit=5)

    assert result.count == 1
    assert result.hits[0].title == "Dream Research"
    assert result.hits[0].score == 1.0


def test_create_task_persists_jsonl(tmp_path: Path) -> None:
    target = tmp_path / "tasks.jsonl"

    record = create_task("Test Mert Tools", "2026-09-01T09:00:00+05:30", task_file=str(target))

    assert record.title == "Test Mert Tools"
    assert target.exists()
    text = target.read_text(encoding="utf-8")
    assert record.id in text
    assert "Test Mert Tools" in text
