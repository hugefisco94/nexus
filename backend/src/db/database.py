"""SQLite database layer with async support.

Uses aiosqlite for non-blocking database operations.
Schema mirrors the Pydantic models in schemas.py.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import aiosqlite

DB_PATH = os.environ.get(
    "NEXUS_DB_PATH", str(Path(__file__).parent.parent.parent / "nexus.db")
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS teams (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    agents TEXT DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    steps TEXT DEFAULT '[]',
    status TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    total_tokens INTEGER DEFAULT 0,
    total_cost_usd REAL DEFAULT 0.0,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

CREATE TABLE IF NOT EXISTS executions (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    model TEXT NOT NULL,
    phase TEXT DEFAULT 'queued',
    output_preview TEXT DEFAULT '',
    tokens_in INTEGER DEFAULT 0,
    tokens_out INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0.0,
    started_at TEXT,
    completed_at TEXT,
    error TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
"""


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db() -> None:
    db = await get_db()
    try:
        await db.executescript(_SCHEMA)
        await db.commit()
    finally:
        await db.close()


# ── Team CRUD ──────────────────────────────────────────────────────


async def create_team(team_data: dict) -> dict:
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO teams (id, name, description, agents, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                team_data["id"],
                team_data["name"],
                team_data.get("description", ""),
                json.dumps(
                    [
                        a if isinstance(a, dict) else a.model_dump()
                        for a in team_data.get("agents", [])
                    ]
                ),
                team_data["created_at"],
                team_data["updated_at"],
            ),
        )
        await db.commit()
        return team_data
    finally:
        await db.close()


async def get_team(team_id: str) -> Optional[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
        row = await cursor.fetchone()
        if not row:
            return None
        return {**dict(row), "agents": json.loads(row["agents"])}
    finally:
        await db.close()


async def list_teams() -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM teams ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [{**dict(r), "agents": json.loads(r["agents"])} for r in rows]
    finally:
        await db.close()


async def delete_team(team_id: str) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM teams WHERE id = ?", (team_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


# ── Task CRUD ──────────────────────────────────────────────────────


async def create_task(task_data: dict) -> dict:
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO tasks (id, team_id, name, description, steps, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                task_data["id"],
                task_data["team_id"],
                task_data["name"],
                task_data.get("description", ""),
                json.dumps(
                    [
                        s if isinstance(s, dict) else s.model_dump()
                        for s in task_data.get("steps", [])
                    ]
                ),
                task_data.get("status", "pending"),
                task_data["created_at"],
            ),
        )
        await db.commit()
        return task_data
    finally:
        await db.close()


async def get_task(task_id: str) -> Optional[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = await cursor.fetchone()
        if not row:
            return None
        return {**dict(row), "steps": json.loads(row["steps"])}
    finally:
        await db.close()


async def list_tasks(team_id: Optional[str] = None) -> list[dict]:
    db = await get_db()
    try:
        if team_id:
            cursor = await db.execute(
                "SELECT * FROM tasks WHERE team_id = ? ORDER BY created_at DESC",
                (team_id,),
            )
        else:
            cursor = await db.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [{**dict(r), "steps": json.loads(r["steps"])} for r in rows]
    finally:
        await db.close()


async def update_task(task_id: str, updates: dict) -> Optional[dict]:
    db = await get_db()
    try:
        sets = []
        vals = []
        for k, v in updates.items():
            if k in ("steps",):
                v = json.dumps(v)
            sets.append(f"{k} = ?")
            vals.append(v)
        vals.append(task_id)
        await db.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id = ?", vals)
        await db.commit()
        return await get_task(task_id)
    finally:
        await db.close()


# ── Execution CRUD ─────────────────────────────────────────────────


async def create_execution(exec_data: dict) -> dict:
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO executions (id, task_id, step_id, agent_id, agent_name, model, phase, started_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                exec_data["id"],
                exec_data["task_id"],
                exec_data["step_id"],
                exec_data["agent_id"],
                exec_data["agent_name"],
                exec_data["model"],
                exec_data.get("phase", "queued"),
                exec_data.get("started_at"),
            ),
        )
        await db.commit()
        return exec_data
    finally:
        await db.close()


async def update_execution(exec_id: str, updates: dict) -> Optional[dict]:
    db = await get_db()
    try:
        sets = []
        vals = []
        for k, v in updates.items():
            sets.append(f"{k} = ?")
            vals.append(v)
        vals.append(exec_id)
        await db.execute(f"UPDATE executions SET {', '.join(sets)} WHERE id = ?", vals)
        await db.commit()
        cursor = await db.execute("SELECT * FROM executions WHERE id = ?", (exec_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await db.close()


async def list_executions(task_id: Optional[str] = None) -> list[dict]:
    db = await get_db()
    try:
        if task_id:
            cursor = await db.execute(
                "SELECT * FROM executions WHERE task_id = ? ORDER BY started_at DESC",
                (task_id,),
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM executions ORDER BY started_at DESC LIMIT 50"
            )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        await db.close()


# ── Stats ──────────────────────────────────────────────────────────


async def get_stats() -> dict:
    db = await get_db()
    try:
        teams = (await (await db.execute("SELECT COUNT(*) FROM teams")).fetchone())[0]
        tasks = (await (await db.execute("SELECT COUNT(*) FROM tasks")).fetchone())[0]
        active = (
            await (
                await db.execute(
                    "SELECT COUNT(*) FROM executions WHERE phase IN ('thinking','executing','reviewing')"
                )
            ).fetchone()
        )[0]
        tokens = (
            await (
                await db.execute(
                    "SELECT COALESCE(SUM(tokens_in + tokens_out), 0) FROM executions"
                )
            ).fetchone()
        )[0]
        cost = (
            await (
                await db.execute("SELECT COALESCE(SUM(cost_usd), 0) FROM executions")
            ).fetchone()
        )[0]
        models_cursor = await db.execute("SELECT DISTINCT model FROM executions")
        models = [r[0] for r in await models_cursor.fetchall()]
        return {
            "total_teams": teams,
            "total_tasks": tasks,
            "active_executions": active,
            "total_tokens": tokens,
            "total_cost_usd": round(cost, 6),
            "models_used": models,
        }
    finally:
        await db.close()
