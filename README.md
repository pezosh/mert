# Mert Tools v0.1

A deliberately small capability layer exposed through MCP.

Current capabilities:

- `search_notes(query, limit)` — searches Markdown notes under `MERT_NOTES_DIR`.
- `create_task(title, due_at)` — appends a structured task record to a local JSONL store.
- `analyze_image(image_path, instruction)` — analyzes a local image with a vision-capable OpenAI model and returns structured observations.

## Why this exists

The goal is to keep reusable capabilities separate from any single persona, chat UI, or agent. ChatGPT, Codex, another MCP-compatible host, or a future agent can call the same tools.

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Optional environment variables:

```bash
export MERT_NOTES_DIR="/path/to/your/obsidian/vault"
export MERT_TASK_FILE="./data/tasks.jsonl"
export OPENAI_API_KEY="..."
export MERT_VISION_MODEL="gpt-5.6"
```

## Run

```bash
mert-tools
```

Or inspect it with the MCP CLI:

```bash
mcp dev src/mert_tools/server.py
```

## Definition of done for v0.1

1. Notes can be searched from a real Markdown vault.
2. Tasks are persisted in deterministic structured form.
3. An image can be converted into validated structured observations.
4. All three tools are callable through one MCP server.

## Next step

Do not add more tools yet. First connect this server to one real MCP host and run three end-to-end tests. After that, replace the local task store with the preferred real task/calendar backend and improve note search only if the naive search proves insufficient.
