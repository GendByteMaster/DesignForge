from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path

from designforge.scripts.render_staging import clean_runs, list_runs


class RenderStagingTests(unittest.TestCase):
    def make_target(self, root: Path) -> Path:
        target = root / "project"
        workspace = target / ".DesignForge"
        workspace.mkdir(parents=True)
        (workspace / "STATE.md").write_text("Current workflow: build\n", encoding="utf-8")
        return target

    def make_run(self, target: Path, run_id: str, *, age_hours: float = 0.0) -> Path:
        run = target / ".DesignForge" / "render-staging" / run_id
        run.mkdir(parents=True)
        (run / "render.png").write_bytes(b"\x89PNG\r\n\x1a\nrender")
        timestamp = time.time() - age_hours * 3600
        os.utime(run, (timestamp, timestamp))
        return run

    def test_list_runs_returns_only_valid_direct_uuid_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            valid = "a" * 32
            self.make_run(target, valid)
            root = target / ".DesignForge" / "render-staging"
            (root / "notes.txt").write_text("keep", encoding="utf-8")
            (root / "not-a-run").mkdir()

            runs, errors = list_runs(target)

            self.assertEqual(errors, [])
            self.assertEqual([run.run_id for run in runs], [valid])
            self.assertGreater(runs[0].size_bytes, 0)

    def test_clean_specific_run_does_not_touch_other_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            first = "a" * 32
            second = "b" * 32
            first_path = self.make_run(target, first)
            second_path = self.make_run(target, second)
            root = target / ".DesignForge" / "render-staging"
            marker = root / "manual-note.txt"
            marker.write_text("preserve", encoding="utf-8")

            removed, errors = clean_runs(target, run_id=first)

            self.assertEqual(errors, [])
            self.assertEqual(removed, [first])
            self.assertFalse(first_path.exists())
            self.assertTrue(second_path.exists())
            self.assertTrue(marker.exists())

    def test_clean_older_than_hours_removes_only_old_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            old = "c" * 32
            fresh = "d" * 32
            old_path = self.make_run(target, old, age_hours=12)
            fresh_path = self.make_run(target, fresh, age_hours=1)

            removed, errors = clean_runs(target, older_than_hours=6)

            self.assertEqual(errors, [])
            self.assertEqual(removed, [old])
            self.assertFalse(old_path.exists())
            self.assertTrue(fresh_path.exists())

    def test_clean_all_removes_only_managed_run_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))
            first = "e" * 32
            second = "f" * 32
            self.make_run(target, first)
            self.make_run(target, second)
            root = target / ".DesignForge" / "render-staging"
            unmanaged = root / "preserve-me"
            unmanaged.mkdir()

            removed, errors = clean_runs(target, all_runs=True)

            self.assertEqual(errors, [])
            self.assertEqual(set(removed), {first, second})
            self.assertTrue(unmanaged.exists())

    def test_clean_requires_exactly_one_selector(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))

            removed, errors = clean_runs(target)
            self.assertEqual(removed, [])
            self.assertTrue(errors)

            removed, errors = clean_runs(target, run_id="a" * 32, all_runs=True)
            self.assertEqual(removed, [])
            self.assertTrue(errors)

    def test_invalid_run_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = self.make_target(Path(tmp))

            removed, errors = clean_runs(target, run_id="../outside")

            self.assertEqual(removed, [])
            self.assertTrue(any("32-character lowercase hex" in error for error in errors))

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink not supported")
    def test_symlink_run_is_ignored_and_never_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = self.make_target(root)
            outside = root / "outside"
            outside.mkdir()
            marker = outside / "marker.txt"
            marker.write_text("safe", encoding="utf-8")
            staging = target / ".DesignForge" / "render-staging"
            staging.mkdir(parents=True)
            run_id = "1" * 32
            try:
                os.symlink(outside, staging / run_id, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")

            runs, errors = list_runs(target)
            self.assertEqual(errors, [])
            self.assertEqual(runs, [])

            removed, errors = clean_runs(target, run_id=run_id)
            self.assertEqual(removed, [])
            self.assertTrue(errors)
            self.assertEqual(marker.read_text(encoding="utf-8"), "safe")


if __name__ == "__main__":
    unittest.main()
