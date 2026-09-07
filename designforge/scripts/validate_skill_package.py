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
