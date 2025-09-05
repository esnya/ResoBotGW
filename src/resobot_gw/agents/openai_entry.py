"""Console entrypoint wired to the OpenAI Agents runner.

This entrypoint imports the Agents SDK adapter at module import time to respect
the "no dynamic import" rule. Use `resobot-gw-openai run` to start it.
"""

from __future__ import annotations

import argparse
import logging
import sys

from resobot_gw.agents.openai_runner import OpenAIAgentsRunner
from resobot_gw.config import Config
from resobot_gw.runtime import GatewayRuntime


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resobot-gw-openai",
        description=("Gateway using OpenAI Agents SDK (imports at startup; no dynamic import)"),
    )
    subparsers = parser.add_subparsers(dest="command")

    p_run = subparsers.add_parser("run", help="Start the gateway with Agents SDK")
    p_run.add_argument("--dry-run", action="store_true", help="Skip external init")
    p_run.add_argument(
        "--bootstrap-hello",
        action="store_true",
        help="Run a one-off hello to verify wiring",
    )
    p_run.add_argument(
        "--log-level",
        default="INFO",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"],
        help="Logging level",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        logging.basicConfig(
            level=getattr(logging, args.log_level, logging.INFO),
            format="%(levelname)s [cid=%(cid)s] %(name)s: %(message)s",
        )
        runtime = GatewayRuntime()
        mcp_cmd: str | None = None
        mcp_args: tuple[str, ...] = ()
        if not args.dry_run:
            cfg = Config.from_env()
            mcp_cmd = cfg.mcp_stdio_command
            # Parse args as whitespace-separated tokens if provided
            if cfg.mcp_stdio_args:
                mcp_args = tuple(a for a in cfg.mcp_stdio_args.split() if a)

        runner = OpenAIAgentsRunner(
            bootstrap_hello=bool(args.bootstrap_hello),
            mcp_stdio_command=mcp_cmd,
            mcp_stdio_args=mcp_args,
        )
        return runtime.start(dry_run=bool(args.dry_run), runner=runner)

    parser.print_help()
    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
