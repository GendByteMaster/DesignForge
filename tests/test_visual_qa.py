from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "designforge" / "scripts" / "designforge.py"
VISUAL_QA = ROOT / "designforge" / "scripts" / "visual_qa.py"
CAPTURE_TEMPLATE = "- [ ] Surface: <!-- name --> | State: <!-- default, hover, focus, loading, error, empty, etc. --> | Viewport: <!-- width x height, device, window size, or native form factor --> | Evidence: `<!-- project-relative .png/.jpg/.jpeg/.webp/.gif/.mp4/.webm path -->`"


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

    def mark_capture(self, target: Path, evidence: str, status: str = "pass") -> Path:
        review = target / ".DesignForge" / "reviews" / "VISUAL_QA.md"
        text = review.read_text(encoding="utf-8")
        text = text.replace(
            CAPTURE_TEMPLATE,
            f"- [x] Surface: Dashboard | State: default | Viewport: 1440x900 | Evidence: `{evidence}`",
        ).replace("Status: pending", f"Status: {status}")
        review.write_text(text, encoding="utf-8")
        return review

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
            self.mark_capture(target, ".DesignForge/reviews/visual-evidence/dashboard.png")

            result = self.validate_visual(target)
            self.assertEqual(result.returncode, 1)
            self.assertIn("evidence file not found", result.stderr)

    def test_checked_capture_with_png_signature_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            self.assertEqual(self.init_visual(target).returncode, 0)
            evidence = target / ".DesignForge" / "reviews" / "visual-evidence" / "dashboard.png"
            evidence.write_bytes(b"\x89PNG\r\n\x1a\nrender-evidence")
            self.mark_capture(target, ".DesignForge/reviews/visual-evidence/dashboard.png")

            result = self.validate_visual(target)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_checked_capture_rejects_fake_png_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            self.assertEqual(self.init_visual(target).returncode, 0)
            evidence = target / ".DesignForge" / "reviews" / "visual-evidence" / "dashboard.png"
            evidence.write_bytes(b"render-evidence")
            self.mark_capture(target, ".DesignForge/reviews/visual-evidence/dashboard.png")

            result = self.validate_visual(target)
            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid render signature", result.stderr)

    def test_supported_render_signatures_are_accepted(self) -> None:
        cases = {
            "capture.png": b"\x89PNG\r\n\x1a\nrest",
            "capture.jpg": b"\xff\xd8\xff\xe0rest",
            "capture.jpeg": b"\xff\xd8\xff\xe1rest",
            "capture.gif": b"GIF89arest",
            "capture.webp": b"RIFF\x08\x00\x00\x00WEBPrest",
            "capture.mp4": b"\x00\x00\x00\x18ftypisomrest",
            "capture.webm": b"\x1a\x45\xdf\xa3rest",
        }

        for filename, payload in cases.items():
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp)
                self.init_target(target)
                self.assertEqual(self.init_visual(target).returncode, 0)
                relative = f".DesignForge/reviews/visual-evidence/{filename}"
                evidence = target / relative
                evidence.write_bytes(payload)
                self.mark_capture(target, relative)

                result = self.validate_visual(target)
                self.assertEqual(result.returncode, 0, f"{filename}: {result.stderr}")

    def test_checked_capture_rejects_evidence_outside_managed_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            self.assertEqual(self.init_visual(target).returncode, 0)
            evidence = target / "dashboard.png"
            evidence.write_bytes(b"\x89PNG\r\n\x1a\nrender-evidence")
            self.mark_capture(target, "dashboard.png")

            result = self.validate_visual(target)
            self.assertEqual(result.returncode, 1)
            self.assertIn("must live under .DesignForge/reviews/visual-evidence", result.stderr)

    def test_checked_capture_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            self.assertEqual(self.init_visual(target).returncode, 0)
            self.mark_capture(target, "../outside.png")

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
            self.mark_capture(target, ".DesignForge/reviews/visual-evidence/dashboard.txt")

            result = self.validate_visual(target)
            self.assertEqual(result.returncode, 1)
            self.assertIn("unsupported render format", result.stderr)


if __name__ == "__main__":
    unittest.main()
