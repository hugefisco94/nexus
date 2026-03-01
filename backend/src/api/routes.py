"""REST API routes for Nexus."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException

from ..db import database as db
from ..models.schemas import (
    AgentConfig,
    CreateTaskRequest,
    CreateTeamRequest,
    DashboardStats,
    ExecuteTaskRequest,
    Task,
    TaskStep,
    Team,
    _now,
    _uuid,
)
from ..services import agent_service, litellm_client

router = APIRouter(prefix="/api")


# ── Health ─────────────────────────────────────────────────────────


@router.get("/health")
async def health():
    litellm_ok = await litellm_client.check_health()
    return {
        "status": "ok",
        "version": "0.1.0",
        "litellm_connected": litellm_ok,
    }


# ── Dashboard ──────────────────────────────────────────────────────


@router.get("/dashboard")
async def get_dashboard() -> dict:
    stats = await db.get_stats()
    tasks = await db.list_tasks()
    stats["recent_tasks"] = tasks[:10]
    return stats


# ── Models ─────────────────────────────────────────────────────────


@router.get("/models")
async def list_models():
    models = await litellm_client.list_models()
    return {"models": models, "count": len(models)}


# ── Teams CRUD ─────────────────────────────────────────────────────


@router.get("/teams")
async def list_teams():
    teams = await db.list_teams()
    return {"teams": teams, "count": len(teams)}


@router.post("/teams")
async def create_team(req: CreateTeamRequest):
    team_data = {
        "id": _uuid(),
        "name": req.name,
        "description": req.description,
        "agents": [
            a.model_dump() if isinstance(a, AgentConfig) else a for a in req.agents
        ],
        "created_at": _now(),
        "updated_at": _now(),
    }
    team = await db.create_team(team_data)
    return team


@router.get("/teams/{team_id}")
async def get_team(team_id: str):
    team = await db.get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.delete("/teams/{team_id}")
async def delete_team(team_id: str):
    ok = await db.delete_team(team_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"deleted": True}


# ── Preset Teams ───────────────────────────────────────────────────


@router.post("/teams/preset/harness")
async def create_harness_preset():
    """Create the Harness Engineering team from reference images."""
    team_data = {
        "id": _uuid(),
        "name": "Harness Engineering Team",
        "description": "Multi-model agent team: Opus orchestrates, Codex reviews, Sonnet builds, Qwen secures, Gemini designs",
        "agents": [
            AgentConfig(
                name="Opus Orchestrator",
                model="claude-opus-4-6",
                provider="anthropic",
                role="orchestrator",
                description="Task decomposition, delegation, result aggregation, final judgment",
                color="#F59E0B",
            ).model_dump(),
            AgentConfig(
                name="Codex Backend",
                model="gpt-5.3-codex",
                provider="openai",
                role="backend",
                description="Backend logic, code review, refactoring. SWE-Bench Pro top scorer",
                reasoning_effort="high",
                color="#3B82F6",
            ).model_dump(),
            AgentConfig(
                name="Sonnet Actor",
                model="claude-sonnet-4-6-20250514",
                provider="anthropic",
                role="frontend",
                description="Main code writing, frontend implementation. Production-grade output",
                color="#10B981",
            ).model_dump(),
            AgentConfig(
                name="Qwen Security",
                model="openrouter/qwen/qwen3-coder",
                provider="alibaba",
                role="security",
                description="Security analysis, vulnerability review. 1/18 cost of Gemini Pro",
                color="#EC4899",
            ).model_dump(),
            AgentConfig(
                name="Gemini Designer",
                model="gemini-3.1-pro",
                provider="google",
                role="designer",
                description="UI design, visual judgment, design system review, screenshot feedback",
                color="#8B5CF6",
            ).model_dump(),
        ],
        "created_at": _now(),
        "updated_at": _now(),
    }
    return await db.create_team(team_data)


# ── Tasks CRUD ─────────────────────────────────────────────────────


@router.get("/tasks")
async def list_tasks(team_id: str = None):
    tasks = await db.list_tasks(team_id)
    return {"tasks": tasks, "count": len(tasks)}


@router.post("/tasks")
async def create_task(req: CreateTaskRequest):
    # Validate team exists
    team = await db.get_team(req.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    steps = []
    for s in req.steps:
        steps.append(
            TaskStep(
                name=s["name"],
                prompt=s["prompt"],
                assigned_agent_id=s["assigned_agent_id"],
                depends_on=s.get("depends_on", []),
            ).model_dump()
        )

    task_data = {
        "id": _uuid(),
        "team_id": req.team_id,
        "name": req.name,
        "description": req.description,
        "steps": steps,
        "status": "pending",
        "created_at": _now(),
    }
    return await db.create_task(task_data)


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ── Execution ──────────────────────────────────────────────────────


@router.post("/tasks/{task_id}/execute")
async def execute_task(task_id: str, parallel: bool = True):
    """Start executing a task. Returns immediately, execution runs in background."""
    task = await db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Fire and forget
    asyncio.create_task(agent_service.execute_task(task_id, parallel=parallel))
    return {"status": "started", "task_id": task_id}


@router.get("/executions")
async def list_executions(task_id: str = None):
    execs = await db.list_executions(task_id)
    return {"executions": execs, "count": len(execs)}
