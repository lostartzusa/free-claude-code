"""Tests for simulations.runner -- CLI argument parsing and entrypoints."""

from simulations.runner import main


class TestRunner:
    def test_default_run(self, capsys):
        main(["--nodes", "10", "--timesteps", "5"])
        output = capsys.readouterr().out
        assert "LIGHTSPEED PROPAGATION ANALYSIS" in output

    def test_phase_scan_flag(self, capsys):
        main(["--phase-scan", "--nodes", "10", "--timesteps", "5"])
        output = capsys.readouterr().out
        assert "PHASE SCAN" in output

    def test_ring_topology(self, capsys):
        main(["--topology", "ring", "--nodes", "10", "--timesteps", "5"])
        output = capsys.readouterr().out
        assert "ring" in output

    def test_custom_alpha(self, capsys):
        main(["--alpha", "0.1", "--nodes", "10", "--timesteps", "5"])
        output = capsys.readouterr().out
        assert "0.1" in output
