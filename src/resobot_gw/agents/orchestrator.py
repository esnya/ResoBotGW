"""Minimal agent orchestration primitives.

Implements resources, intents, a compatibility matrix, and an Arbiter that
greedily commits compatible proposals with simple preemption and lock expiry.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from enum import Enum, StrEnum


class Resource(StrEnum):
    speech = "speech"
    locomotion = "locomotion"
    head = "head"
    hands_l = "handsL"
    hands_r = "handsR"
    ui = "ui"
    sensors = "sensors"


class Tier(int, Enum):
    """Priority tier (lower value = higher priority)."""

    reflex = 0
    safety = 1
    activity = 2
    planner = 3


@dataclass(frozen=True)
class Intent:
    """A proposed action from an Agent requiring resources for a short duration."""

    agent: str
    kind: str
    params: dict[str, object]
    resources: tuple[Resource, ...]
    score: float
    hold_ms: int
    tier: Tier


# Compatibility matrix (True = allowed) based on the spec's table.
_ALLOWED: dict[tuple[Resource, Resource], bool] = {}

_R = list(Resource)
for r in _R:
    for c in _R:
        _ALLOWED[r, c] = True

# Disallow same-resource concurrency (self-conflict)
for r in _R:
    _ALLOWED[r, r] = False


# Apply specific constraints from the table
def _ban(a: Resource, b: Resource) -> None:
    _ALLOWED[a, b] = False
    _ALLOWED[b, a] = False


_ban(Resource.speech, Resource.speech)
_ban(Resource.locomotion, Resource.locomotion)
_ban(Resource.head, Resource.head)
_ban(Resource.hands_l, Resource.hands_l)
_ban(Resource.hands_r, Resource.hands_r)
_ban(Resource.ui, Resource.ui)


def resources_compatible(a: Sequence[Resource], b: Sequence[Resource]) -> bool:
    for ra in a:
        for rb in b:
            if not _ALLOWED.get((ra, rb), True):
                return False
    return True


@dataclass
class _Lock:
    holder: str
    tier: Tier
    until_ms: int


@dataclass
class Arbiter:
    """Greedy arbiter with simple preemption and time-based locks."""

    now_ms_fn: Callable[[], int] = field(
        default=lambda: int(time.monotonic() * 1000),
    )  # injection for testing
    _locks: dict[Resource, _Lock] = field(default_factory=dict)

    def _expire(self, now_ms: int) -> None:
        for r, lk in list(self._locks.items()):
            if lk.until_ms <= now_ms:
                del self._locks[r]

    def _can_acquire(self, intent: Intent, now_ms: int) -> bool:
        # Check conflicting locks; allow preemption if higher priority
        for r in intent.resources:
            lk = self._locks.get(r)
            if lk is None:
                continue
            if lk.until_ms <= now_ms:
                continue
            if intent.tier < lk.tier:
                # preempt allowed
                continue
            return False
        return True

    def _acquire(self, intent: Intent, now_ms: int) -> None:
        until = now_ms + max(1, intent.hold_ms)
        for r in intent.resources:
            self._locks[r] = _Lock(holder=intent.agent, tier=intent.tier, until_ms=until)

    def tick(self, proposals: Iterable[Intent]) -> list[Intent]:
        now = self.now_ms_fn()
        self._expire(now)
        # order: tier asc (higher prio first), then score desc
        ordered = sorted(proposals, key=lambda i: (i.tier, -i.score))

        committed: list[Intent] = []
        for intent in ordered:
            # filter by compatibility with already committed intents
            if any(
                not resources_compatible(intent.resources, c.resources) for c in committed
            ):
                continue
            # check locks (with preemption)
            if not self._can_acquire(intent, now):
                continue
            # preempt conflicting locks explicitly
            for r in intent.resources:
                lk = self._locks.get(r)
                if lk and lk.until_ms > now and intent.tier < lk.tier:
                    del self._locks[r]
            self._acquire(intent, now)
            committed.append(intent)
        return committed
