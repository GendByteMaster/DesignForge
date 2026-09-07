from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "designforge" / "scripts" / "render_staging.py"
DESIGNFORGE = ROOT / "designforge" / "scripts" / "designforge.py"


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class RenderStagingPublicCLITests(unittest.TestCase):
    def init_target(self, target: Path) -> None:
        result = run(DESIGNFORGE, "init", str(target), "--mode", "refactor")
        self.assertEqual(result.returncode, 0, result.stderr)

    def make_run(self, target: Path, run_id: str, *, age_hours: float = 0.0) -> Path:
        run_dir = target / ".DesignForge" / "render-staging" / run_id
        run_dir.mkdir(parents=True)
        (run_dir / "render.png").write_bytes(b"\x89PNG\r\n\x1a\nrender")
        timestamp = time.time() - age_hours * 3600
        os.utime(run_dir, (timestamp, timestamp))
        return run_dir

    def test_list_reports_managed_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self.init_target(target)
            run_id = "a" * 32
            self.make_run(target, run_id)

            result = run(CLI, "list", str(target))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(run_id, result.stdout)
            self.assertIn("render-staging", result.stdout)

    def test_clean_specific_run_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self.init_target(target)
            run_id = "b" * 32
            run_dir = self.make_run(target, run_id)

            result = run(CLI, "clean", str(target), "--run", run_id)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"Removed renderer staging run: {run_id}", result.stdout)
            self.assertFalse(run_dir.exists())

    def test_clean_old_runs_keeps_fresh_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self.init_target(target)
            old_id = "c" * 32
            fresh_id = "d" * 32
            old = self.make_run(target, old_id, age_hours=24)
            fresh = self.make_run(target, fresh_id, age_hours=1)

            result = run(CLI, "clean", str(target), "--older-than-hours", "6")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(old.exists())
            self.assertTrue(fresh.exists())

    def test_clean_requires_initialized_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run(CLI, "list", tmp)
            self.assertEqual(result.returncode, 1)
            self.assertIn("run init first", result.stderr)


if __name__ == "__main__":
    unittest.main()
