"""Speed-of-light analysis for the discrete propagation system.

In a discrete lattice the absolute maximum rate at which information can
travel is **1 node per timestep** -- the causal cone of the recurrence.
Whether the wavefront *actually* advances at that speed depends on alpha and
the 2/pi compression factor.

Key results
-----------
* **Isolated node decay**: ``B_{t+1} = (2/pi) B_t`` -- exponential decay
  with rate ``2/pi ~= 0.6366`` per step.
* **Critical alpha on a k-regular graph**: for the peak eigenvalue to
  be >= 1 we need ``(2/pi)(1 + k*alpha) >= 1`` giving
  ``alpha_crit = (pi/2 - 1) / k``.
  On a 1-D chain (k=2) this gives ``alpha_crit ~= 0.2854``.
* **Supercritical regime** (``alpha > alpha_crit``): the wavefront
  advances at 1 node/step (the system's "speed of light").
* **Subcritical regime** (``alpha < alpha_crit``): intensity decays
  faster than it can spread; effective speed -> 0.
"""

import math

from .propagation import COMPRESSION, Graph, PropagationResult, propagate


def critical_alpha(degree: int) -> float:
    """Minimum alpha for sustained propagation on a k-regular graph.

    Derived from ``(2/pi)(1 + k*alpha) >= 1`` giving
    ``alpha = (pi/2 - 1) / k``.
    """
    if degree <= 0:
        return math.inf
    return (math.pi / 2 - 1) / degree


def decay_rate_isolated() -> float:
    """Per-step multiplicative decay for a node with no neighbors."""
    return COMPRESSION


def effective_speed(
    result: PropagationResult,
    threshold: float = 1e-6,
) -> float:
    """Estimate the effective wavefront speed in nodes/timestep.

    Measures how far the furthest excited node travels per step on
    average across the entire run.
    """
    if result.timesteps == 0:
        return 0.0

    positions = [
        result.wavefront_position(t, threshold=threshold)
        for t in range(result.timesteps + 1)
    ]

    first_nonzero = positions[0]
    last_pos = positions[-1]
    if last_pos <= first_nonzero:
        return 0.0

    return (last_pos - first_nonzero) / result.timesteps


def phase_scan(
    graph: Graph,
    source_node: int,
    alpha_values: list[float],
    timesteps: int = 50,
    threshold: float = 1e-6,
) -> list[tuple[float, float, float]]:
    """Scan a range of alpha values and return (alpha, speed, total_intensity).

    Useful for locating the phase transition between decay and
    sustained propagation.
    """
    initial = [0.0] * graph.num_nodes
    initial[source_node] = 1.0

    results: list[tuple[float, float, float]] = []
    for a in alpha_values:
        res = propagate(graph, initial, alpha=a, timesteps=timesteps)
        speed = effective_speed(res, threshold=threshold)
        total = res.total_intensity(timesteps)
        results.append((a, speed, total))
    return results


def lightspeed_report(
    topology: str = "chain",
    num_nodes: int = 100,
    alpha: float = 0.5,
    timesteps: int = 60,
) -> str:
    """Return a human-readable analysis of the propagation dynamics.

    Parameters
    ----------
    topology:
        One of ``"chain"``, ``"ring"``, ``"grid"``, ``"complete"``.
    num_nodes:
        Number of nodes (for grid, uses sqrt x sqrt).
    alpha:
        Propagation strength.
    timesteps:
        Simulation length.
    """
    graph: Graph
    if topology == "chain":
        graph = Graph.chain(num_nodes)
    elif topology == "ring":
        graph = Graph.ring(num_nodes)
    elif topology == "grid":
        side = int(math.sqrt(num_nodes))
        graph = Graph.grid_2d(side, side)
        num_nodes = side * side
    elif topology == "grid3d":
        side = round(num_nodes ** (1.0 / 3))
        graph = Graph.grid_3d(side, side, side)
        num_nodes = side * side * side
    elif topology == "complete":
        graph = Graph.complete(num_nodes)
    else:
        msg = f"unknown topology {topology!r}"
        raise ValueError(msg)

    initial = [0.0] * num_nodes
    initial[0] = 1.0

    result = propagate(graph, initial, alpha=alpha, timesteps=timesteps)

    typical_degree = graph.degree(min(1, num_nodes - 1))
    alpha_c = critical_alpha(typical_degree)
    speed = effective_speed(result)
    regime = "supercritical" if alpha > alpha_c else "subcritical"

    lines: list[str] = [
        "=" * 60,
        "  LIGHTSPEED PROPAGATION ANALYSIS",
        "=" * 60,
        "",
        f"  Topology          : {topology} ({num_nodes} nodes)",
        f"  Typical degree    : {typical_degree}",
        f"  Compression (2/pi): {COMPRESSION:.6f}",
        f"  alpha (propag.)   : {alpha:.6f}",
        f"  alpha_critical    : {alpha_c:.6f}",
        f"  Regime            : {regime}",
        f"  Timesteps         : {timesteps}",
        "",
        "-- Propagation Results --",
        "",
        f"  Effective speed   : {speed:.4f} nodes/step",
        "  Theoretical max   : 1.0000 nodes/step (speed of light)",
        f"  Speed ratio (v/c) : {speed:.4f}",
        "",
        f"  Initial intensity : {result.total_intensity(0):.6f}",
        f"  Final intensity   : {result.total_intensity(timesteps):.6f}",
        "",
    ]

    if regime == "supercritical":
        lines.extend(
            [
                "-- Supercritical Analysis --",
                "",
                "  The wavefront propagates at the system's speed of light",
                "  (1 node/step). Intensity grows as alpha feeds energy from",
                "  neighbors faster than 2/pi compression removes it.",
                "",
                "  To reach 'real' speed of light (c ~ 3e8 m/s),",
                "  map each node to a spatial distance dx and each step",
                "  to dt such that  dx/dt = c.  For dx = 1 m that gives",
                "  dt ~ 3.33 ns per simulation step.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "-- Subcritical Analysis --",
                "",
                f"  alpha < alpha_crit ({alpha:.4f} < {alpha_c:.4f}): intensity",
                "  decays faster than it spreads. The wavefront stalls.",
                f"  Increase alpha above {alpha_c:.4f} to reach lightspeed.",
                "",
            ]
        )

    lines.append("-- Wavefront Snapshots --")
    lines.append("")
    snapshot_times = list(range(0, timesteps + 1, max(1, timesteps // 8)))
    if timesteps not in snapshot_times:
        snapshot_times.append(timesteps)

    bar_width = 50
    for t in snapshot_times:
        state = result.history[t]
        max_val = max(state) if max(state) > 0 else 1.0
        bar_chars: list[str] = []
        display_nodes = min(num_nodes, bar_width)
        step = max(1, num_nodes // display_nodes)
        for idx in range(0, min(num_nodes, display_nodes * step), step):
            normalised = state[idx] / max_val
            if normalised > 0.75:
                bar_chars.append("#")
            elif normalised > 0.50:
                bar_chars.append("=")
            elif normalised > 0.25:
                bar_chars.append("-")
            elif normalised > 0.01:
                bar_chars.append(".")
            else:
                bar_chars.append(" ")
        bar = "".join(bar_chars)
        lines.append(f"  t={t:3d} |{bar}|")

    lines.extend(["", "=" * 60])
    return "\n".join(lines)
