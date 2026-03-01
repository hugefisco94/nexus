import asyncio
import json
import os
import tempfile

import pytest
import httpx
from fastapi.testclient import TestClient

os.environ["NEXUS_DB_PATH"] = os.path.join(tempfile.gettempdir(), "nexus_test.db")

from src.main import app
from src.db.database import init_db


@pytest.fixture(autouse=True)
def setup_db():
    asyncio.get_event_loop().run_until_complete(init_db())
    yield
    db_path = os.environ["NEXUS_DB_PATH"]
    if os.path.exists(db_path):
        os.remove(db_path)


client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Nexus"
    assert data["version"] == "0.1.0"


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"


def test_dashboard():
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert "total_teams" in data
    assert "total_tasks" in data


def test_create_team():
    payload = {
        "name": "Test Team",
        "description": "A test agent team",
        "agents": [
            {
                "id": "a1",
                "name": "Opus Lead",
                "model": "claude-opus-4-6",
                "provider": "anthropic",
                "role": "orchestrator",
                "description": "Orchestrator",
                "reasoning_effort": "medium",
                "max_tokens": 4096,
                "temperature": 0.7,
                "color": "#F59E0B",
            }
        ],
    }
    r = client.post("/api/teams", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Test Team"
    assert len(data["agents"]) == 1
    return data


def test_list_teams():
    test_create_team()
    r = client.get("/api/teams")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1


def test_get_team():
    team = test_create_team()
    r = client.get(f"/api/teams/{team['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Test Team"


def test_delete_team():
    team = test_create_team()
    r = client.delete(f"/api/teams/{team['id']}")
    assert r.status_code == 200
    assert r.json()["deleted"] is True


def test_create_harness_preset():
    r = client.post("/api/teams/preset/harness")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Harness Engineering Team"
    assert len(data["agents"]) == 5


def test_create_task():
    team = test_create_team()
    payload = {
        "team_id": team["id"],
        "name": "Test Task",
        "description": "A test task",
        "steps": [
            {
                "name": "Step 1",
                "prompt": "Analyze the codebase",
                "assigned_agent_id": "a1",
                "depends_on": [],
            }
        ],
    }
    r = client.post("/api/tasks", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Test Task"
    assert len(data["steps"]) == 1


def test_list_tasks():
    r = client.get("/api/tasks")
    assert r.status_code == 200
    assert "tasks" in r.json()


def test_get_task_not_found():
    r = client.get("/api/tasks/nonexistent")
    assert r.status_code == 404


def test_list_executions():
    r = client.get("/api/executions")
    assert r.status_code == 200
    assert "executions" in r.json()


def test_team_not_found():
    r = client.get("/api/teams/nonexistent")
    assert r.status_code == 404


def test_delete_team_not_found():
    r = client.delete("/api/teams/nonexistent")
    assert r.status_code == 404


def test_task_with_invalid_team():
    payload = {
        "team_id": "nonexistent",
        "name": "Bad Task",
        "steps": [],
    }
    r = client.post("/api/tasks", json=payload)
    assert r.status_code == 404


def test_execute_task_not_found():
    r = client.post("/api/tasks/nonexistent/execute")
    assert r.status_code == 404


def test_dashboard_after_operations():
    test_create_harness_preset()
    r = client.get("/api/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert data["total_teams"] >= 1
