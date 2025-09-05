"""Default Agent runner and composition.

This is an adapter point for the OpenAI Agents SDK. Do not import external
SDKs here until their API is confirmed. Provide a no-op default.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from .interface import AgentRunner

logger = logging.getLogger(__name__)


@dataclass
class NoopRunner(AgentRunner):
    """A minimal runner that idles until cancelled.

    Useful as a placeholder before integrating a real Agents SDK.
    """

    poll_interval_s: float = 0.5

    async def run(self) -> None:  # pragma: no cover - trivial loop
        logger.warning("NoopRunner active: Agents orchestration not yet implemented")
        try:
            while True:
                await asyncio.sleep(self.poll_interval_s)
        except asyncio.CancelledError:
            logger.info("NoopRunner cancelled; shutting down")
            raise


def create_default_runner() -> AgentRunner:
    """Factory for the default runner used by the runtime."""
    return NoopRunner()
