from __future__ import annotations

import asyncio

from resobot_gw.agents.coordinator import (
    AgentSpec,
    AsyncProposer,
    Coordinator,
    ReasoningEffort,
)
from resobot_gw.agents.orchestrator import Arbiter, Intent, Resource, Tier
from resobot_gw.bus import Bus


class DummyProposer(AsyncProposer):
    def __init__(self, spec: AgentSpec, intent: Intent, delay: float) -> None:
        super().__init__(spec)
        self._intent = intent
        self._delay = delay

    async def propose(self) -> tuple[Intent, ...]:
        await asyncio.sleep(self._delay)
        return (self._intent,)


def test_tick_async_commits() -> None:
    arb = Arbiter(now_ms_fn=lambda: 1000)
    coord = Coordinator(arbiter=arb, bus=Bus())
    spec1 = AgentSpec(
        name="dlg",
        model="gpt",
        instructions="say hi",
        reasoning=ReasoningEffort.low,
    )
    spec2 = AgentSpec(
        name="nav",
        model="gpt",
        instructions="move",
        reasoning=ReasoningEffort.low,
    )
    intent1 = Intent(
        agent="dlg",
        kind="say",
        params={},
        resources=(Resource.speech,),
        score=1.0,
        hold_ms=50,
        tier=Tier.reflex,
    )
    intent2 = Intent(
        agent="nav",
        kind="move",
        params={},
        resources=(Resource.locomotion,),
        score=1.0,
        hold_ms=50,
        tier=Tier.activity,
    )
    p1 = DummyProposer(spec1, intent1, delay=0.05)
    p2 = DummyProposer(spec2, intent2, delay=0.05)
    committed = asyncio.run(coord.tick_async([p1, p2]))
    kinds = {c.kind for c in committed}
    assert kinds == {"say", "move"}
