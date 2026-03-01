# Nexus — AI Agent Mission Control

<div align="center">

```
  ┌─────────────────────────────────────────────┐
  │         N E X U S   v0.1.0                  │
  │    AI Agent Mission Control Dashboard       │
  │                                             │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
  │  │  Opus    │  │  Codex   │  │  Sonnet  │  │
  │  │ Orchest. │  │ Backend  │  │  Actor   │  │
  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
  │       └──────────────┼──────────────┘       │
  │              ┌───────┴───────┐              │
  │              │ ORCHESTRATOR  │              │
  │              └───────────────┘              │
  └─────────────────────────────────────────────┘
```

**Multi-model agent team orchestration with real-time monitoring**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)

</div>

---

## What is Nexus?

Nexus is a **Harness Engineering** dashboard that visualizes and orchestrates multi-model AI agent teams. Inspired by Mitchell Hashimoto's methodology:

> *"Humans steer. Agents execute."*

- **Agent Team Composer** — Define teams with specialized model roles (Orchestrator, Backend, Frontend, Security, Designer)
- **Live Execution Monitor** — Watch agents work in parallel with real-time WebSocket updates
- **Task Pipeline Builder** — Create multi-step pipelines with dependency graphs
- **Cost & Performance Analytics** — Track tokens, cost, and latency per model
- **LiteLLM Integration** — Connect to 88+ models via existing LiteLLM proxy

## Architecture

```
┌─────────────────────────────────┐
│   BROWSER (React 19 + Vite)     │
│   ├── Dashboard                 │
│   ├── Team Builder              │
│   ├── Execution Monitor         │
│   └── Results Viewer            │
└──────────────┬──────────────────┘
               │ REST + WebSocket
┌──────────────┴──────────────────┐
│   BACKEND (FastAPI + uvicorn)   │
│   ├── /api/* routes             │
│   ├── /ws WebSocket             │
│   ├── Agent Orchestration       │
│   └── LiteLLM Client           │
└──────────────┬──────────────────┘
               │
┌──────────────┴──────────────────┐
│   DATA (SQLite + LiteLLM)       │
│   ├── Teams / Agents            │
│   ├── Tasks / Steps             │
│   ├── Executions                │
│   └── localhost:4000 (LiteLLM)  │
└─────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 22+
- LiteLLM proxy at `localhost:4000` (optional, for AI execution)

### Backend

```bash
cd backend
pip install -e ".[dev]"
uvicorn src.main:app --host 0.0.0.0 --port 8800 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — API proxied to `:8800` automatically.

### Docker

```bash
docker compose up -d
```

Frontend at `:3000`, Backend at `:8800`.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check + LiteLLM status |
| GET | `/api/dashboard` | Dashboard stats |
| GET | `/api/models` | Available LiteLLM models |
| POST | `/api/teams` | Create agent team |
| POST | `/api/teams/preset/harness` | Create Harness Engineering preset team |
| GET | `/api/teams` | List teams |
| POST | `/api/tasks` | Create task with steps |
| POST | `/api/tasks/{id}/execute` | Execute task (parallel/sequential) |
| GET | `/api/executions` | List executions |
| WS | `/ws` | Real-time execution updates |

## Harness Engineering Team Preset

One-click creation of the reference architecture:

| Agent | Model | Role |
|-------|-------|------|
| Opus Orchestrator | claude-opus-4-6 | Task decomposition, delegation, judgment |
| Codex Backend | gpt-5.3-codex | Backend logic, code review, refactoring |
| Sonnet Actor | claude-sonnet-4-6 | Main code writing, frontend |
| Qwen Security | qwen3-coder | Security analysis, vulnerability review |
| Gemini Designer | gemini-3.1-pro | UI design, visual judgment |

## Tech Stack

- **Frontend**: React 19, Vite 6, TailwindCSS 3.4, TypeScript 5.8
- **Backend**: FastAPI, uvicorn, Pydantic v2
- **Database**: SQLite (aiosqlite) — production-ready with WAL mode
- **AI**: LiteLLM proxy (88+ models)
- **Real-time**: WebSocket (native FastAPI)
- **Deployment**: Docker, Harness.io CI/CD

## Testing

```bash
cd backend
pytest tests/ -v    # 17 tests, ~2.6s
```

## License

MIT — see [LICENSE](LICENSE)
