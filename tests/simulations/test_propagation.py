"""Tests for simulations.propagation -- graph construction and the core recurrence."""

import math

import pytest

from simulations.propagation import COMPRESSION, Graph, PropagationResult, propagate

# ── Graph factories ──────────────────────────────────────────────


class TestGraph:
    def test_chain_creates_correct_edges(self):
        g = Graph.chain(5)
        assert g.num_nodes == 5
        assert set(g.neighbors(0)) == {1}
        assert set(g.neighbors(2)) == {1, 3}
        assert set(g.neighbors(4)) == {3}

    def test_ring_closes_the_loop(self):
        g = Graph.ring(5)
        assert 4 in g.neighbors(0)
        assert 0 in g.neighbors(4)

    def test_grid_2d_dimensions(self):
        g = Graph.grid_2d(3, 4)
        assert g.num_nodes == 12
        # corner node has exactly 2 neighbors
        assert g.degree(0) == 2

    def test_complete_graph_degree(self):
        g = Graph.complete(5)
        for i in range(5):
            assert g.degree(i) == 4

    def test_single_node_chain(self):
        g = Graph.chain(1)
        assert g.num_nodes == 1
        assert g.neighbors(0) == []

    def test_two_node_ring(self):
        g = Graph.ring(2)
        assert 1 in g.neighbors(0)
        assert 0 in g.neighbors(1)


# ── Propagation recurrence ───────────────────────────────────────


class TestPropagate:
    def test_initial_state_preserved(self):
        g = Graph.chain(3)
        initial = [1.0, 0.0, 0.0]
        result = propagate(g, initial, alpha=0.5, timesteps=0)
        assert result.history[0] == initial

    def test_single_step_isolated_node(self):
        g = Graph(num_nodes=1)
        result = propagate(g, [1.0], alpha=0.5, timesteps=1)
        assert result.intensity_at(1, 0) == pytest.approx(COMPRESSION)

    def test_isolated_decay_is_geometric(self):
        g = Graph(num_nodes=1)
        result = propagate(g, [1.0], alpha=0.5, timesteps=10)
        for t in range(1, 11):
            expected = COMPRESSION**t
            assert result.intensity_at(t, 0) == pytest.approx(expected, rel=1e-9)

    def test_symmetry_on_ring(self):
        g = Graph.ring(5)
        initial = [1.0, 0.0, 0.0, 0.0, 0.0]
        result = propagate(g, initial, alpha=0.3, timesteps=5)
        # nodes 1 and 4 are symmetric neighbors of source
        assert result.intensity_at(5, 1) == pytest.approx(
            result.intensity_at(5, 4), rel=1e-9
        )

    def test_mismatched_initial_raises(self):
        g = Graph.chain(3)
        with pytest.raises(ValueError, match="initial has 2 entries"):
            propagate(g, [1.0, 0.0], alpha=0.5, timesteps=1)

    def test_propagation_spreads_energy(self):
        g = Graph.chain(5)
        initial = [1.0, 0.0, 0.0, 0.0, 0.0]
        result = propagate(g, initial, alpha=0.5, timesteps=3)
        # after 3 steps node 1 should have nonzero intensity
        assert result.intensity_at(3, 1) > 0.0

    def test_compression_constant(self):
        assert pytest.approx(2.0 / math.pi) == COMPRESSION


# ── PropagationResult helpers ────────────────────────────────────


class TestPropagationResult:
    def test_total_intensity(self):
        result = PropagationResult(
            timesteps=1,
            alpha=0.0,
            history=[[1.0, 2.0, 3.0], [0.5, 1.0, 1.5]],
        )
        assert result.total_intensity(0) == pytest.approx(6.0)
        assert result.total_intensity(1) == pytest.approx(3.0)

    def test_wavefront_position(self):
        result = PropagationResult(
            timesteps=0,
            alpha=0.0,
            history=[[0.0, 0.0, 1.0, 0.0, 0.0]],
        )
        assert result.wavefront_position(0) == 2

    def test_wavefront_position_all_zero(self):
        result = PropagationResult(
            timesteps=0,
            alpha=0.0,
            history=[[0.0, 0.0, 0.0]],
        )
        assert result.wavefront_position(0) == -1

    def test_num_nodes(self):
        result = PropagationResult(
            timesteps=0,
            alpha=0.0,
            history=[[0.0] * 10],
        )
        assert result.num_nodes == 10

    def test_num_nodes_empty(self):
        result = PropagationResult(timesteps=0, alpha=0.0, history=[])
        assert result.num_nodes == 0
