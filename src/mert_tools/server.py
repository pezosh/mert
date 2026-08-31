from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from .capabilities import analyze_image as _analyze_image
from .capabilities import create_task as _create_task
from .capabilities import search_notes as _search_notes

server = MCPServer("mert-tools")


@server.tool()
def search_notes(query: str, limit: int = 5) -> dict:
    """Search markdown notes and return ranked structured matches."""
    return _search_notes(query=query, limit=limit).model_dump(mode="json")


@server.tool()
def create_task(title: str, due_at: str | None = None) -> dict:
    """Create a local task record. due_at should be ISO-8601 when provided."""
    return _create_task(title=title, due_at=due_at).model_dump(mode="json")


@server.tool()
def analyze_image(image_path: str, instruction: str = "Describe the important visible facts in this image.") -> dict:
    """Analyze a local image with a vision-capable OpenAI model and return structured observations."""
    return _analyze_image(image_path=image_path, instruction=instruction).model_dump(mode="json")


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
