from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "designforge" / "scripts" / "validate_skill_package.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("designforge_validate_skill_package", VALIDATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillPackageContractTests(unittest.TestCase):
    def test_portable_skill_package_is_valid(self) -> None:
        validator = load_validator()
        self.assertEqual(validator.validate(), [])

    def test_renderer_adapter_is_a_required_visual_resource(self) -> None:
        validator = load_validator()
        renderer = ROOT / "designforge" / "scripts" / "render_adapter.py"
        reference = ROOT / "designforge" / "references" / "RENDER_ADAPTER.md"
        self.assertTrue(renderer.is_file())
        self.assertTrue(reference.is_file())

        reference_text = reference.read_text(encoding="utf-8")
        for heading in validator.RENDER_ADAPTER_REFERENCE_SECTIONS:
            with self.subTest(heading=heading):
                self.assertIn(heading, reference_text)

    def test_playwright_browser_adapter_is_a_portable_optional_provider(self) -> None:
        validator = load_validator()
        adapter = ROOT / "designforge" / "adapters" / "playwright_browser.py"
        reference = ROOT / "designforge" / "references" / "BROWSER_ADAPTER.md"
        self.assertTrue(adapter.is_file())
        self.assertTrue(reference.is_file())

        reference_text = reference.read_text(encoding="utf-8")
        for heading in validator.BROWSER_ADAPTER_REFERENCE_SECTIONS:
            with self.subTest(heading=heading):
                self.assertIn(heading, reference_text)

        adapter_text = adapter.read_text(encoding="utf-8")
        self.assertNotIn("import playwright", adapter_text.split("def main", 1)[0])
        self.assertIn("designforge-render-adapter-v1", adapter_text)

    def test_visual_qa_reference_requires_capture_handoff(self) -> None:
        validator = load_validator()
        self.assertIn("## Capture handoff", validator.VISUAL_QA_REFERENCE_SECTIONS)


if __name__ == "__main__":
    unittest.main()
