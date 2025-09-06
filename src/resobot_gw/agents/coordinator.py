"""Coordinator wiring stub proposers to the Arbiter.

Allows testing inter-agent cooperation by collecting stub intents each tick and
committing compatible ones via the `Arbiter`. Emits a `commit` event on the Bus.
"""

from __future__ import annotations

import asyncio
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum

from resobot_gw.bus import Bus, Event

from .orchestrator import Arbiter, Intent


class ReasoningEffort(StrEnum):
    """Relative effort level for reasoning-heavy agents."""

    low = "low"
    medium = "medium"
    high = "high"


@dataclass(frozen=True)
class AgentSpec:
    """Static configuration for an Agent."""

    name: str
    model: str
    instructions: str
    reasoning: ReasoningEffort


class Proposer:
    """Simple stub input interface for Agents.

    Implement `propose()` to return any intents for the current tick.
    """

    def propose(self) -> Iterable[Intent]:  # pragma: no cover - interface stub
        return ()


@dataclass
class AsyncProposer:
    """Async variant allowing concurrent proposal gathering."""

    spec: AgentSpec

    async def propose(self) -> Iterable[Intent]:  # pragma: no cover - interface stub
        return ()


@dataclass
class Coordinator:
    arbiter: Arbiter
    bus: Bus
    topic_commit: str = "commit"

    def tick(self, proposers: Sequence[Proposer]) -> list[Intent]:
        proposals: list[Intent] = []
        for p in proposers:
            proposals.extend(p.propose())
        committed = self.arbiter.tick(proposals)
        if committed:
            self.bus.publish(Event(topic=self.topic_commit, payload=committed))
        return committed

    async def tick_async(self, proposers: Sequence[AsyncProposer]) -> list[Intent]:
        proposals: list[Intent] = []
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(p.propose()) for p in proposers]
        for t in tasks:
            proposals.extend(list(t.result()))
        committed = self.arbiter.tick(proposals)
        if committed:
            self.bus.publish(Event(topic=self.topic_commit, payload=committed))
        return committed
