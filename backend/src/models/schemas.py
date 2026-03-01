"""Nexus data models — Netflix-style hierarchical entity design.

Hierarchy: Team → Agent → Task → Execution
Each entity has rich metadata for analytics and real-time monitoring.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


def _uuid() -> str:
    return str(uuid.uuid4())[:8]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ── Enums ──────────────────────────────────────────────────────────


class ModelProvider(str, enum.Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    ALIBABA = "alibaba"
    MOONSHOT = "moonshot"
    DEEPSEEK = "deepseek"
    LOCAL = "local"


class AgentRole(str, enum.Enum):
    ORCHESTRATOR = "orchestrator"
    BACKEND = "backend"
    FRONTEND = "frontend"
    SECURITY = "security"
    RESEARCHER = "researcher"
    DESIGNER = "designer"
    REVIEWER = "reviewer"
    TESTER = "tester"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionPhase(str, enum.Enum):
    QUEUED = "queued"
    THINKING = "thinking"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    DONE = "done"
    ERROR = "error"


# ── Core Entities ──────────────────────────────────────────────────


class AgentConfig(BaseModel):
    """Single agent within a team — maps to one AI model."""

    id: str = Field(default_factory=_uuid)
    name: str
    model: str  # e.g. "claude-opus-4-6", "gpt-5.3-codex"
    provider: ModelProvider
    role: AgentRole
    description: str = ""
    reasoning_effort: str = "medium"  # low | medium | high
    max_tokens: int = 4096
    temperature: float = 0.7
    color: str = "#3B82F6"  # UI accent color


class Team(BaseModel):
    """A composed team of AI agents with defined roles."""

    id: str = Field(default_factory=_uuid)
    name: str
    description: str = ""
    agents: list[AgentConfig] = []
    created_at: str = Field(default_factory=_now)
    updated_at: str = Field(default_factory=_now)


class TaskStep(BaseModel):
    """A single step within a task pipeline."""

    id: str = Field(default_factory=_uuid)
    name: str
    prompt: str
    assigned_agent_id: str
    depends_on: list[str] = []  # step IDs
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    tokens_used: int = 0
    cost_usd: float = 0.0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: int = 0


class Task(BaseModel):
    """A multi-step task executed by an agent team."""

    id: str = Field(default_factory=_uuid)
    team_id: str
    name: str
    description: str = ""
    steps: list[TaskStep] = []
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = Field(default_factory=_now)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_tokens: int = 0
    total_cost_usd: float = 0.0


class Execution(BaseModel):
    """Real-time execution state for a single agent step."""

    id: str = Field(default_factory=_uuid)
    task_id: str
    step_id: str
    agent_id: str
    agent_name: str
    model: str
    phase: ExecutionPhase = ExecutionPhase.QUEUED
    output_preview: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


# ── API Request/Response ───────────────────────────────────────────


class CreateTeamRequest(BaseModel):
    name: str
    description: str = ""
    agents: list[AgentConfig] = []


class CreateTaskRequest(BaseModel):
    team_id: str
    name: str
    description: str = ""
    steps: list[dict] = []  # [{name, prompt, assigned_agent_id, depends_on}]


class ExecuteTaskRequest(BaseModel):
    task_id: str
    parallel: bool = True


class DashboardStats(BaseModel):
    total_teams: int = 0
    total_tasks: int = 0
    active_executions: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    models_used: list[str] = []
    recent_tasks: list[Task] = []


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    litellm_connected: bool = False
    db_connected: bool = True
    uptime_seconds: float = 0.0
