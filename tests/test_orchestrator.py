from __future__ import annotations

from resobot_gw.agents.orchestrator import Arbiter, Intent, Resource, Tier


def mk_int(
    agent: str,
    kind: str,
    res: tuple[Resource, ...],
    *,
    tier: Tier,
    score: float = 1.0,
    hold_ms: int = 50,
) -> Intent:
    return Intent(
        agent=agent,
        kind=kind,
        params={},
        resources=res,
        score=score,
        hold_ms=hold_ms,
        tier=tier,
    )


def test_parallel_say_look_move_commits() -> None:
    arb = Arbiter(now_ms_fn=lambda: 1000)
    say = mk_int("dlg", "say", (Resource.speech,), tier=Tier.reflex)
    look = mk_int("gaze", "look_at", (Resource.head,), tier=Tier.reflex)
    move = mk_int("nav", "move_to", (Resource.locomotion,), tier=Tier.activity)

    committed = arb.tick([say, look, move])
    kinds = {c.kind for c in committed}
    assert {"say", "look_at", "move_to"} == kinds


def test_preempt_lower_tier_lock() -> None:
    # planner holds speech, reflex say should preempt
    now = 1000
    arb = Arbiter(now_ms_fn=lambda: now)
    planner_say = mk_int("plan", "say", (Resource.speech,), tier=Tier.planner, hold_ms=500)
    committed1 = arb.tick([planner_say])
    assert committed1
    assert committed1[0].tier is Tier.planner

    # Next tick same time, reflex arrives and should preempt lock
    reflex_say = mk_int("dlg", "say", (Resource.speech,), tier=Tier.reflex)
    committed2 = arb.tick([reflex_say])
    assert committed2
    assert committed2[0].tier is Tier.reflex


def test_locomotion_and_hand_allowed() -> None:
    arb = Arbiter(now_ms_fn=lambda: 1000)
    move = mk_int("nav", "move_to", (Resource.locomotion,), tier=Tier.activity)
    grab = mk_int("mani", "grab", (Resource.hands_l,), tier=Tier.activity)

    committed = arb.tick([move, grab])
    kinds = {c.kind for c in committed}
    # △ in spec treated as allowed in v0
    assert kinds == {"move_to", "grab"}
