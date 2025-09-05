from __future__ import annotations

from resobot_gw.runtime import GatewayRuntime


def test_runtime_dry_run() -> None:
    runtime = GatewayRuntime()
    code = runtime.start(dry_run=True)
    assert code == 0
