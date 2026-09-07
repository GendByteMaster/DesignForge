from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "designforge" / "scripts" / "designforge.py"
ADAPTER = ROOT / "designforge" / "adapters" / "playwright_browser.py"


def run(
    *args: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )


class PlaywrightBrowserAdapterTests(unittest.TestCase):
    def init_target(self, target: Path) -> None:
        result = run(str(CLI), "init", str(target), "--mode", "refactor")
        self.assertEqual(result.returncode, 0, result.stderr)

    def write_fake_playwright(self, root: Path) -> Path:
        package = root / "playwright"
        package.mkdir()
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "sync_api.py").write_text(
            textwrap.dedent(
                """
                from pathlib import Path

                class Error(Exception):
                    pass

                class TimeoutError(Error):
                    pass

                class Locator:
                    def __init__(self, page, selector):
                        self.page = page
                        self.selector = selector

                    def wait_for(self, **kwargs):
                        self.page.waited_for = self.selector

                    def screenshot(self, **kwargs):
                        Path(kwargs["path"]).write_bytes(b"\\x89PNG\\r\\n\\x1a\\nlocator")

                class Page:
                    def __init__(self):
                        self.waited_for = None

                    def goto(self, url, **kwargs):
                        self.url = url

                    def locator(self, selector):
                        return Locator(self, selector)

                    def wait_for_timeout(self, delay):
                        self.delay = delay

                    def screenshot(self, **kwargs):
                        Path(kwargs["path"]).write_bytes(b"\\x89PNG\\r\\n\\x1a\\npage")

                class Context:
                    def new_page(self):
                        return Page()

                    def close(self):
                        pass

                class Browser:
                    def new_context(self, **kwargs):
                        return Context()

                    def close(self):
                        pass

                class BrowserType:
                    def launch(self, **kwargs):
                        return Browser()

                class Playwright:
                    chromium = BrowserType()
                    firefox = BrowserType()
                    webkit = BrowserType()

                class Manager:
                    def __enter__(self):
                        return Playwright()

                    def __exit__(self, exc_type, exc, tb):
                        return False

                def sync_playwright():
                    return Manager()
                """
            ),
            encoding="utf-8",
        )
        return root

    def test_adapter_runs_through_public_visual_render_without_registering_capture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            target.mkdir()
            self.init_target(target)
            fake = self.write_fake_playwright(root / "fake")
            pythonpath = str(fake)
            if os.environ.get("PYTHONPATH"):
                pythonpath += os.pathsep + os.environ["PYTHONPATH"]

            result = run(
                str(CLI),
                "visual",
                "render",
                str(target),
                "--surface",
                "Dashboard",
                "--state",
                "default",
                "--viewport",
                "1280x800",
                "--adapter",
                sys.executable,
                str(ADAPTER),
                "--url",
                "http://127.0.0.1:4173/dashboard",
                env={"PYTHONPATH": pythonpath},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Render artifact:", result.stdout)
            self.assertIn("Inspect this artifact", result.stdout)
            artifacts = list(
                (target / ".DesignForge" / "render-staging").glob("*/render.png")
            )
            self.assertEqual(len(artifacts), 1)
            self.assertTrue(artifacts[0].is_file())
            self.assertFalse(
                (target / ".DesignForge" / "reviews" / "VISUAL_QA.md").exists()
            )

    def test_adapter_rejects_non_http_url_before_loading_playwright(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            output.mkdir()
            result = run(
                str(ADAPTER),
                "--url",
                "file:///tmp/index.html",
                env={
                    "DESIGNFORGE_RENDER_PROTOCOL": "designforge-render-adapter-v1",
                    "DESIGNFORGE_OUTPUT_DIR": str(output),
                    "DESIGNFORGE_VIEWPORT": "1280x800",
                },
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("http:// or https://", result.stderr)

    def test_adapter_requires_numeric_viewport_or_explicit_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            output.mkdir()
            result = run(
                str(ADAPTER),
                "--url",
                "http://127.0.0.1:4173",
                env={
                    "DESIGNFORGE_RENDER_PROTOCOL": "designforge-render-adapter-v1",
                    "DESIGNFORGE_OUTPUT_DIR": str(output),
                    "DESIGNFORGE_VIEWPORT": "desktop",
                },
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("numeric WIDTHxHEIGHT", result.stderr)

    def test_adapter_rejects_selector_full_page_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            output.mkdir()
            result = run(
                str(ADAPTER),
                "--url",
                "http://127.0.0.1:4173",
                "--selector",
                "#app",
                "--full-page",
                env={
                    "DESIGNFORGE_RENDER_PROTOCOL": "designforge-render-adapter-v1",
                    "DESIGNFORGE_OUTPUT_DIR": str(output),
                    "DESIGNFORGE_VIEWPORT": "1280x800",
                },
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("cannot be used together", result.stderr)

    def test_adapter_emits_protocol_json_when_run_directly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "out"
            output.mkdir()
            fake = self.write_fake_playwright(root / "fake")
            result = run(
                str(ADAPTER),
                "--url",
                "https://example.com",
                "--viewport",
                "1024x768",
                env={
                    "PYTHONPATH": str(fake),
                    "DESIGNFORGE_RENDER_PROTOCOL": "designforge-render-adapter-v1",
                    "DESIGNFORGE_OUTPUT_DIR": str(output),
                    "DESIGNFORGE_VIEWPORT": "desktop",
                },
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout.strip().splitlines()[-1])
            self.assertEqual(payload["protocol"], "designforge-render-adapter-v1")
            self.assertEqual(payload["artifact"], "render.png")
            self.assertTrue((output / "render.png").is_file())


if __name__ == "__main__":
    unittest.main()
