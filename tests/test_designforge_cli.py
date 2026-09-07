from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "designforge" / "scripts" / "designforge.py"


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class DesignForgeCliTests(unittest.TestCase):
    def test_init_creates_minimal_workspace_and_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            result = run_cli("init", str(target), "--mode", "reimagine")
            self.assertEqual(result.returncode, 0, result.stderr)

            workspace = target / ".DesignForge"
            self.assertTrue((workspace / "PROJECT.md").exists())
            self.assertTrue((workspace / "STATE.md").exists())
            self.assertFalse((workspace / "ROADMAP.md").exists())

            project = (workspace / "PROJECT.md").read_text(encoding="utf-8")
            state = (workspace / "STATE.md").read_text(encoding="utf-8")
            self.assertIn("## Redesign mode\n\nreimagine", project)
            self.assertIn("Mode: reimagine", state)
            self.assertIn("Current workflow: init", state)

    def test_init_is_idempotent_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            first = run_cli("init", str(target), "--mode", "refactor")
            self.assertEqual(first.returncode, 0, first.stderr)

            project_path = target / ".DesignForge" / "PROJECT.md"
            project_path.write_text("# Project\n\ncustom user content\n", encoding="utf-8")

            second = run_cli("init", str(target), "--mode", "reimagine")
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(project_path.read_text(encoding="utf-8"), "# Project\n\ncustom user content\n")
            self.assertIn("preserved", second.stdout)

    def test_force_overwrites_managed_root_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(run_cli("init", str(target), "--mode", "refactor").returncode, 0)

            project_path = target / ".DesignForge" / "PROJECT.md"
            project_path.write_text("custom", encoding="utf-8")

            result = run_cli("init", str(target), "--mode", "conservative", "--force")
            self.assertEqual(result.returncode, 0, result.stderr)
            project = project_path.read_text(encoding="utf-8")
            self.assertIn("## Redesign mode\n\nconservative", project)
            self.assertNotEqual(project, "custom")

    def test_phase_creates_numbered_artifacts_and_updates_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(run_cli("init", str(target), "--mode", "refactor").returncode, 0)

            result = run_cli("phase", "Main Workspace", "--target", str(target))
            self.assertEqual(result.returncode, 0, result.stderr)

            phase = target / ".DesignForge" / "phases" / "01-main-workspace"
            self.assertTrue(phase.is_dir())
            for filename in (
                "CONTEXT.md",
                "RESEARCH.md",
                "PLAN.md",
                "DESIGN.md",
                "IMPLEMENTATION.md",
                "REVIEW.md",
                "RESULT.md",
            ):
                self.assertTrue((phase / filename).exists(), filename)

            state = (target / ".DesignForge" / "STATE.md").read_text(encoding="utf-8")
            self.assertIn("Current phase: 01-main-workspace", state)
            self.assertIn("Current workflow: plan", state)
            self.assertIn("Status: ready", state)

    def test_state_updates_known_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(run_cli("init", str(target), "--mode", "refactor").returncode, 0)

            result = run_cli(
                "state",
                "--target",
                str(target),
                "--workflow",
                "build",
                "--status",
                "in-progress",
                "--phase",
                "02-navigation",
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            state = (target / ".DesignForge" / "STATE.md").read_text(encoding="utf-8")
            self.assertIn("Current phase: 02-navigation", state)
            self.assertIn("Current workflow: build", state)
            self.assertIn("Status: in-progress", state)

    def test_validate_passes_for_skill_and_initialized_workspace(self) -> None:
        skill = run_cli("validate")
        self.assertEqual(skill.returncode, 0, skill.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(run_cli("init", str(target), "--mode", "conservative").returncode, 0)
            workspace = run_cli("validate", "--target", str(target))
            self.assertEqual(workspace.returncode, 0, workspace.stderr)

    def test_phase_requires_initialized_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli("phase", "Navigation", "--target", tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("run init first", result.stderr)


if __name__ == "__main__":
    unittest.main()
