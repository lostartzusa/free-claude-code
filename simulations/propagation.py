"""Core propagation engine.

Defines the graph structure and runs the discrete recurrence::

    B_{t+1}(i) = (2/pi) [B_t(i) + alpha * sum_{j in N(i)} B_t(j)]

where ``2/pi ~= 0.6366`` acts as a compression operator each timestep.
"""

import math
from dataclasses import dataclass, field
from typing import Self

COMPRESSION: float = 2.0 / math.pi  # ~= 0.6366


@dataclass
class Graph:
    """Undirected graph stored as an adjacency list.

    Nodes are labelled 0 .. n-1.
    """

    num_nodes: int
    adjacency: dict[int, list[int]] = field(default_factory=dict)

    def add_edge(self, u: int, v: int) -> None:
        self.adjacency.setdefault(u, []).append(v)
        self.adjacency.setdefault(v, []).append(u)

    def neighbors(self, node: int) -> list[int]:
        return self.adjacency.get(node, [])

    def degree(self, node: int) -> int:
        return len(self.neighbors(node))

    # -- factory helpers --

    @classmethod
    def chain(cls, n: int) -> Self:
        """1-D chain: 0-1-2-..-(n-1)."""
        g = cls(num_nodes=n)
        for i in range(n - 1):
            g.add_edge(i, i + 1)
        return g

    @classmethod
    def ring(cls, n: int) -> Self:
        """Cycle: chain with an extra edge closing the loop."""
        g = cls.chain(n)
        if n > 2:
            g.add_edge(0, n - 1)
        return g

    @classmethod
    def grid_2d(cls, rows: int, cols: int) -> Self:
        """2-D rectangular lattice with 4-connectivity."""
        n = rows * cols
        g = cls(num_nodes=n)
        for r in range(rows):
            for c in range(cols):
                node = r * cols + c
                if c + 1 < cols:
                    g.add_edge(node, node + 1)
                if r + 1 < rows:
                    g.add_edge(node, node + cols)
        return g

    @classmethod
    def complete(cls, n: int) -> Self:
        """Fully connected graph on *n* nodes."""
        g = cls(num_nodes=n)
        for i in range(n):
            for j in range(i + 1, n):
                g.add_edge(i, j)
        return g


@dataclass
class PropagationResult:
    """Full history of a propagation run."""

    timesteps: int
    alpha: float
    history: list[list[float]]  # history[t][i] = B_t(i)

    @property
    def num_nodes(self) -> int:
        return len(self.history[0]) if self.history else 0

    def intensity_at(self, t: int, node: int) -> float:
        return self.history[t][node]

    def total_intensity(self, t: int) -> float:
        return sum(self.history[t])

    def wavefront_position(self, t: int, threshold: float = 1e-6) -> int:
        """Index of the furthest node whose intensity exceeds *threshold*."""
        state = self.history[t]
        furthest = -1
        for i, val in enumerate(state):
            if val > threshold:
                furthest = i
        return furthest


def propagate(
    graph: Graph,
    initial: list[float],
    alpha: float,
    timesteps: int,
) -> PropagationResult:
    """Run the propagation recurrence for *timesteps* steps.

    Parameters
    ----------
    graph:
        Network topology.
    initial:
        Starting intensities B_0(i) for every node.
    alpha:
        Propagation strength (coupling to neighbors).
    timesteps:
        Number of discrete time-steps to simulate.

    Returns
    -------
    PropagationResult with the full state history.
    """
    if len(initial) != graph.num_nodes:
        msg = (
            f"initial has {len(initial)} entries but graph has {graph.num_nodes} nodes"
        )
        raise ValueError(msg)

    history: list[list[float]] = [list(initial)]

    current = list(initial)
    for _ in range(timesteps):
        next_state = [0.0] * graph.num_nodes
        for i in range(graph.num_nodes):
            neighbor_sum = sum(current[j] for j in graph.neighbors(i))
            next_state[i] = COMPRESSION * (current[i] + alpha * neighbor_sum)
        history.append(next_state)
        current = next_state

    return PropagationResult(
        timesteps=timesteps,
        alpha=alpha,
        history=history,
    )
