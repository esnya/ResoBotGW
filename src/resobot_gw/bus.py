"""In-memory synchronous message bus for internal events.

Simple, typed, and non-null. Suitable for initial orchestration.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    """A basic internal event.

    - topic: domain-specific channel name
    - payload: immutable message data (recommend dataclasses/tuples)
    """

    topic: str
    payload: object


Subscriber = Callable[[Event], None]


class Bus:
    """Synchronous pub/sub bus with per-topic subscribers."""

    def __init__(self) -> None:
        self._subs: dict[str, list[Subscriber]] = defaultdict(list)

    def subscribe(self, topic: str, subscriber: Subscriber) -> None:
        if not topic:
            raise ValueError("topic must be non-empty")
        self._subs[topic].append(subscriber)

    def publish(self, event: Event) -> None:
        subs = list(self._subs.get(event.topic, ()))
        for fn in subs:
            fn(event)
