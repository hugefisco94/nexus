"""LiteLLM client — connects to existing LiteLLM proxy at localhost:4000.

Provides async completion with cost tracking and error handling.
"""

from __future__ import annotations

import os
import time
from typing import Optional

import httpx

LITELLM_BASE = os.environ.get("LITELLM_BASE_URL", "http://localhost:4000")
LITELLM_KEY = os.environ.get("LITELLM_API_KEY", "sk-litellm-master-key")


async def check_health() -> bool:
    """Check if LiteLLM proxy is alive."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{LITELLM_BASE}/health/liveliness")
            return resp.status_code == 200
    except Exception:
        return False


async def list_models() -> list[str]:
    """Get available models from LiteLLM."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{LITELLM_BASE}/v1/models",
                headers={"Authorization": f"Bearer {LITELLM_KEY}"},
            )
            if resp.status_code == 200:
                data = resp.json()
                return [m["id"] for m in data.get("data", [])]
    except Exception:
        pass
    return []


async def complete(
    model: str,
    messages: list[dict],
    max_tokens: int = 4096,
    temperature: float = 0.7,
    reasoning_effort: Optional[str] = None,
) -> dict:
    """Send completion request to LiteLLM proxy.

    Returns:
        {
            "content": str,
            "tokens_in": int,
            "tokens_out": int,
            "cost_usd": float,
            "duration_ms": int,
            "model": str,
        }
    """
    payload: dict = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    if reasoning_effort and reasoning_effort != "medium":
        payload["extra_body"] = {"reasoning_effort": reasoning_effort}

    start = time.time()

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{LITELLM_BASE}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {LITELLM_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        resp.raise_for_status()

    duration_ms = int((time.time() - start) * 1000)
    data = resp.json()

    usage = data.get("usage", {})
    content = ""
    if data.get("choices"):
        content = data["choices"][0].get("message", {}).get("content", "")

    # LiteLLM provides cost info in response headers or usage
    cost = 0.0
    if "_litellm_model_cost" in data:
        cost = data["_litellm_model_cost"]
    elif usage.get("completion_cost"):
        cost = usage["completion_cost"]

    return {
        "content": content,
        "tokens_in": usage.get("prompt_tokens", 0),
        "tokens_out": usage.get("completion_tokens", 0),
        "cost_usd": cost,
        "duration_ms": duration_ms,
        "model": data.get("model", model),
    }
