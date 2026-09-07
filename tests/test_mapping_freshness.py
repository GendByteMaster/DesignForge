from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "designforge" / "scripts" / "designforge.py"
FRESHNESS = ROOT / "designforge" / "scripts" / "mapping_freshness.py"
STACK_TEMPLATE = ROOT / "designforge" / "assets" / "codebase" / "STACK.md"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def git(target: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(target), *args],
        text=True,
        capture_output=True,
        check=False,
    )


class MappingFreshnessTests(unittest.TestCase):
    def init_target(self, target: Path) -> None:
        result = run(str(CLI), "init", str(target), "--mode", "refactor")
        self.assertEqual(result.returncode, 0, result.stderr)

    def init_git_repo(self, target: Path) -> None:
        self.assertEqual(git(target, "init").returncode, 0)
        self.assertEqual(git(target, "config", "user.email", "designforge@example.test").returncode, 0)
        self.assertEqual(git(target, "config", "user.name", "DesignForge Tests").returncode, 0)

    def commit(self, target: Path, message: str, *paths: str) -> None:
        add = git(target, "add", *paths)
        self.assertEqual(add.returncode, 0, add.stderr)
        commit = git(target, "commit", "-m", message)
        self.assertEqual(commit.returncode, 0, commit.stderr)

    def prepare_mapping(self, target: Path) -> Path:
        self.init_git_repo(target)
        source = target / "src" / "App.tsx"
        source.parent.mkdir(parents=True)
        source.write_text("export default function App() { return <main>Hello</main>; }\n", encoding="utf-8")
        (target / "README.md").write_text("# Fixture\n", encoding="utf-8")
        self.commit(target, "initial fixture", "src/App.tsx", "README.md")

        self.init_target(target)
        codebase = target / ".DesignForge" / "codebase"
        codebase.mkdir(parents=True)
        text = STACK_TEMPLATE.read_text(encoding="utf-8").replace(
            "## Verified findings\n\n- None yet.",
            "## Verified findings\n\n- The fixture has a React-style application entry.",
        ).replace(
            "## Evidence index\n\n- None yet.",
            "## Evidence index\n\n- `src/App.tsx` — application source used by this finding.",
        )
        artifact = codebase / "STACK.md"
        artifact.write_text(text, encoding="utf-8")
        return artifact

    def stamp(self, target: Path) -> subprocess.CompletedProcess[str]:
        return run(str(FRESHNESS), "stamp", str(target))

    def check(self, target: Path) -> subprocess.CompletedProcess[str]:
        return run(str(FRESHNESS), "check", str(target))

    def test_stamp_then_check_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.prepare_mapping(target)

            stamped = self.stamp(target)
            self.assertEqual(stamped.returncode, 0, stamped.stderr)
            state = target / ".DesignForge" / "codebase" / "MAP_STATE.md"
            self.assertTrue(state.is_file())
            text = state.read_text(encoding="utf-8")
            self.assertIn("## Source digests", text)
            self.assertIn("## Mapping artifact digests", text)
            self.assertIn("`src/App.tsx`", text)
            self.assertIn("`.DesignForge/codebase/STACK.md`", text)

            checked = self.check(target)
            self.assertEqual(checked.returncode, 0, checked.stderr)

    def test_cited_source_change_marks_mapping_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.prepare_mapping(target)
            self.assertEqual(self.stamp(target).returncode, 0)

            source = target / "src" / "App.tsx"
            source.write_text("export default function App() { return <main>Changed</main>; }\n", encoding="utf-8")

            checked = self.check(target)
            self.assertEqual(checked.returncode, 1)
            self.assertIn("source changed: src/App.tsx", checked.stderr)

    def test_mapping_artifact_change_marks_mapping_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            artifact = self.prepare_mapping(target)
            self.assertEqual(self.stamp(target).returncode, 0)

            artifact.write_text(artifact.read_text(encoding="utf-8") + "\nAdditional interpretation.\n", encoding="utf-8")

            checked = self.check(target)
            self.assertEqual(checked.returncode, 1)
            self.assertIn("mapping artifact changed after stamp", checked.stderr)
            self.assertIn(".DesignForge/codebase/STACK.md", checked.stderr)

    def test_new_ui_relevant_committed_file_marks_mapping_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.prepare_mapping(target)
            self.assertEqual(self.stamp(target).returncode, 0)

            panel = target / "src" / "Panel.tsx"
            panel.write_text("export function Panel() { return <aside />; }\n", encoding="utf-8")
            self.commit(target, "add panel", "src/Panel.tsx")

            checked = self.check(target)
            self.assertEqual(checked.returncode, 1)
            self.assertIn("UI-relevant committed change since mapping: src/Panel.tsx", checked.stderr)

    def test_new_ui_relevant_worktree_file_marks_mapping_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.prepare_mapping(target)
            self.assertEqual(self.stamp(target).returncode, 0)

            panel = target / "src" / "Panel.tsx"
            panel.write_text("export function Panel() { return <aside />; }\n", encoding="utf-8")

            checked = self.check(target)
            self.assertEqual(checked.returncode, 1)
            self.assertIn("new UI-relevant working-tree change: src/Panel.tsx", checked.stderr)

    def test_non_ui_committed_drift_does_not_invalidate_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            self.prepare_mapping(target)
            self.assertEqual(self.stamp(target).returncode, 0)

            readme = target / "README.md"
            readme.write_text("# Fixture\n\nDocumentation only.\n", encoding="utf-8")
            self.commit(target, "docs only", "README.md")

            checked = self.check(target)
            self.assertEqual(checked.returncode, 0, checked.stderr)

    def test_freshness_works_without_git_using_content_digests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            source = target / "src" / "App.tsx"
            source.parent.mkdir(parents=True)
            source.write_text("export default function App() { return <main />; }\n", encoding="utf-8")
            self.init_target(target)
            codebase = target / ".DesignForge" / "codebase"
            codebase.mkdir(parents=True)
            text = STACK_TEMPLATE.read_text(encoding="utf-8").replace(
                "## Verified findings\n\n- None yet.",
                "## Verified findings\n\n- Application source exists.",
            ).replace(
                "## Evidence index\n\n- None yet.",
                "## Evidence index\n\n- `src/App.tsx` — source evidence.",
            )
            (codebase / "STACK.md").write_text(text, encoding="utf-8")

            stamped = self.stamp(target)
            self.assertEqual(stamped.returncode, 0, stamped.stderr)
            checked = self.check(target)
            self.assertEqual(checked.returncode, 0, checked.stderr)

            source.write_text("export default function App() { return <main>Changed</main>; }\n", encoding="utf-8")
            stale = self.check(target)
            self.assertEqual(stale.returncode, 1)
            self.assertIn("source changed: src/App.tsx", stale.stderr)


if __name__ == "__main__":
    unittest.main()
