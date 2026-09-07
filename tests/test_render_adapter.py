from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "designforge" / "scripts" / "designforge.py"
RENDER_ADAPTER = ROOT / "designforge" / "scripts" / "render_adapter.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class RenderAdapterTests(unittest.TestCase):
    def init_target(self, target: Path) -> None:
        result = run(str(CLI), "init", str(target), "--mode", "refactor")
        self.assertEqual(result.returncode, 0, result.stderr)

    def write_adapter(self, directory: Path, body: str) -> Path:
        adapter = directory / "adapter.py"
        adapter.write_text(textwrap.dedent(body), encoding="utf-8")
        return adapter

    def render(self, target: Path, adapter: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return run(
            str(RENDER_ADAPTER),
            str(target),
            "--surface",
            "Dashboard",
            "--state",
            "default",
            "--viewport",
            "1440x900",
            *extra,
            "--adapter",
            sys.executable,
            str(adapter),
        )

    def test_adapter_produces_staging_artifact_without_visual_qa_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            target.mkdir()
            self.init_target(target)
            adapter = self.write_adapter(
                root,
                """
                import json
                import os
                from pathlib import Path

                output = Path(os.environ["DESIGNFORGE_OUTPUT_DIR"]) / "render.png"
                output.write_bytes(b"\\x89PNG\\r\\n\\x1a\\nrender")
                print(json.dumps({"protocol": os.environ["DESIGNFORGE_RENDER_PROTOCOL"], "artifact": "render.png"}))
                """,
            )

            result = self.render(target, adapter)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Render artifact:", result.stdout)
            self.assertIn("Inspect this artifact", result.stdout)
            self.assertFalse((target / ".DesignForge" / "reviews" / "VISUAL_QA.md").exists())

            staging = target / ".DesignForge" / "render-staging"
            artifacts = list(staging.glob("*/render.png"))
            self.assertEqual(len(artifacts), 1)
            self.assertTrue(artifacts[0].is_file())

    def test_adapter_receives_normalized_render_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            target.mkdir()
            self.init_target(target)
            adapter = self.write_adapter(
                root,
                """
                import json
                import os
                from pathlib import Path

                output_dir = Path(os.environ["DESIGNFORGE_OUTPUT_DIR"])
                output = output_dir / "render.png"
                output.write_bytes(b"\\x89PNG\\r\\n\\x1a\\nrender")
                metadata = {
                    "surface": os.environ["DESIGNFORGE_SURFACE"],
                    "state": os.environ["DESIGNFORGE_STATE"],
                    "viewport": os.environ["DESIGNFORGE_VIEWPORT"],
                    "phase": os.environ["DESIGNFORGE_PHASE"],
                }
                (output_dir / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
                print(json.dumps({"protocol": os.environ["DESIGNFORGE_RENDER_PROTOCOL"], "artifact": "render.png"}))
                """,
            )

            result = run(
                str(RENDER_ADAPTER),
                str(target),
                "--surface",
                "  Dashboard  ",
                "--state",
                " default ",
                "--viewport",
                " 1440x900 ",
                "--adapter",
                sys.executable,
                str(adapter),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            metadata_files = list((target / ".DesignForge" / "render-staging").glob("*/metadata.json"))
            self.assertEqual(len(metadata_files), 1)
            metadata = json.loads(metadata_files[0].read_text(encoding="utf-8"))
            self.assertEqual(metadata, {"surface": "Dashboard", "state": "default", "viewport": "1440x900", "phase": ""})

    def test_adapter_phase_scope_requires_existing_phase_and_passes_phase_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            target.mkdir()
            self.init_target(target)
            adapter = self.write_adapter(
                root,
                """
                import json
                import os
                from pathlib import Path

                output_dir = Path(os.environ["DESIGNFORGE_OUTPUT_DIR"])
                output = output_dir / "render.png"
                output.write_bytes(b"\\x89PNG\\r\\n\\x1a\\nrender")
                (output_dir / "phase.txt").write_text(os.environ["DESIGNFORGE_PHASE"], encoding="utf-8")
                print(json.dumps({"protocol": os.environ["DESIGNFORGE_RENDER_PROTOCOL"], "artifact": "render.png"}))
                """,
            )

            missing = self.render(target, adapter, "--phase", "01-main-workspace")
            self.assertEqual(missing.returncode, 1)
            self.assertIn("phase directory not found", missing.stderr)

            phase = run(str(CLI), "phase", "Main Workspace", "--target", str(target))
            self.assertEqual(phase.returncode, 0, phase.stderr)
            rendered = self.render(target, adapter, "--phase", "01-main-workspace")
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            phase_files = list((target / ".DesignForge" / "render-staging").glob("*/phase.txt"))
            self.assertEqual(len(phase_files), 1)
            self.assertEqual(phase_files[0].read_text(encoding="utf-8"), "01-main-workspace")

    def test_adapter_rejects_artifact_escape_from_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            target.mkdir()
            self.init_target(target)
            adapter = self.write_adapter(
                root,
                """
                import json
                import os
                from pathlib import Path

                output_dir = Path(os.environ["DESIGNFORGE_OUTPUT_DIR"])
                outside = output_dir.parent / "outside.png"
                outside.write_bytes(b"\\x89PNG\\r\\n\\x1a\\nrender")
                print(json.dumps({"protocol": os.environ["DESIGNFORGE_RENDER_PROTOCOL"], "artifact": "../outside.png"}))
                """,
            )

            result = self.render(target, adapter)
            self.assertEqual(result.returncode, 1)
            self.assertIn("inside DESIGNFORGE_OUTPUT_DIR", result.stderr)

    def test_adapter_rejects_invalid_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            target.mkdir()
            self.init_target(target)
            adapter = self.write_adapter(
                root,
                """
                import json
                import os
                from pathlib import Path

                output = Path(os.environ["DESIGNFORGE_OUTPUT_DIR"]) / "render.png"
                output.write_bytes(b"fake")
                print(json.dumps({"protocol": os.environ["DESIGNFORGE_RENDER_PROTOCOL"], "artifact": "render.png"}))
                """,
            )

            result = self.render(target, adapter)
            self.assertEqual(result.returncode, 1)
            self.assertIn("invalid render signature", result.stderr)

    def test_adapter_rejects_wrong_protocol(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            target.mkdir()
            self.init_target(target)
            adapter = self.write_adapter(
                root,
                """
                import json
                import os
                from pathlib import Path

                output = Path(os.environ["DESIGNFORGE_OUTPUT_DIR"]) / "render.png"
                output.write_bytes(b"\\x89PNG\\r\\n\\x1a\\nrender")
                print(json.dumps({"protocol": "wrong", "artifact": "render.png"}))
                """,
            )

            result = self.render(target, adapter)
            self.assertEqual(result.returncode, 1)
            self.assertIn("designforge-render-adapter-v1", result.stderr)

    def test_adapter_failure_is_reported_and_staging_run_is_removed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "project"
            target.mkdir()
            self.init_target(target)
            adapter = self.write_adapter(root, "raise SystemExit(7)\n")

            result = self.render(target, adapter)
            self.assertEqual(result.returncode, 1)
            self.assertIn("exited with code 7", result.stderr)
            staging = target / ".DesignForge" / "render-staging"
            if staging.exists():
                self.assertEqual(list(staging.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
