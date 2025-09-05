from __future__ import annotations

from resobot_gw.bus import Bus, Event


def test_bus_publish_subscribe() -> None:
    bus = Bus()
    received: list[Event] = []

    def sub(ev: Event) -> None:
        received.append(ev)

    bus.subscribe("topic", sub)
    bus.publish(Event(topic="topic", payload={"x": 1}))

    assert len(received) == 1
    assert received[0].payload == {"x": 1}
