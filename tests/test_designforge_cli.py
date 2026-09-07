from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "designforge" / "scripts" / "designforge.py"
FIXTURE = ROOT / "tests" / "fixtures" / "sample-web-app"


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

    def test_phase_rejects_non_positive_number(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(run_cli("init", str(target), "--mode", "refactor").returncode, 0)
            result = run_cli("phase", "Navigation", "--target", str(target), "--number", "0")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("greater than zero", result.stderr)

    def test_transition_allows_normal_lifecycle_step(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(run_cli("init", str(target), "--mode", "refactor").returncode, 0)

            result = run_cli("transition", "map", "--target", str(target))
            self.assertEqual(result.returncode, 0, result.stderr)
            state = (target / ".DesignForge" / "STATE.md").read_text(encoding="utf-8")
            self.assertIn("Current workflow: map", state)
            self.assertIn("Status: ready", state)

    def test_transition_rejects_invalid_jump_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(run_cli("init", str(target), "--mode", "refactor").returncode, 0)

            result = run_cli("transition", "guard", "--target", str(target))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not allowed", result.stderr)

            forced = run_cli("transition", "guard", "--target", str(target), "--force")
            self.assertEqual(forced.returncode, 0, forced.stderr)

    def test_state_remains_low_level_recovery_tool(self) -> None:
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
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            state = (target / ".DesignForge" / "STATE.md").read_text(encoding="utf-8")
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

    def test_validate_detects_mode_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(run_cli("init", str(target), "--mode", "refactor").returncode, 0)
            state_path = target / ".DesignForge" / "STATE.md"
            state = state_path.read_text(encoding="utf-8").replace("Mode: refactor", "Mode: reimagine")
            state_path.write_text(state, encoding="utf-8")

            result = run_cli("validate", "--target", str(target))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("does not match", result.stderr)

    def test_validate_detects_missing_active_phase_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.assertEqual(run_cli("init", str(target), "--mode", "refactor").returncode, 0)
            self.assertEqual(
                run_cli("state", "--target", str(target), "--phase", "03-missing-phase").returncode,
                0,
            )

            result = run_cli("validate", "--target", str(target))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing phase directory", result.stderr)

    def test_phase_requires_initialized_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_cli("phase", "Navigation", "--target", tmp)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("run init first", result.stderr)

    def test_end_to_end_representative_project_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "sample-web-app"
            shutil.copytree(FIXTURE, target)

            steps = (
                ("init", str(target), "--mode", "reimagine"),
                ("transition", "map", "--target", str(target)),
                ("transition", "direct", "--target", str(target)),
                ("transition", "systemize", "--target", str(target)),
                ("phase", "Main Workspace", "--target", str(target)),
                ("transition", "build", "--target", str(target), "--status", "in-progress"),
                ("transition", "review", "--target", str(target), "--status", "review"),
                ("transition", "guard", "--target", str(target), "--status", "complete"),
                ("validate", "--target", str(target)),
            )

            for step in steps:
                result = run_cli(*step)
                self.assertEqual(result.returncode, 0, f"{step}: {result.stderr}")

            state = (target / ".DesignForge" / "STATE.md").read_text(encoding="utf-8")
            self.assertIn("Current phase: 01-main-workspace", state)
            self.assertIn("Current workflow: guard", state)
            self.assertIn("Mode: reimagine", state)
            self.assertIn("Status: complete", state)


if __name__ == "__main__":
    unittest.main()
