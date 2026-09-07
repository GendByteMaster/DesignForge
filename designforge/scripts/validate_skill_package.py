#!/usr/bin/env python3
"""Validate the portable DesignForge Agent Skill package."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = SKILL_ROOT / "SKILL.md"
OPENAI_YAML = SKILL_ROOT / "agents" / "openai.yaml"
ALLOWED_FRONTMATTER_KEYS = {"name", "description"}
REQUIRED_OPENAI_KEYS = {"display_name", "short_description", "default_prompt"}
MAPPING_TEMPLATES = (
    "STACK.md",
    "UI_ARCHITECTURE.md",
    "COMPONENTS.md",
    "STYLES.md",
    "SCREENS.md",
    "CONCERNS.md",
)
MAPPING_SECTIONS = (
    "## Scope",
    "## Verified findings",
    "## Inferences",
    "## Unknowns",
    "## Evidence index",
)
VISUAL_QA_SECTIONS = (
    "## Scope",
    "## Capture matrix",
    "## Findings",
    "## Accessibility observations",
    "## Unverified states",
    "## Verdict",
)


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    if not text.startswith("---\n"):
        return {}, ["SKILL.md must start with YAML frontmatter"]

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, ["SKILL.md frontmatter is not closed"]

    metadata: dict[str, str] = {}
    errors: list[str] = []
    for raw_line in text[4:end].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if raw_line[:1].isspace():
            errors.append("SKILL.md frontmatter must not contain nested metadata")
            continue
        if ":" not in line:
            errors.append(f"invalid frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")
    return metadata, errors


def parse_openai_interface(text: str) -> tuple[dict[str, str], list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "interface:":
        return {}, ["agents/openai.yaml must start with 'interface:'"]

    values: dict[str, str] = {}
    errors: list[str] = []
    for raw_line in lines[1:]:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if not raw_line.startswith(("  ", "\t")):
            errors.append("agents/openai.yaml may only contain keys under interface")
            continue
        line = raw_line.strip()
        if ":" not in line:
            errors.append(f"invalid agents/openai.yaml line: {line}")
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values, errors


def validate_mapping_resources(errors: list[str]) -> None:
    codebase_assets = SKILL_ROOT / "assets" / "codebase"
    for name in MAPPING_TEMPLATES:
        path = codebase_assets / name
        if not path.is_file():
            errors.append(f"missing mapping template: assets/codebase/{name}")
            continue
        text = path.read_text(encoding="utf-8")
        for heading in MAPPING_SECTIONS:
            if heading not in text:
                errors.append(f"assets/codebase/{name} is missing {heading}")

    scripts = {
        "mapping provenance validator": "validate_mapping_artifacts.py",
        "mapping freshness checker": "mapping_freshness.py",
    }
    for label, filename in scripts.items():
        if not (SKILL_ROOT / "scripts" / filename).is_file():
            errors.append(f"missing {label}: scripts/{filename}")


def validate_visual_resources(errors: list[str]) -> None:
    template = SKILL_ROOT / "assets" / "reviews" / "VISUAL_QA.md"
    if not template.is_file():
        errors.append("missing visual QA template: assets/reviews/VISUAL_QA.md")
    else:
        text = template.read_text(encoding="utf-8")
        if not text.startswith("# Visual QA"):
            errors.append("assets/reviews/VISUAL_QA.md must start with '# Visual QA'")
        for heading in VISUAL_QA_SECTIONS:
            if heading not in text:
                errors.append(f"assets/reviews/VISUAL_QA.md is missing {heading}")
        if "Status: pending" not in text:
            errors.append("assets/reviews/VISUAL_QA.md must default to Status: pending")

    if not (SKILL_ROOT / "scripts" / "visual_qa.py").is_file():
        errors.append("missing visual QA validator: scripts/visual_qa.py")


def validate() -> list[str]:
    errors: list[str] = []

    if not SKILL_MD.is_file():
        return ["designforge/SKILL.md is missing"]

    metadata, frontmatter_errors = parse_frontmatter(SKILL_MD.read_text(encoding="utf-8"))
    errors.extend(frontmatter_errors)

    keys = set(metadata)
    extra = keys - ALLOWED_FRONTMATTER_KEYS
    missing = ALLOWED_FRONTMATTER_KEYS - keys
    if extra:
        errors.append("SKILL.md frontmatter has unsupported keys: " + ", ".join(sorted(extra)))
    if missing:
        errors.append("SKILL.md frontmatter is missing: " + ", ".join(sorted(missing)))

    name = metadata.get("name", "")
    if name != SKILL_ROOT.name:
        errors.append("SKILL.md name must match the skill directory name")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append("SKILL.md name must use lowercase letters, numbers, and hyphens")
    if len(name) > 64:
        errors.append("SKILL.md name must be 64 characters or fewer")
    if not metadata.get("description"):
        errors.append("SKILL.md description must not be empty")

    if not OPENAI_YAML.is_file():
        errors.append("agents/openai.yaml is missing")
    else:
        interface, interface_errors = parse_openai_interface(
            OPENAI_YAML.read_text(encoding="utf-8")
        )
        errors.extend(interface_errors)
        missing_openai = REQUIRED_OPENAI_KEYS - set(interface)
        if missing_openai:
            errors.append(
                "agents/openai.yaml is missing interface keys: "
                + ", ".join(sorted(missing_openai))
            )
        short_description = interface.get("short_description", "")
        if short_description and not (25 <= len(short_description) <= 64):
            errors.append("OpenAI short_description must be 25-64 characters")
        default_prompt = interface.get("default_prompt", "")
        if default_prompt and "$designforge" not in default_prompt:
            errors.append("OpenAI default_prompt must reference $designforge")

    for required_dir in ("assets", "references", "scripts", "workflows"):
        if not (SKILL_ROOT / required_dir).is_dir():
            errors.append(f"missing skill resource directory: {required_dir}/")

    validate_mapping_resources(errors)
    validate_visual_resources(errors)
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("DesignForge skill package validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
