"""Async runtime for ResoBotGW.

Centers the application lifecycle around an async Agent runner. No dynamic
imports and no try-wrapped imports as per policy.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from .agents.interface import AgentRunner
from .agents.runner import create_default_runner
from .config import Config
from .obs import CorrelationFilter, new_correlation_id

logger = logging.getLogger(__name__)


@dataclass
class GatewayRuntime:
    """Gateway runtime orchestrating Agents and IO bridges.

    For now, this is a skeleton that validates configuration and wires the
    OpenAI client when not in dry-run mode.
    """

    async def run(self, *, dry_run: bool = False, runner: AgentRunner | None = None) -> int:
        """Run the gateway runtime asynchronously.

        Returns a process-like exit code (0 success, non-zero failure).
        """
        # Ensure correlation ID present in logs
        logging.getLogger().addFilter(CorrelationFilter())
        cid = new_correlation_id()
        logger.info("Starting ResoBotGW cid=%s dry_run=%s", cid, dry_run)

        try:
            if dry_run:
                logger.debug("Dry-run: skipping external service initialization")
                return 0

            # Load and validate configuration (non-null)
            _ = Config.from_env()

            # Select agent runner (default placeholder for now)
            agent_runner = runner or create_default_runner()

            # Run until cancelled
            await agent_runner.run()
            return 0
        except ValueError as cfg_err:
            logger.error("Configuration error: %s", cfg_err)
            return 2
        except asyncio.CancelledError:  # pragma: no cover - cancellation path
            logger.info("Cancelled; shutting down cleanly")
            return 0
        except Exception:  # pragma: no cover - defensive
            logger.exception("Unexpected error")
            return 3

    def start(self, *, dry_run: bool = False, runner: AgentRunner | None = None) -> int:
        """Sync entrypoint that runs the async runtime with asyncio.run()."""
        return asyncio.run(self.run(dry_run=dry_run, runner=runner))
