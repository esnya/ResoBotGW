"""OpenAI Agents SDK-backed runner.

Imports the Agents SDK statically to comply with the "no dynamic import" rule.
This module requires `openai-agents` to be installed; otherwise import will fail
immediately, which is desired per policy.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

# Import Agents SDK at module import time (no dynamic import per policy)
from agents import Agent, Runner  # type: ignore[import-not-found]
from agents.mcp import MCPServerStdio  # type: ignore[import-not-found]

from .interface import AgentRunner

logger = logging.getLogger(__name__)


@dataclass
class OpenAIAgentsRunner(AgentRunner):
    """Minimal adapter that runs a simple agent.

    By default, this runner idles until cancellation. Optionally, you can enable
    a one-off bootstrap request (useful to verify the wiring) by setting
    `bootstrap_hello=True`.
    """

    bootstrap_hello: bool = False
    poll_interval_s: float = 0.5
    mcp_stdio_command: str | None = None
    mcp_stdio_args: tuple[str, ...] = ()

    async def run(self) -> None:  # pragma: no cover - requires network to exercise
        mcp_servers = []
        if self.mcp_stdio_command:
            params = {"command": self.mcp_stdio_command}
            if self.mcp_stdio_args:
                params["args"] = list(self.mcp_stdio_args)
            mcp_servers = [MCPServerStdio(params=params)]

        if self.bootstrap_hello:
            agent = Agent(
                name="Gateway",
                instructions="You only respond in haikus.",
                mcp_servers=mcp_servers,
            )
            result = await Runner.run(agent, "Hello from ResoBotGW")
            logger.info("Bootstrap result: %s", getattr(result, "final_output", "<no output>"))

        logger.info("OpenAI Agents runner active; idling until cancellation")
        try:
            while True:
                await asyncio.sleep(self.poll_interval_s)
        except asyncio.CancelledError:
            logger.info("OpenAI Agents runner cancelled; shutting down")
            raise
