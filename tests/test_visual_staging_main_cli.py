from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "designforge" / "scripts" / "designforge.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class VisualStagingMainCLITests(unittest.TestCase):
    def init_target(self, target: Path) -> None:
        result = run("init", str(target), "--mode", "refactor")
        self.assertEqual(result.returncode, 0, result.stderr)

    def make_run(self, target: Path, run_id: str, *, age_hours: float = 0.0) -> Path:
        run_dir = target / ".DesignForge" / "render-staging" / run_id
        run_dir.mkdir(parents=True)
        (run_dir / "render.png").write_bytes(b"\x89PNG\r\n\x1a\nrender")
        timestamp = time.time() - age_hours * 3600
        os.utime(run_dir, (timestamp, timestamp))
        return run_dir

    def test_visual_staging_list_reports_managed_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self.init_target(target)
            run_id = "a" * 32
            self.make_run(target, run_id)

            result = run("visual", "staging", "list", str(target))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(run_id, result.stdout)
            self.assertIn("render-staging", result.stdout)

    def test_visual_staging_clean_specific_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self.init_target(target)
            first_id = "b" * 32
            second_id = "c" * 32
            first = self.make_run(target, first_id)
            second = self.make_run(target, second_id)

            result = run(
                "visual",
                "staging",
                "clean",
                str(target),
                "--run",
                first_id,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"Removed renderer staging run: {first_id}", result.stdout)
            self.assertFalse(first.exists())
            self.assertTrue(second.exists())

    def test_visual_staging_clean_by_age(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self.init_target(target)
            old_id = "d" * 32
            fresh_id = "e" * 32
            old = self.make_run(target, old_id, age_hours=12)
            fresh = self.make_run(target, fresh_id, age_hours=1)

            result = run(
                "visual",
                "staging",
                "clean",
                str(target),
                "--older-than-hours",
                "6",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(old.exists())
            self.assertTrue(fresh.exists())

    def test_visual_staging_clean_requires_explicit_selector(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self.init_target(target)

            result = run("visual", "staging", "clean", str(target))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("one of the arguments", result.stderr)


if __name__ == "__main__":
    unittest.main()
