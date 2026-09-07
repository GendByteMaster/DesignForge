from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "designforge" / "scripts" / "designforge.py"
VISUAL_QA = ROOT / "designforge" / "scripts" / "visual_qa.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class VisualQATests(unittest.TestCase):
    def init_target(self, target: Path) -> None:
        result = run(str(CLI), "init", str(target), "--mode", "refactor")
        self.assertEqual(result.returncode, 0, result.stderr)

    def init_visual(self, target: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return run(str(VISUAL_QA), "init", str(target), *extra)

    def validate_visual(self, target: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return run(str(VISUAL_QA), "validate", str(target), *extra)

    def test_init_requires_designforge_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            result = self.init_visual(target)
            self.assertEqual(result.returncode, 1)
            self.assertIn("STATE.md not found", result.stderr)

    def test_global_init_creates_visual_qa_and_evidence_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)

            result = self.init_visual(target)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".DesignForge" / "reviews" / "VISUAL_QA.md").is_file())
            self.assertTrue((target / ".DesignForge" / "reviews" / "visual-evidence").is_dir())

    def test_public_cli_exposes_visual_init_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)

            initialized = run(str(CLI), "visual", "init", str(target))
            self.assertEqual(initialized.returncode, 0, initialized.stderr)
            self.assertIn("Visual QA artifact", initialized.stdout)

            validated = run(str(CLI), "visual", "validate", str(target))
            self.assertEqual(validated.returncode, 0, validated.stderr)
            self.assertIn("visual QA validation passed", validated.stdout)

    def test_phase_init_targets_existing_phase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            phase = run(str(CLI), "phase", "Main Workspace", "--target", str(target))
            self.assertEqual(phase.returncode, 0, phase.stderr)

            result = self.init_visual(target, "--phase", "01-main-workspace")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".DesignForge" / "phases" / "01-main-workspace" / "VISUAL_QA.md").is_file())
            self.assertTrue((target / ".DesignForge" / "phases" / "01-main-workspace" / "visual-evidence").is_dir())

    def test_phase_init_rejects_missing_phase(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            result = self.init_visual(target, "--phase", "99-missing")
            self.assertEqual(result.returncode, 1)
            self.assertIn("phase directory not found", result.stderr)

    def test_pending_template_is_structurally_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            self.assertEqual(self.init_visual(target).returncode, 0)

            result = self.validate_visual(target)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_pass_requires_inspected_render_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            self.assertEqual(self.init_visual(target).returncode, 0)
            review = target / ".DesignForge" / "reviews" / "VISUAL_QA.md"
            review.write_text(review.read_text(encoding="utf-8").replace("Status: pending", "Status: pass"), encoding="utf-8")

            result = self.validate_visual(target)
            self.assertEqual(result.returncode, 1)
            self.assertIn("requires at least one inspected render artifact", result.stderr)

    def test_checked_capture_requires_existing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            self.assertEqual(self.init_visual(target).returncode, 0)
            review = target / ".DesignForge" / "reviews" / "VISUAL_QA.md"
            text = review.read_text(encoding="utf-8")
            text = text.replace(
                "- [ ] Surface: <!-- name --> | State: <!-- default, hover, focus, loading, error, empty, etc. --> | Viewport: <!-- width x height, device, window size, or native form factor --> | Evidence: `<!-- project-relative .png/.jpg/.jpeg/.webp/.gif/.mp4/.webm path -->`",
                "- [x] Surface: Dashboard | State: default | Viewport: 1440x900 | Evidence: `.DesignForge/reviews/visual-evidence/dashboard.png`",
            ).replace("Status: pending", "Status: pass")
            review.write_text(text, encoding="utf-8")

            result = self.validate_visual(target)
            self.assertEqual(result.returncode, 1)
            self.assertIn("evidence file not found", result.stderr)

    def test_checked_capture_with_nonempty_render_evidence_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            self.assertEqual(self.init_visual(target).returncode, 0)
            evidence = target / ".DesignForge" / "reviews" / "visual-evidence" / "dashboard.png"
            evidence.write_bytes(b"render-evidence")

            review = target / ".DesignForge" / "reviews" / "VISUAL_QA.md"
            text = review.read_text(encoding="utf-8")
            text = text.replace(
                "- [ ] Surface: <!-- name --> | State: <!-- default, hover, focus, loading, error, empty, etc. --> | Viewport: <!-- width x height, device, window size, or native form factor --> | Evidence: `<!-- project-relative .png/.jpg/.jpeg/.webp/.gif/.mp4/.webm path -->`",
                "- [x] Surface: Dashboard | State: default | Viewport: 1440x900 | Evidence: `.DesignForge/reviews/visual-evidence/dashboard.png`",
            ).replace("Status: pending", "Status: pass")
            review.write_text(text, encoding="utf-8")

            result = self.validate_visual(target)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_checked_capture_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            self.assertEqual(self.init_visual(target).returncode, 0)
            review = target / ".DesignForge" / "reviews" / "VISUAL_QA.md"
            text = review.read_text(encoding="utf-8")
            text = text.replace(
                "- [ ] Surface: <!-- name --> | State: <!-- default, hover, focus, loading, error, empty, etc. --> | Viewport: <!-- width x height, device, window size, or native form factor --> | Evidence: `<!-- project-relative .png/.jpg/.jpeg/.webp/.gif/.mp4/.webm path -->`",
                "- [x] Surface: Dashboard | State: default | Viewport: 1440x900 | Evidence: `../outside.png`",
            ).replace("Status: pending", "Status: pass")
            review.write_text(text, encoding="utf-8")

            result = self.validate_visual(target)
            self.assertEqual(result.returncode, 1)
            self.assertIn("must be project-relative", result.stderr)

    def test_checked_capture_rejects_unsupported_format(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            self.assertEqual(self.init_visual(target).returncode, 0)
            evidence = target / ".DesignForge" / "reviews" / "visual-evidence" / "dashboard.txt"
            evidence.write_text("not render evidence", encoding="utf-8")
            review = target / ".DesignForge" / "reviews" / "VISUAL_QA.md"
            text = review.read_text(encoding="utf-8")
            text = text.replace(
                "- [ ] Surface: <!-- name --> | State: <!-- default, hover, focus, loading, error, empty, etc. --> | Viewport: <!-- width x height, device, window size, or native form factor --> | Evidence: `<!-- project-relative .png/.jpg/.jpeg/.webp/.gif/.mp4/.webm path -->`",
                "- [x] Surface: Dashboard | State: default | Viewport: 1440x900 | Evidence: `.DesignForge/reviews/visual-evidence/dashboard.txt`",
            ).replace("Status: pending", "Status: pass")
            review.write_text(text, encoding="utf-8")

            result = self.validate_visual(target)
            self.assertEqual(result.returncode, 1)
            self.assertIn("unsupported render format", result.stderr)


if __name__ == "__main__":
    unittest.main()
