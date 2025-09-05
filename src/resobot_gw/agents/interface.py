"""Agent runner interfaces for the gateway.

Defines the minimal async contract the runtime depends on, without Protocols.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class AgentRunner(ABC):
    @abstractmethod
    async def run(self) -> None:
        """Run the agent application loop until completion or cancellation."""
        raise NotImplementedError
