from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "designforge" / "scripts" / "designforge.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class NestedManifestScannerTests(unittest.TestCase):
    def test_scan_detects_nested_frontend_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            desktop = target / "desktop"
            (desktop / "src").mkdir(parents=True)
            (desktop / "package.json").write_text(
                json.dumps(
                    {
                        "dependencies": {
                            "react": "^19.0.0",
                            "@heroui/react": "^3.0.0",
                            "motion": "^13.0.0",
                            "lucide-react": "^0.468.0",
                        },
                        "devDependencies": {
                            "tailwindcss": "^4.0.0",
                            "vite": "^6.0.0",
                        },
                    }
                ),
                encoding="utf-8",
            )
            (desktop / "src" / "App.tsx").write_text(
                "export function App() { return <main>Hello</main>; }\n",
                encoding="utf-8",
            )
            (desktop / "src" / "design-system.css").write_text(
                ":root { --accent: #5b82ff; }\nbutton { color: var(--accent); }\n",
                encoding="utf-8",
            )

            init = run_cli("init", str(target), "--mode", "refactor")
            self.assertEqual(init.returncode, 0, init.stderr)
            scan = run_cli("scan", str(target))
            self.assertEqual(scan.returncode, 0, scan.stderr)

            evidence = (target / ".DesignForge" / "codebase" / "EVIDENCE.md").read_text(encoding="utf-8")
            self.assertIn("`desktop/package.json`", evidence)
            self.assertIn("Node.js package manifest", evidence)
            self.assertIn("React", evidence)
            self.assertIn("HeroUI", evidence)
            self.assertIn("Tailwind CSS", evidence)
            self.assertIn("Motion / Framer Motion", evidence)
            self.assertIn("Lucide", evidence)
            self.assertIn("`desktop/src/App.tsx`", evidence)

    def test_scan_ignores_dependency_manifests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            dependency = target / "node_modules" / "fake-ui"
            dependency.mkdir(parents=True)
            (dependency / "package.json").write_text(
                json.dumps({"dependencies": {"react": "999.0.0"}}),
                encoding="utf-8",
            )

            self.assertEqual(run_cli("init", str(target), "--mode", "refactor").returncode, 0)
            scan = run_cli("scan", str(target))
            self.assertEqual(scan.returncode, 0, scan.stderr)

            evidence = (target / ".DesignForge" / "codebase" / "EVIDENCE.md").read_text(encoding="utf-8")
            self.assertNotIn("node_modules/fake-ui/package.json", evidence)
            self.assertNotIn("React", evidence)

    def test_scan_limits_nested_manifest_depth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            too_deep = target / "one" / "two" / "three" / "four"
            too_deep.mkdir(parents=True)
            (too_deep / "package.json").write_text(
                json.dumps({"dependencies": {"react": "^19.0.0"}}),
                encoding="utf-8",
            )

            self.assertEqual(run_cli("init", str(target), "--mode", "refactor").returncode, 0)
            scan = run_cli("scan", str(target))
            self.assertEqual(scan.returncode, 0, scan.stderr)

            evidence = (target / ".DesignForge" / "codebase" / "EVIDENCE.md").read_text(encoding="utf-8")
            self.assertNotIn("one/two/three/four/package.json", evidence)
            self.assertNotIn("React", evidence)

    def test_scan_reports_invalid_nested_package_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            app = target / "apps" / "web"
            app.mkdir(parents=True)
            (app / "package.json").write_text("{ invalid json", encoding="utf-8")

            self.assertEqual(run_cli("init", str(target), "--mode", "refactor").returncode, 0)
            scan = run_cli("scan", str(target))
            self.assertEqual(scan.returncode, 0, scan.stderr)

            evidence = (target / ".DesignForge" / "codebase" / "EVIDENCE.md").read_text(encoding="utf-8")
            self.assertIn("`apps/web/package.json` exists but could not be parsed as JSON", evidence)


if __name__ == "__main__":
    unittest.main()
