from __future__ import annotations

import os
import re
import struct
import subprocess
import sys
import tempfile
import threading
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "designforge" / "scripts" / "designforge.py"
ADAPTER = ROOT / "designforge" / "adapters" / "playwright_browser.py"
REAL_E2E = os.environ.get("DESIGNFORGE_REAL_BROWSER_E2E") == "1"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise AssertionError("artifact is not PNG")
    if data[12:16] != b"IHDR":
        raise AssertionError("PNG IHDR chunk missing")
    return struct.unpack(">II", data[16:24])


@unittest.skipUnless(REAL_E2E, "set DESIGNFORGE_REAL_BROWSER_E2E=1 for real Playwright E2E")
class PlaywrightRealE2ETests(unittest.TestCase):
    def test_real_chromium_render_capture_validate_and_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            target.mkdir()
            site = root / "site"
            site.mkdir()
            (site / "index.html").write_text(
                """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>DesignForge Browser E2E</title>
<style>
  html, body { margin: 0; min-height: 100%; font-family: sans-serif; background: #f5f5f5; }
  main { width: 720px; margin: 64px auto; padding: 32px; background: white; border-radius: 12px; }
  h1 { margin: 0 0 12px; font-size: 32px; }
  p { margin: 0; color: #444; }
</style>
</head>
<body>
<main id="ready" data-state="ready">
  <h1>DesignForge real browser E2E</h1>
  <p>Rendered by Chromium through the optional Playwright adapter.</p>
</main>
</body>
</html>
""",
                encoding="utf-8",
            )

            result = run("init", str(target), "--mode", "refactor")
            self.assertEqual(result.returncode, 0, result.stderr)
            result = run("visual", "init", str(target))
            self.assertEqual(result.returncode, 0, result.stderr)

            handler = partial(SimpleHTTPRequestHandler, directory=str(site))
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_port}/index.html"
                result = run(
                    "visual",
                    "render",
                    str(target),
                    "--surface",
                    "Browser Fixture",
                    "--state",
                    "ready",
                    "--viewport",
                    "1280x800",
                    "--adapter",
                    sys.executable,
                    str(ADAPTER),
                    "--url",
                    url,
                    "--browser",
                    "chromium",
                    "--wait-for-selector",
                    "#ready",
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

            self.assertEqual(result.returncode, 0, result.stderr)
            match = re.search(r"^Render artifact: (.+)$", result.stdout, re.MULTILINE)
            self.assertIsNotNone(match, result.stdout)
            artifact = Path(match.group(1).strip())
            self.assertTrue(artifact.is_file())
            self.assertEqual(png_dimensions(artifact), (1280, 800))

            run_id = artifact.parent.name
            self.assertRegex(run_id, r"^[0-9a-f]{32}$")

            result = run("visual", "staging", "list", str(target))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(run_id, result.stdout)

            # This is a disposable mechanical pipeline test, not a claim about
            # the visual quality of an external product. The generated PNG is
            # inspected above for the exact expected render dimensions before
            # exercising the persistent capture handoff.
            result = run(
                "visual",
                "capture",
                str(artifact),
                str(target),
                "--surface",
                "Browser Fixture",
                "--state",
                "ready",
                "--viewport",
                "1280x800",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            evidence = list(
                (target / ".DesignForge" / "reviews" / "visual-evidence").glob("*.png")
            )
            self.assertEqual(len(evidence), 1)
            self.assertTrue(evidence[0].is_file())

            result = run("visual", "verdict", "pass", str(target))
            self.assertEqual(result.returncode, 0, result.stderr)
            result = run("visual", "validate", str(target))
            self.assertEqual(result.returncode, 0, result.stderr)

            result = run(
                "visual",
                "staging",
                "clean",
                str(target),
                "--run",
                run_id,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(artifact.parent.exists())
            self.assertTrue(evidence[0].is_file())


if __name__ == "__main__":
    unittest.main()
