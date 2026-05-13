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
