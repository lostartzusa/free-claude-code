"""Lightweight HTTP server for the propagation dashboard.

Serves the static HTML dashboard using stdlib ``http.server`` so no extra
dependencies are needed.

Usage::

    uv run python -m simulations.dashboard.serve [--port PORT]
"""

import argparse
import functools
import http.server
import os
import sys
from pathlib import Path

DASHBOARD_DIR: Path = Path(__file__).resolve().parent


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Serve the lightspeed propagation dashboard",
    )
    p.add_argument(
        "--port",
        type=int,
        default=8050,
        help="port to serve on (default: 8050)",
    )
    p.add_argument(
        "--bind",
        default="0.0.0.0",
        help="address to bind to (default: 0.0.0.0)",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    """Start the dashboard HTTP server."""
    args = _build_parser().parse_args(argv)
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=os.fspath(DASHBOARD_DIR),
    )
    server = http.server.HTTPServer((args.bind, args.port), handler)
    url = f"http://localhost:{args.port}"
    print(f"Dashboard running at {url}")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down")
        sys.exit(0)


if __name__ == "__main__":
    main()
