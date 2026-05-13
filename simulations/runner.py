"""CLI runner for the lightspeed propagation simulation.

Usage
-----
    uv run python -m simulations.runner [OPTIONS]

Options are parsed from environment variables or command-line flags.
"""

import argparse

from .lightspeed import lightspeed_report, phase_scan
from .propagation import Graph


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Discrete intensity-propagation simulation",
    )
    p.add_argument(
        "--topology",
        choices=["chain", "ring", "grid", "complete"],
        default="chain",
        help="network topology (default: chain)",
    )
    p.add_argument(
        "--nodes",
        type=int,
        default=100,
        help="number of nodes (default: 100)",
    )
    p.add_argument(
        "--alpha",
        type=float,
        default=0.5,
        help="propagation strength alpha (default: 0.5)",
    )
    p.add_argument(
        "--timesteps",
        type=int,
        default=60,
        help="simulation length (default: 60)",
    )
    p.add_argument(
        "--phase-scan",
        action="store_true",
        help="run a phase-scan over alpha in [0, 1] and print results",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)

    if args.phase_scan:
        _run_phase_scan(args)
    else:
        report = lightspeed_report(
            topology=args.topology,
            num_nodes=args.nodes,
            alpha=args.alpha,
            timesteps=args.timesteps,
        )
        print(report)


def _run_phase_scan(args: argparse.Namespace) -> None:
    graph = Graph.chain(args.nodes)
    alphas = [i * 0.02 for i in range(51)]
    results = phase_scan(
        graph,
        source_node=0,
        alpha_values=alphas,
        timesteps=args.timesteps,
    )

    print("=" * 50)
    print("  PHASE SCAN -- alpha vs effective speed")
    print("=" * 50)
    print(f"  {'alpha':>8s}  {'speed':>10s}  {'total_B':>12s}")
    print("  " + "-" * 34)
    for a, speed, total in results:
        marker = " <- critical" if 0.27 < a < 0.30 else ""
        print(f"  {a:8.4f}  {speed:10.4f}  {total:12.6f}{marker}")
    print("=" * 50)


if __name__ == "__main__":
    main()
