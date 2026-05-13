"""Tests for simulations.lightspeed -- critical alpha, speed analysis, and reporting."""

import math

import pytest

from simulations.lightspeed import (
    critical_alpha,
    decay_rate_isolated,
    effective_speed,
    lightspeed_report,
    phase_scan,
)
from simulations.propagation import COMPRESSION, Graph, propagate


class TestCriticalAlpha:
    def test_degree_two(self):
        # 1-D chain: alpha_crit = (pi/2 - 1) / 2 ~= 0.2854
        expected = (math.pi / 2 - 1) / 2
        assert critical_alpha(2) == pytest.approx(expected)

    def test_degree_four(self):
        expected = (math.pi / 2 - 1) / 4
        assert critical_alpha(4) == pytest.approx(expected)

    def test_degree_zero_returns_inf(self):
        assert critical_alpha(0) == math.inf


class TestDecayRate:
    def test_value(self):
        assert decay_rate_isolated() == pytest.approx(COMPRESSION)


class TestEffectiveSpeed:
    def test_zero_timesteps(self):
        g = Graph.chain(5)
        result = propagate(g, [1.0, 0.0, 0.0, 0.0, 0.0], alpha=0.5, timesteps=0)
        assert effective_speed(result) == 0.0

    def test_supercritical_has_positive_speed(self):
        g = Graph.chain(50)
        initial = [0.0] * 50
        initial[0] = 1.0
        result = propagate(g, initial, alpha=0.5, timesteps=30)
        speed = effective_speed(result)
        assert speed > 0.0

    def test_subcritical_has_zero_or_low_speed(self):
        g = Graph.chain(50)
        initial = [0.0] * 50
        initial[0] = 1.0
        result = propagate(g, initial, alpha=0.01, timesteps=30)
        speed = effective_speed(result)
        assert speed < 0.5

    def test_speed_does_not_exceed_one(self):
        g = Graph.chain(100)
        initial = [0.0] * 100
        initial[0] = 1.0
        result = propagate(g, initial, alpha=2.0, timesteps=50)
        speed = effective_speed(result)
        # cannot exceed 1 node/step (causal limit)
        assert speed <= 1.0 + 1e-9


class TestPhaseScan:
    def test_returns_correct_length(self):
        g = Graph.chain(20)
        alphas = [0.0, 0.3, 0.6, 1.0]
        results = phase_scan(g, source_node=0, alpha_values=alphas, timesteps=10)
        assert len(results) == 4

    def test_each_entry_is_triple(self):
        g = Graph.chain(10)
        results = phase_scan(g, source_node=0, alpha_values=[0.5], timesteps=5)
        a, speed, total = results[0]
        assert isinstance(a, float)
        assert isinstance(speed, float)
        assert isinstance(total, float)

    def test_higher_alpha_gives_more_intensity(self):
        g = Graph.chain(20)
        results = phase_scan(g, source_node=0, alpha_values=[0.1, 0.9], timesteps=10)
        _, _, total_low = results[0]
        _, _, total_high = results[1]
        assert total_high > total_low


class TestLightspeedReport:
    def test_chain_report_contains_key_fields(self):
        report = lightspeed_report(topology="chain", num_nodes=20, alpha=0.5)
        assert "LIGHTSPEED PROPAGATION ANALYSIS" in report
        assert "chain" in report
        assert "supercritical" in report

    def test_subcritical_report(self):
        report = lightspeed_report(topology="chain", num_nodes=20, alpha=0.1)
        assert "subcritical" in report.lower()

    def test_ring_topology(self):
        report = lightspeed_report(topology="ring", num_nodes=20, alpha=0.5)
        assert "ring" in report

    def test_grid_topology(self):
        report = lightspeed_report(topology="grid", num_nodes=25, alpha=0.3)
        assert "grid" in report

    def test_complete_topology(self):
        report = lightspeed_report(topology="complete", num_nodes=10, alpha=0.1)
        assert "complete" in report

    def test_unknown_topology_raises(self):
        with pytest.raises(ValueError, match="unknown topology"):
            lightspeed_report(topology="hexagonal")

    def test_wavefront_snapshots_present(self):
        report = lightspeed_report(topology="chain", num_nodes=20, timesteps=16)
        assert "t=" in report
