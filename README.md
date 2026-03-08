> **DEPRECATED** — This repository has been consolidated into [mdo-nexus-ooda](https://github.com/hugefisco94/mdo-nexus-ooda). No further updates here.

<div align="center">

# N E X U S

**Orchestrate multi-model AI agent teams. Observe every decision in real time.**

<br/>

<a href="https://github.com/hugefisco94/nexus/releases/latest">
  <img alt="Release" src="https://img.shields.io/github/v/release/hugefisco94/nexus?style=for-the-badge&logo=starship&color=C9CBFF&logoColor=D9E0EE&labelColor=0d1117&include_prerelease&sort=semver" />
</a>
<a href="https://github.com/hugefisco94/nexus/blob/master/LICENSE">
  <img alt="License" src="https://img.shields.io/github/license/hugefisco94/nexus?style=for-the-badge&logo=starship&color=ee999f&logoColor=D9E0EE&labelColor=0d1117" />
</a>
<a href="https://github.com/hugefisco94/nexus/pulse">
  <img alt="Last commit" src="https://img.shields.io/github/last-commit/hugefisco94/nexus?style=for-the-badge&logo=starship&color=8bd5ca&logoColor=D9E0EE&labelColor=0d1117" />
</a>
<a href="https://github.com/hugefisco94/nexus/stargazers">
  <img alt="Stars" src="https://img.shields.io/github/stars/hugefisco94/nexus?style=for-the-badge&logo=starship&color=c69ff5&logoColor=D9E0EE&labelColor=0d1117" />
</a>

<br/><br/>

<a href="#quick-start">Quick Start</a>&nbsp;&nbsp;&bull;&nbsp;&nbsp;<a href="#architecture">Architecture</a>&nbsp;&nbsp;&bull;&nbsp;&nbsp;<a href="#api-reference">API</a>&nbsp;&nbsp;&bull;&nbsp;&nbsp;<a href="https://github.com/hugefisco94/nexus/releases">Releases</a>

<br/>

<img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
<img src="https://img.shields.io/badge/React_19-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React"/>
<img src="https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript"/>
<img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white" alt="TailwindCSS"/>
<img src="https://img.shields.io/badge/LiteLLM-000000?style=flat-square&logo=openai&logoColor=white" alt="LiteLLM"/>
<img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker"/>

</div>

<br/>

<p align="center"><em>"Humans steer. Agents execute."</em></p>

---

## Why Nexus

Nexus gives you a single control surface for multi-model AI agent teams. Define a team of specialist models, assign each a role, then launch tasks and watch execution unfold in real time through WebSocket-driven dashboards.

One endpoint provisions a battle-tested five-agent team. One command deploys the entire stack.

<br/>

<table>
<tr>
<td width="25%" align="center"><strong>Compose</strong><br/><sub>Build teams with role-specific models</sub></td>
<td width="25%" align="center"><strong>Execute</strong><br/><sub>Parallel &amp; sequential pipelines</sub></td>
<td width="25%" align="center"><strong>Observe</strong><br/><sub>Live WebSocket execution feed</sub></td>
<td width="25%" align="center"><strong>Analyze</strong><br/><sub>Tokens, cost, latency per agent</sub></td>
</tr>
</table>

<br/>

## Architecture

```mermaid
graph TB
    subgraph CLIENT ["CLIENT"]
        direction LR
        D["Dashboard"]
        TB["TeamBuilder"]
        EM["ExecutionMonitor"]
        RV["ResultsViewer"]
    end

    subgraph API ["FASTAPI  :8800"]
        direction LR
        REST["/api/*"]
        WS["/ws"]
        ORCH["Orchestrator"]
    end

    subgraph DATA ["PERSISTENCE"]
        direction LR
        DB[("SQLite\nWAL mode")]
        LLM["LiteLLM\n:4000"]
    end

    CLIENT -- "REST + WebSocket" --> API
    ORCH --> DB
    ORCH --> LLM

    style CLIENT fill:#1e1e2e,stroke:#cba6f7,color:#cdd6f4
    style API fill:#1e1e2e,stroke:#89b4fa,color:#cdd6f4
    style DATA fill:#1e1e2e,stroke:#a6e3a1,color:#cdd6f4
```

<br/>

### Data Model

```mermaid
erDiagram
    TEAM ||--o{ AGENT : contains
    TEAM ||--o{ TASK : receives
    TASK ||--o{ STEP : "broken into"
    TASK ||--o{ EXECUTION : triggers
    EXECUTION ||--o{ STEP_RESULT : produces

    TEAM {
        string id PK
        string name
        string strategy
    }
    AGENT {
        string id PK
        string role
        string model
    }
    TASK {
        string id PK
        string prompt
        string mode
    }
    EXECUTION {
        string id PK
        string status
        float total_cost
    }
```

<br/>

### Harness Engineering Preset

A single `POST /api/teams/preset/harness` provisions the reference team:

| Role | Model | Responsibility |
|:-----|:------|:---------------|
| **Orchestrator** | `claude-opus-4-6` | Decomposition, delegation, judgment |
| **Backend** | `gpt-5.3-codex` | Logic, review, refactoring |
| **Actor** | `claude-sonnet-4-6` | Primary code generation |
| **Security** | `qwen3-coder` | Vulnerability analysis |
| **Designer** | `gemini-3.1-pro` | UI evaluation, visual judgment |

<br/>

## Quick Start

### Docker &mdash; recommended

```bash
docker compose up -d
```

Frontend on `:3000` &middot; Backend on `:8800`

### Manual

```bash
# backend
cd backend && pip install -e ".[dev]"
uvicorn src.main:app --port 8800 --reload

# frontend
cd frontend && npm install && npm run dev
```

Open `http://localhost:5173` &mdash; API proxied automatically.

> **Optional** &mdash; connect a [LiteLLM](https://docs.litellm.ai/) proxy at `localhost:4000` for live AI execution.

<br/>

## API Reference

| Method | Endpoint | Purpose |
|:------:|:---------|:--------|
| `GET` | `/api/health` | Liveness + LiteLLM status |
| `GET` | `/api/dashboard` | Aggregate statistics |
| `GET` | `/api/models` | Available models via LiteLLM |
| `POST` | `/api/teams` | Create team |
| `POST` | `/api/teams/preset/harness` | Provision preset team |
| `GET` | `/api/teams` | List teams |
| `POST` | `/api/tasks` | Create task with steps |
| `POST` | `/api/tasks/{id}/execute` | Execute task |
| `GET` | `/api/executions` | List executions |
| `WS` | `/ws` | Real-time execution stream |

<br/>

## Testing

```bash
cd backend && pytest tests/ -v   # 17 tests · ~2.6s
```

<br/>

## License

[MIT](LICENSE)

---

<div align="center">
<sub>Built with precision. Designed for control.</sub>
</div>
