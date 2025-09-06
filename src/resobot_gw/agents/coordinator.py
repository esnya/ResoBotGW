"""Coordinator wiring stub proposers to the Arbiter.

Allows testing inter-agent cooperation by collecting stub intents each tick and
committing compatible ones via the `Arbiter`. Emits a `commit` event on the Bus.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from resobot_gw.bus import Bus, Event

from .orchestrator import Arbiter, Intent


class Proposer:
    """Simple stub input interface for Agents.

    Implement `propose()` to return any intents for the current tick.
    """

    def propose(self) -> Iterable[Intent]:  # pragma: no cover - interface stub
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
