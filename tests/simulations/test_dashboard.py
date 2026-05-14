"""Tests for simulations.dashboard -- server and static assets."""

import threading
import time
import urllib.request
from http.client import HTTPResponse

from simulations.dashboard.serve import DASHBOARD_DIR, main


class TestDashboardAssets:
    def test_index_html_exists(self):
        index = DASHBOARD_DIR / "index.html"
        assert index.is_file()

    def test_index_html_contains_formula(self):
        text = (DASHBOARD_DIR / "index.html").read_text(encoding="utf-8")
        assert "COMPRESSION" in text
        assert "2.0 / Math.PI" in text

    def test_index_html_has_canvas_elements(self):
        text = (DASHBOARD_DIR / "index.html").read_text(encoding="utf-8")
        assert 'id="wavefront"' in text
        assert 'id="phase-chart"' in text

    def test_index_html_has_controls(self):
        text = (DASHBOARD_DIR / "index.html").read_text(encoding="utf-8")
        assert 'id="alpha"' in text
        assert 'id="topology"' in text
        assert 'id="nodes"' in text

    def test_index_html_implements_all_topologies(self):
        text = (DASHBOARD_DIR / "index.html").read_text(encoding="utf-8")
        for topo in ("chain", "ring", "grid", "complete"):
            assert f"'{topo}'" in text

    def test_dashboard_dir_is_correct_path(self):
        assert DASHBOARD_DIR.is_dir()
        assert (DASHBOARD_DIR / "__init__.py").is_file()


class TestDashboard3DAssets:
    def test_index3d_html_exists(self):
        index3d = DASHBOARD_DIR / "index3d.html"
        assert index3d.is_file()

    def test_index3d_html_contains_propagation_engine(self):
        text = (DASHBOARD_DIR / "index3d.html").read_text(encoding="utf-8")
        assert "COMPRESSION" in text
        assert "2.0 / Math.PI" in text

    def test_index3d_html_has_three_js_import(self):
        text = (DASHBOARD_DIR / "index3d.html").read_text(encoding="utf-8")
        assert "three" in text
        assert "OrbitControls" in text

    def test_index3d_html_has_3d_canvas(self):
        text = (DASHBOARD_DIR / "index3d.html").read_text(encoding="utf-8")
        assert 'id="canvas3d"' in text

    def test_index3d_html_has_controls(self):
        text = (DASHBOARD_DIR / "index3d.html").read_text(encoding="utf-8")
        assert 'id="alpha"' in text
        assert 'id="side"' in text
        assert 'id="threshold"' in text
        assert 'id="slice"' in text

    def test_index3d_html_builds_3d_graph(self):
        text = (DASHBOARD_DIR / "index3d.html").read_text(encoding="utf-8")
        assert "buildGraph3D" in text

    def test_2d_links_to_3d(self):
        text = (DASHBOARD_DIR / "index.html").read_text(encoding="utf-8")
        assert 'href="index3d.html"' in text

    def test_3d_links_to_2d(self):
        text = (DASHBOARD_DIR / "index3d.html").read_text(encoding="utf-8")
        assert 'href="index.html"' in text

    def test_index3d_has_covid_presets(self):
        text = (DASHBOARD_DIR / "index3d.html").read_text(encoding="utf-8")
        assert "COVID_PRESETS" in text
        assert "r0ToAlpha" in text
        assert "alphaToR0" in text

    def test_index3d_has_r0_values(self):
        text = (DASHBOARD_DIR / "index3d.html").read_text(encoding="utf-8")
        assert "2.5" in text
        assert "5.0" in text
        assert "12.0" in text

    def test_index3d_has_epidemic_colors(self):
        text = (DASHBOARD_DIR / "index3d.html").read_text(encoding="utf-8")
        assert "epidemicColor" in text

    def test_index3d_has_preset_buttons(self):
        text = (DASHBOARD_DIR / "index3d.html").read_text(encoding="utf-8")
        assert 'id="preset-original"' in text
        assert 'id="preset-delta"' in text
        assert 'id="preset-omicron"' in text

    def test_index3d_tracks_previous_state(self):
        text = (DASHBOARD_DIR / "index3d.html").read_text(encoding="utf-8")
        assert "state.previous" in text
        assert "state.peakEver" in text

    def test_index3d_has_infection_counters(self):
        text = (DASHBOARD_DIR / "index3d.html").read_text(encoding="utf-8")
        assert "m-infected" in text
        assert "m-new-infected" in text
        assert "m-recovered" in text
        assert "m-uninfected" in text


class TestTwinPrimesAssets:
    def test_primes_html_exists(self):
        assert (DASHBOARD_DIR / "primes.html").is_file()

    def test_primes_html_has_primality_test(self):
        text = (DASHBOARD_DIR / "primes.html").read_text(encoding="utf-8")
        assert "isPrime" in text

    def test_primes_html_has_gap_cycle(self):
        text = (DASHBOARD_DIR / "primes.html").read_text(encoding="utf-8")
        assert "GAPS" in text or "[2, 4, 2, 10, 2, 10]" in text

    def test_primes_html_has_color_coding(self):
        text = (DASHBOARD_DIR / "primes.html").read_text(encoding="utf-8")
        for cls in ("prime", "composite", "interval", "twin-prime"):
            assert cls in text

    def test_primes_html_has_stats(self):
        text = (DASHBOARD_DIR / "primes.html").read_text(encoding="utf-8")
        for stat_id in ("m-primes", "m-twins", "m-density", "m-largest-twin"):
            assert stat_id in text

    def test_primes_html_has_navigation(self):
        text = (DASHBOARD_DIR / "primes.html").read_text(encoding="utf-8")
        assert 'href="index.html"' in text
        assert 'href="index3d.html"' in text

    def test_2d_links_to_primes(self):
        text = (DASHBOARD_DIR / "index.html").read_text(encoding="utf-8")
        assert 'href="primes.html"' in text

    def test_3d_links_to_primes(self):
        text = (DASHBOARD_DIR / "index3d.html").read_text(encoding="utf-8")
        assert 'href="primes.html"' in text

    def test_primes_html_has_animate_mode(self):
        text = (DASHBOARD_DIR / "primes.html").read_text(encoding="utf-8")
        assert "animate" in text.lower()


class TestMarbleSimAssets:
    def test_marbles_html_exists(self):
        assert (DASHBOARD_DIR / "marbles.html").is_file()

    def test_marbles_html_has_physics_engine(self):
        text = (DASHBOARD_DIR / "marbles.html").read_text(encoding="utf-8")
        assert "physicsStep" in text
        assert "computeDispersion" in text

    def test_marbles_html_has_collision_impulse(self):
        text = (DASHBOARD_DIR / "marbles.html").read_text(encoding="utf-8")
        assert "restitution" in text
        assert "impulse" in text.lower() or "imp" in text

    def test_marbles_html_has_three_js(self):
        text = (DASHBOARD_DIR / "marbles.html").read_text(encoding="utf-8")
        assert "three" in text
        assert "OrbitControls" in text

    def test_marbles_html_has_charts(self):
        text = (DASHBOARD_DIR / "marbles.html").read_text(encoding="utf-8")
        assert "chart-dispersion" in text
        assert "chart-rate" in text

    def test_marbles_html_has_controls(self):
        text = (DASHBOARD_DIR / "marbles.html").read_text(encoding="utf-8")
        assert 'id="marbles"' in text
        assert 'id="gravity"' in text
        assert 'id="restitution"' in text
        assert 'id="friction"' in text

    def test_marbles_html_has_phase_detection(self):
        text = (DASHBOARD_DIR / "marbles.html").read_text(encoding="utf-8")
        assert "detectPhase" in text
        assert "impact" in text.lower()
        assert "dispersion" in text.lower()

    def test_marbles_html_has_navigation(self):
        text = (DASHBOARD_DIR / "marbles.html").read_text(encoding="utf-8")
        assert 'href="index.html"' in text
        assert 'href="index3d.html"' in text
        assert 'href="primes.html"' in text

    def test_all_pages_link_to_marbles(self):
        for page in ("index.html", "index3d.html", "primes.html"):
            text = (DASHBOARD_DIR / page).read_text(encoding="utf-8")
            assert 'href="marbles.html"' in text, f"{page} missing marbles link"

    def test_marbles_html_has_metrics(self):
        text = (DASHBOARD_DIR / "marbles.html").read_text(encoding="utf-8")
        for metric_id in ("m-time", "m-dispersion", "m-rate", "m-impact", "m-energy"):
            assert metric_id in text


class TestDashboardServer:
    def test_serves_index_html(self):
        port = _find_free_port()
        server_thread = threading.Thread(
            target=main,
            args=(["--port", str(port)],),
            daemon=True,
        )
        server_thread.start()
        time.sleep(0.5)

        resp: HTTPResponse = urllib.request.urlopen(
            f"http://localhost:{port}/index.html",
            timeout=5,
        )
        assert resp.status == 200
        body = resp.read().decode("utf-8")
        assert "LIGHTSPEED PROPAGATION" in body

    def test_serves_3d_html(self):
        port = _find_free_port()
        server_thread = threading.Thread(
            target=main,
            args=(["--port", str(port)],),
            daemon=True,
        )
        server_thread.start()
        time.sleep(0.5)

        resp: HTTPResponse = urllib.request.urlopen(
            f"http://localhost:{port}/index3d.html",
            timeout=5,
        )
        assert resp.status == 200
        body = resp.read().decode("utf-8")
        assert "LIGHTSPEED 3D" in body

    def test_serves_primes_html(self):
        port = _find_free_port()
        server_thread = threading.Thread(
            target=main,
            args=(["--port", str(port)],),
            daemon=True,
        )
        server_thread.start()
        time.sleep(0.5)

        resp: HTTPResponse = urllib.request.urlopen(
            f"http://localhost:{port}/primes.html",
            timeout=5,
        )
        assert resp.status == 200
        body = resp.read().decode("utf-8")
        assert "TWIN PRIME" in body

    def test_serves_marbles_html(self):
        port = _find_free_port()
        server_thread = threading.Thread(
            target=main,
            args=(["--port", str(port)],),
            daemon=True,
        )
        server_thread.start()
        time.sleep(0.5)

        resp: HTTPResponse = urllib.request.urlopen(
            f"http://localhost:{port}/marbles.html",
            timeout=5,
        )
        assert resp.status == 200
        body = resp.read().decode("utf-8")
        assert "HYPOTENUSE" in body

    def test_serves_root_as_index(self):
        port = _find_free_port()
        server_thread = threading.Thread(
            target=main,
            args=(["--port", str(port)],),
            daemon=True,
        )
        server_thread.start()
        time.sleep(0.5)

        resp: HTTPResponse = urllib.request.urlopen(
            f"http://localhost:{port}/",
            timeout=5,
        )
        assert resp.status == 200


def _find_free_port() -> int:
    """Find an available TCP port."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]
