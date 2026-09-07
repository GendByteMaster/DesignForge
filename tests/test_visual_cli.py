from __future__ import annotations

import subprocess
import sys
import tempfile
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


class VisualPublicCLITests(unittest.TestCase):
    def init_target(self, target: Path) -> None:
        result = run("init", str(target), "--mode", "refactor")
        self.assertEqual(result.returncode, 0, result.stderr)

    def write_png(self, path: Path) -> None:
        path.write_bytes(b"\x89PNG\r\n\x1a\nrender-evidence")

    def test_public_cli_capture_registers_managed_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self.init_target(target)
            source = Path(tmp) / "shot.png"
            self.write_png(source)

            captured = run(
                "visual",
                "capture",
                str(source),
                str(target),
                "--surface",
                "Dashboard",
                "--state",
                "default",
                "--viewport",
                "1440x900",
            )
            self.assertEqual(captured.returncode, 0, captured.stderr)
            self.assertIn("Visual capture registered", captured.stdout)

            evidence = target / ".DesignForge" / "reviews" / "visual-evidence" / "dashboard-default.png"
            self.assertTrue(evidence.is_file())

            validated = run("visual", "validate", str(target))
            self.assertEqual(validated.returncode, 0, validated.stderr)

    def test_public_cli_conclusive_verdict_requires_capture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self.init_target(target)

            initialized = run("visual", "init", str(target))
            self.assertEqual(initialized.returncode, 0, initialized.stderr)

            verdict = run("visual", "verdict", "pass", str(target))
            self.assertEqual(verdict.returncode, 1)
            self.assertIn("requires at least one inspected render artifact", verdict.stderr)

            review = target / ".DesignForge" / "reviews" / "VISUAL_QA.md"
            self.assertIn("Status: pending", review.read_text(encoding="utf-8"))

    def test_public_cli_capture_then_pass_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self.init_target(target)
            source = Path(tmp) / "shot.png"
            self.write_png(source)

            captured = run(
                "visual",
                "capture",
                str(source),
                str(target),
                "--surface",
                "Dashboard",
                "--state",
                "focus",
                "--viewport",
                "1280x800",
            )
            self.assertEqual(captured.returncode, 0, captured.stderr)

            verdict = run("visual", "verdict", "pass", str(target))
            self.assertEqual(verdict.returncode, 0, verdict.stderr)
            self.assertIn("Visual QA verdict: pass", verdict.stdout)

            validated = run("visual", "validate", str(target))
            self.assertEqual(validated.returncode, 0, validated.stderr)

    def test_public_cli_phase_capture_uses_phase_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "project"
            target.mkdir()
            self.init_target(target)
            phase = run("phase", "Main Workspace", "--target", str(target))
            self.assertEqual(phase.returncode, 0, phase.stderr)
            source = Path(tmp) / "shot.png"
            self.write_png(source)

            captured = run(
                "visual",
                "capture",
                str(source),
                str(target),
                "--surface",
                "Main Workspace",
                "--state",
                "default",
                "--viewport",
                "desktop",
                "--phase",
                "01-main-workspace",
            )
            self.assertEqual(captured.returncode, 0, captured.stderr)

            evidence = (
                target
                / ".DesignForge"
                / "phases"
                / "01-main-workspace"
                / "visual-evidence"
                / "main-workspace-default.png"
            )
            self.assertTrue(evidence.is_file())

            validated = run(
                "visual",
                "validate",
                str(target),
                "--phase",
                "01-main-workspace",
            )
            self.assertEqual(validated.returncode, 0, validated.stderr)


if __name__ == "__main__":
    unittest.main()
