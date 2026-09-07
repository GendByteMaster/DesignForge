from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "designforge" / "scripts" / "designforge.py"
VALIDATOR = ROOT / "designforge" / "scripts" / "validate_mapping_artifacts.py"
STACK_TEMPLATE = ROOT / "designforge" / "assets" / "codebase" / "STACK.md"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class MappingArtifactValidationTests(unittest.TestCase):
    def init_target(self, target: Path) -> None:
        result = run(str(CLI), "init", str(target), "--mode", "refactor")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_empty_mapping_requires_explicit_allow_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)

            invalid = run(str(VALIDATOR), str(target))
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("no interpreted mapping artifacts", invalid.stderr)

            allowed = run(str(VALIDATOR), str(target), "--allow-empty")
            self.assertEqual(allowed.returncode, 0, allowed.stderr)

    def test_template_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            codebase = target / ".DesignForge" / "codebase"
            codebase.mkdir(parents=True)
            (codebase / "STACK.md").write_text(STACK_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")

            result = run(str(VALIDATOR), str(target))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_verified_finding_requires_repository_path_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            codebase = target / ".DesignForge" / "codebase"
            codebase.mkdir(parents=True)
            text = STACK_TEMPLATE.read_text(encoding="utf-8").replace(
                "## Verified findings\n\n- None yet.",
                "## Verified findings\n\n- The UI uses React.",
            )
            (codebase / "STACK.md").write_text(text, encoding="utf-8")

            result = run(str(VALIDATOR), str(target))
            self.assertEqual(result.returncode, 1)
            self.assertIn("repository-relative path", result.stderr)

    def test_verified_finding_with_evidence_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            codebase = target / ".DesignForge" / "codebase"
            codebase.mkdir(parents=True)
            text = STACK_TEMPLATE.read_text(encoding="utf-8").replace(
                "## Verified findings\n\n- None yet.",
                "## Verified findings\n\n- The UI uses React.",
            ).replace(
                "## Evidence index\n\n- None yet.",
                "## Evidence index\n\n- `desktop/package.json` — declares React dependencies.",
            )
            (codebase / "STACK.md").write_text(text, encoding="utf-8")

            result = run(str(VALIDATOR), str(target))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_required_section_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.init_target(target)
            codebase = target / ".DesignForge" / "codebase"
            codebase.mkdir(parents=True)
            text = STACK_TEMPLATE.read_text(encoding="utf-8").replace("## Unknowns\n\n- None yet.\n\n", "")
            (codebase / "STACK.md").write_text(text, encoding="utf-8")

            result = run(str(VALIDATOR), str(target))
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing ## Unknowns", result.stderr)


if __name__ == "__main__":
    unittest.main()
