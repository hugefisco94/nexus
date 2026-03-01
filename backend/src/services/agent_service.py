"""Agent orchestration service — executes tasks across multi-model teams.

Supports parallel execution of independent steps and sequential
execution of dependent steps, mirroring the Harness Engineering
architecture from the reference images.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Callable, Optional

from ..db import database as db
from ..models.schemas import (
    AgentConfig,
    ExecutionPhase,
    TaskStatus,
    _now,
    _uuid,
)
from . import litellm_client


# Type for WebSocket broadcast callback
BroadcastFn = Optional[Callable[[dict], asyncio.coroutines]]


async def execute_task(
    task_id: str,
    parallel: bool = True,
    on_update: BroadcastFn = None,
) -> dict:
    """Execute a task by running its steps through assigned agents.

    Args:
        task_id: The task to execute.
        parallel: If True, run independent steps concurrently.
        on_update: Async callback for real-time status updates.
    """
    task = await db.get_task(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    team = await db.get_team(task["team_id"])
    if not team:
        raise ValueError(f"Team {task['team_id']} not found")

    agents_map: dict[str, dict] = {}
    for agent in team["agents"]:
        a = agent if isinstance(agent, dict) else agent.model_dump()
        agents_map[a["id"]] = a

    await db.update_task(
        task_id,
        {
            "status": TaskStatus.RUNNING.value,
            "started_at": _now(),
        },
    )

    if on_update:
        await on_update({"type": "task_started", "task_id": task_id})

    steps = task["steps"]
    results: dict[str, str] = {}  # step_id -> output

    if parallel:
        await _execute_parallel(task_id, steps, agents_map, results, on_update)
    else:
        await _execute_sequential(task_id, steps, agents_map, results, on_update)

    executions = await db.list_executions(task_id)
    total_tokens = sum(
        e.get("tokens_in", 0) + e.get("tokens_out", 0) for e in executions
    )
    total_cost = sum(e.get("cost_usd", 0) for e in executions)

    failed = any(s.get("status") == TaskStatus.FAILED.value for s in steps)

    await db.update_task(
        task_id,
        {
            "status": TaskStatus.FAILED.value if failed else TaskStatus.COMPLETED.value,
            "completed_at": _now(),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "steps": steps,
        },
    )

    if on_update:
        await on_update(
            {
                "type": "task_completed",
                "task_id": task_id,
                "status": "failed" if failed else "completed",
                "total_tokens": total_tokens,
                "total_cost_usd": total_cost,
            }
        )

    return await db.get_task(task_id)


async def _execute_step(
    task_id: str,
    step: dict,
    agent: dict,
    context: str,
    on_update: BroadcastFn,
) -> str:
    """Execute a single step with its assigned agent."""
    exec_id = _uuid()
    now = _now()

    await db.create_execution(
        {
            "id": exec_id,
            "task_id": task_id,
            "step_id": step["id"],
            "agent_id": agent["id"],
            "agent_name": agent["name"],
            "model": agent["model"],
            "phase": ExecutionPhase.THINKING.value,
            "started_at": now,
        }
    )

    step["status"] = TaskStatus.RUNNING.value
    step["started_at"] = now

    if on_update:
        await on_update(
            {
                "type": "step_started",
                "task_id": task_id,
                "step_id": step["id"],
                "agent_name": agent["name"],
                "model": agent["model"],
                "phase": "thinking",
            }
        )

    try:
        system_msg = (
            f"You are {agent['name']}, role: {agent['role']}. "
            f"{agent.get('description', '')} "
            "Produce clear, actionable output."
        )
        user_msg = step["prompt"]
        if context:
            user_msg = f"Context from previous steps:\n{context}\n\n---\n\nYour task:\n{step['prompt']}"

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        await db.update_execution(exec_id, {"phase": ExecutionPhase.EXECUTING.value})
        if on_update:
            await on_update(
                {
                    "type": "step_phase",
                    "task_id": task_id,
                    "step_id": step["id"],
                    "phase": "executing",
                }
            )

        result = await litellm_client.complete(
            model=agent["model"],
            messages=messages,
            max_tokens=agent.get("max_tokens", 4096),
            temperature=agent.get("temperature", 0.7),
            reasoning_effort=agent.get("reasoning_effort"),
        )

        content = result["content"]
        step["status"] = TaskStatus.COMPLETED.value
        step["result"] = content
        step["tokens_used"] = result["tokens_in"] + result["tokens_out"]
        step["cost_usd"] = result["cost_usd"]
        step["completed_at"] = _now()
        step["duration_ms"] = result["duration_ms"]

        await db.update_execution(
            exec_id,
            {
                "phase": ExecutionPhase.DONE.value,
                "output_preview": content[:500],
                "tokens_in": result["tokens_in"],
                "tokens_out": result["tokens_out"],
                "cost_usd": result["cost_usd"],
                "completed_at": _now(),
            },
        )

        if on_update:
            await on_update(
                {
                    "type": "step_completed",
                    "task_id": task_id,
                    "step_id": step["id"],
                    "agent_name": agent["name"],
                    "tokens": step["tokens_used"],
                    "duration_ms": result["duration_ms"],
                    "output_preview": content[:200],
                }
            )

        return content

    except Exception as e:
        error_msg = str(e)
        step["status"] = TaskStatus.FAILED.value
        step["completed_at"] = _now()

        await db.update_execution(
            exec_id,
            {
                "phase": ExecutionPhase.ERROR.value,
                "error": error_msg,
                "completed_at": _now(),
            },
        )

        if on_update:
            await on_update(
                {
                    "type": "step_failed",
                    "task_id": task_id,
                    "step_id": step["id"],
                    "error": error_msg,
                }
            )

        return f"[ERROR] {error_msg}"


async def _execute_parallel(
    task_id: str,
    steps: list[dict],
    agents_map: dict[str, dict],
    results: dict[str, str],
    on_update: BroadcastFn,
) -> None:
    """Execute steps in waves — parallel within each wave, sequential across waves."""
    remaining = {s["id"]: s for s in steps}
    completed_ids: set[str] = set()

    while remaining:
        # Find steps whose dependencies are all met
        ready = []
        for sid, step in remaining.items():
            deps = step.get("depends_on", [])
            if all(d in completed_ids for d in deps):
                ready.append(step)

        if not ready:
            # Deadlock — mark remaining as failed
            for step in remaining.values():
                step["status"] = TaskStatus.FAILED.value
            break

        # Execute ready steps in parallel
        context_parts = [
            results.get(d, "") for step in ready for d in step.get("depends_on", [])
        ]
        context = "\n---\n".join(filter(None, context_parts))

        tasks = []
        for step in ready:
            agent = agents_map.get(step["assigned_agent_id"])
            if not agent:
                step["status"] = TaskStatus.FAILED.value
                step["result"] = f"Agent {step['assigned_agent_id']} not found in team"
                completed_ids.add(step["id"])
                del remaining[step["id"]]
                continue
            tasks.append(_execute_step(task_id, step, agent, context, on_update))

        if tasks:
            outputs = await asyncio.gather(*tasks, return_exceptions=True)
            for step, output in zip(ready, outputs):
                if step["id"] in remaining:
                    if isinstance(output, Exception):
                        results[step["id"]] = f"[ERROR] {output}"
                    else:
                        results[step["id"]] = output
                    completed_ids.add(step["id"])
                    del remaining[step["id"]]


async def _execute_sequential(
    task_id: str,
    steps: list[dict],
    agents_map: dict[str, dict],
    results: dict[str, str],
    on_update: BroadcastFn,
) -> None:
    """Execute all steps one by one."""
    context = ""
    for step in steps:
        agent = agents_map.get(step["assigned_agent_id"])
        if not agent:
            step["status"] = TaskStatus.FAILED.value
            continue
        output = await _execute_step(task_id, step, agent, context, on_update)
        results[step["id"]] = output
        context += f"\n---\n{output}"
