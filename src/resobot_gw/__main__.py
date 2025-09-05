"""Command-line entry for ResoBotGW.

Provides a minimal CLI with a `run` subcommand and `--version` flag.
"""

from __future__ import annotations

import argparse
import logging
import sys

from . import __version__
from .runtime import GatewayRuntime


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resobot-gw",
        description=(
            "Experimental gateway orchestrating concurrent AI Agents for Resonite via ResoBotMCP"
        ),
    )
    parser.add_argument("--version", action="store_true", help="Print version and exit")

    subparsers = parser.add_subparsers(dest="command")

    p_run = subparsers.add_parser("run", help="Start the gateway (skeleton)")
    p_run.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not touch external services; run skeleton only",
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

    if args.version:
        print(__version__)
        return 0

    if args.command == "run":
        logging.basicConfig(
            level=getattr(logging, args.log_level, logging.INFO),
            format="%(levelname)s [cid=%(cid)s] %(name)s: %(message)s",
        )
        runtime = GatewayRuntime()
        # Ensure that the runtime manages the event loop via asyncio.run
        return runtime.start(dry_run=bool(args.dry_run))

    parser.print_help()
    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
