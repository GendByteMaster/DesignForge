from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "designforge" / "scripts" / "install_skill.py"


def run_installer(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(INSTALLER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class DesignForgeInstallerTests(unittest.TestCase):
    def test_installs_for_codex_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            result = run_installer("codex", str(project))
            self.assertEqual(result.returncode, 0, result.stderr)

            skill = project / ".agents" / "skills" / "designforge"
            self.assertTrue((skill / "SKILL.md").is_file())
            self.assertTrue((skill / "agents" / "openai.yaml").is_file())
            self.assertTrue((skill / "scripts" / "designforge.py").is_file())
            self.assertFalse(any(path.name == "__pycache__" for path in skill.rglob("__pycache__")))

    def test_installs_for_claude_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            result = run_installer("claude", str(project))
            self.assertEqual(result.returncode, 0, result.stderr)

            skill = project / ".claude" / "skills" / "designforge"
            self.assertTrue((skill / "SKILL.md").is_file())
            self.assertTrue((skill / "workflows" / "BUILD.md").is_file())

    def test_existing_install_is_preserved_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.assertEqual(run_installer("codex", str(project)).returncode, 0)

            skill = project / ".agents" / "skills" / "designforge"
            marker = skill / "custom.txt"
            marker.write_text("keep me", encoding="utf-8")

            second = run_installer("codex", str(project))
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("already exists", second.stderr)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep me")

    def test_force_replaces_existing_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.assertEqual(run_installer("claude", str(project)).returncode, 0)

            skill = project / ".claude" / "skills" / "designforge"
            marker = skill / "stale.txt"
            marker.write_text("stale", encoding="utf-8")

            result = run_installer("claude", str(project), "--force")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(marker.exists())
            self.assertTrue((skill / "SKILL.md").is_file())

    def test_missing_project_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing"
            result = run_installer("codex", str(missing))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("does not exist", result.stderr)


if __name__ == "__main__":
    unittest.main()
