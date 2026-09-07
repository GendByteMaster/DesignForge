#!/usr/bin/env python3
"""Small dependency-free operational toolkit for the DesignForge skill."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from state_machine import (
    VALID_MODES,
    VALID_STATUSES,
    VALID_WORKFLOWS,
    allowed_targets,
    can_transition,
)

SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = SKILL_ROOT / "assets"

PHASE_FILES = {
    "CONTEXT.md": "# Phase Context\n\n## Goal\n\n## User decisions\n\n## Constraints\n\n## Non-negotiables\n",
    "RESEARCH.md": "# Phase Research\n\n## Evidence\n\n## Findings\n\n## Open questions\n",
    "PLAN.md": "# Phase Plan\n\n## Outcome\n\n## Scope\n\n## Tasks\n\n## Validation\n",
    "DESIGN.md": "# Phase Design\n\n## Intent\n\n## Layout\n\n## Components\n\n## States\n\n## Responsive behavior\n\n## Accessibility\n",
    "IMPLEMENTATION.md": "# Phase Implementation\n\n## Affected areas\n\n## Changes\n\n## Verification\n",
    "REVIEW.md": "# Phase Review\n\n## Visual QA\n\n## Accessibility\n\n## Consistency\n\n## Defects\n",
    "RESULT.md": "# Phase Result\n\n## Completed\n\n## Remaining\n\n## Decisions\n\n## Next\n",
}


def fail(message: str, code: int = 2) -> int:
    print(f"error: {message}", file=sys.stderr)
    return code


def replace_prefixed_line(text: str, prefix: str, value: str) -> str:
    pattern = re.compile(rf"^{re.escape(prefix)}.*$", re.MULTILINE)
    replacement = f"{prefix}{value}"
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    suffix = "" if text.endswith("\n") else "\n"
    return f"{text}{suffix}{replacement}\n"


def read_prefixed_line(text: str, prefix: str) -> str | None:
    match = re.search(rf"^{re.escape(prefix)}(.*)$", text, re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def set_project_mode(text: str, mode: str) -> str:
    marker = "<!-- conservative | refactor | reimagine -->"
    if marker in text:
        return text.replace(marker, mode, 1)

    heading = "## Redesign mode"
    if heading in text:
        section = re.compile(r"(## Redesign mode\s*\n)(.*?)(?=\n## |\Z)", re.DOTALL)
        if section.search(text):
            return section.sub(rf"\1\n{mode}\n", text, count=1)
    return text.rstrip() + f"\n\n## Redesign mode\n\n{mode}\n"


def extract_project_mode(text: str) -> str | None:
    match = re.search(r"^## Redesign mode\s*\n+\s*([^\n#<][^\n]*)", text, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    if not target.exists() or not target.is_dir():
        return fail(f"target directory does not exist: {target}")

    workspace = target / ".DesignForge"
    workspace.mkdir(parents=True, exist_ok=True)

    project_dst = workspace / "PROJECT.md"
    state_dst = workspace / "STATE.md"

    project_exists = project_dst.exists()
    state_exists = state_dst.exists()

    if not project_exists or args.force:
        project = (ASSETS_DIR / "PROJECT.md").read_text(encoding="utf-8")
        project = set_project_mode(project, args.mode)
        project_dst.write_text(project, encoding="utf-8")

    if not state_exists or args.force:
        state = (ASSETS_DIR / "STATE.md").read_text(encoding="utf-8")
        state = replace_prefixed_line(state, "Mode: ", args.mode)
        state = replace_prefixed_line(state, "Current workflow: ", "init")
        state = replace_prefixed_line(state, "Status: ", "initialized")
        state_dst.write_text(state, encoding="utf-8")

    print(f"DesignForge workspace: {workspace}")
    print(f"PROJECT.md: {'overwritten' if project_exists and args.force else 'preserved' if project_exists else 'created'}")
    print(f"STATE.md: {'overwritten' if state_exists and args.force else 'preserved' if state_exists else 'created'}")
    return 0


def slugify(value: str) -> str:
    value = value.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def next_phase_number(phases_dir: Path) -> int:
    highest = 0
    if phases_dir.exists():
        for child in phases_dir.iterdir():
            if not child.is_dir():
                continue
            match = re.match(r"^(\d+)-", child.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return highest + 1


def cmd_phase(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    workspace = target / ".DesignForge"
    state_path = workspace / "STATE.md"
    if not state_path.exists():
        return fail(".DesignForge/STATE.md not found; run init first")

    slug = slugify(args.name)
    if not slug:
        return fail("phase name must contain at least one ASCII letter or number")

    phases_dir = workspace / "phases"
    number = args.number if args.number is not None else next_phase_number(phases_dir)
    if number < 1:
        return fail("phase number must be greater than zero")

    phase_id = f"{number:02d}-{slug}"
    phase_dir = phases_dir / phase_id

    if phase_dir.exists() and not args.force:
        return fail(f"phase already exists: {phase_id}")

    phase_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in PHASE_FILES.items():
        path = phase_dir / filename
        if path.exists() and not args.force:
            continue
        path.write_text(content, encoding="utf-8")

    state = state_path.read_text(encoding="utf-8")
    state = replace_prefixed_line(state, "Current phase: ", phase_id)
    state = replace_prefixed_line(state, "Current workflow: ", "plan")
    state = replace_prefixed_line(state, "Status: ", "ready")
    state_path.write_text(state, encoding="utf-8")

    print(f"Created phase: {phase_id}")
    return 0


def cmd_state(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    state_path = target / ".DesignForge" / "STATE.md"
    if not state_path.exists():
        return fail(".DesignForge/STATE.md not found; run init first")

    state = state_path.read_text(encoding="utf-8")
    if args.phase is not None:
        state = replace_prefixed_line(state, "Current phase: ", args.phase)
    if args.workflow is not None:
        state = replace_prefixed_line(state, "Current workflow: ", args.workflow)
    if args.mode is not None:
        state = replace_prefixed_line(state, "Mode: ", args.mode)
    if args.status is not None:
        state = replace_prefixed_line(state, "Status: ", args.status)
    state_path.write_text(state, encoding="utf-8")
    print(f"Updated state: {state_path}")
    return 0


def cmd_transition(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    state_path = target / ".DesignForge" / "STATE.md"
    if not state_path.exists():
        return fail(".DesignForge/STATE.md not found; run init first")

    state = state_path.read_text(encoding="utf-8")
    current = read_prefixed_line(state, "Current workflow: ")
    if current not in VALID_WORKFLOWS:
        return fail("STATE.md contains an invalid or missing Current workflow")

    if not args.force and not can_transition(current, args.workflow):
        allowed = ", ".join(allowed_targets(current)) or "none"
        return fail(f"transition {current} -> {args.workflow} is not allowed; allowed: {allowed}")

    state = replace_prefixed_line(state, "Current workflow: ", args.workflow)
    state = replace_prefixed_line(state, "Status: ", args.status)
    state_path.write_text(state, encoding="utf-8")
    print(f"Transitioned workflow: {current} -> {args.workflow}")
    return 0


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    result: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if line.startswith(" ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def validate_skill() -> list[str]:
    errors: list[str] = []
    skill_path = SKILL_ROOT / "SKILL.md"
    if not skill_path.exists():
        return ["designforge/SKILL.md is missing"]

    text = skill_path.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)
    if frontmatter.get("name") != SKILL_ROOT.name:
        errors.append("SKILL.md name must match the skill folder name")
    if not frontmatter.get("description"):
        errors.append("SKILL.md description is missing")

    for name in sorted(VALID_WORKFLOWS):
        path = SKILL_ROOT / "workflows" / f"{name.upper()}.md"
        if not path.exists():
            errors.append(f"missing workflow: {path.relative_to(SKILL_ROOT)}")

    for asset in ("PROJECT.md", "STATE.md", "ROADMAP.md", "DESIGN.md", "DESIGN_SYSTEM.md"):
        path = ASSETS_DIR / asset
        if not path.exists():
            errors.append(f"missing asset: assets/{asset}")

    if not (Path(__file__).resolve().parent / "state_machine.py").exists():
        errors.append("missing operational state machine")
    return errors


def validate_workspace(target: Path) -> list[str]:
    errors: list[str] = []
    workspace = target / ".DesignForge"
    if not workspace.exists():
        return [".DesignForge directory is missing"]
    for name in ("PROJECT.md", "STATE.md"):
        if not (workspace / name).exists():
            errors.append(f".DesignForge/{name} is missing")

    state_path = workspace / "STATE.md"
    state_mode: str | None = None
    if state_path.exists():
        state = state_path.read_text(encoding="utf-8")
        state_mode = read_prefixed_line(state, "Mode: ")
        workflow = read_prefixed_line(state, "Current workflow: ")
        status = read_prefixed_line(state, "Status: ")
        phase = read_prefixed_line(state, "Current phase: ")

        if state_mode not in VALID_MODES:
            errors.append("STATE.md contains an invalid or missing Mode")
        if workflow not in VALID_WORKFLOWS:
            errors.append("STATE.md contains an invalid or missing Current workflow")
        if status not in VALID_STATUSES:
            errors.append("STATE.md contains an invalid or missing Status")
        if phase and phase != "not-started" and not (workspace / "phases" / phase).is_dir():
            errors.append(f"STATE.md references a missing phase directory: {phase}")

    project_path = workspace / "PROJECT.md"
    if project_path.exists():
        project_mode = extract_project_mode(project_path.read_text(encoding="utf-8"))
        if project_mode not in VALID_MODES:
            errors.append("PROJECT.md contains an invalid or missing Redesign mode")
        elif state_mode in VALID_MODES and project_mode != state_mode:
            errors.append("PROJECT.md Redesign mode does not match STATE.md Mode")
    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    errors = validate_skill()
    if args.target is not None:
        errors.extend(validate_workspace(Path(args.target).resolve()))

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    print("DesignForge validation passed")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="designforge", description="Operational toolkit for DesignForge workflows")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="initialize .DesignForge in a target project")
    init_parser.add_argument("target", nargs="?", default=".")
    init_parser.add_argument("--mode", choices=sorted(VALID_MODES), default="refactor")
    init_parser.add_argument("--force", action="store_true", help="overwrite managed root artifacts")
    init_parser.set_defaults(func=cmd_init)

    phase_parser = subparsers.add_parser("phase", help="create a numbered DesignForge phase")
    phase_parser.add_argument("name")
    phase_parser.add_argument("--target", default=".")
    phase_parser.add_argument("--number", type=int)
    phase_parser.add_argument("--force", action="store_true")
    phase_parser.set_defaults(func=cmd_phase)

    transition_parser = subparsers.add_parser("transition", help="move to an allowed workflow state")
    transition_parser.add_argument("workflow", choices=sorted(VALID_WORKFLOWS))
    transition_parser.add_argument("--target", default=".")
    transition_parser.add_argument("--status", choices=sorted(VALID_STATUSES), default="ready")
    transition_parser.add_argument("--force", action="store_true", help="allow an explicit non-standard transition")
    transition_parser.set_defaults(func=cmd_transition)

    state_parser = subparsers.add_parser("state", help="low-level recovery update for compact workflow state")
    state_parser.add_argument("--target", default=".")
    state_parser.add_argument("--phase")
    state_parser.add_argument("--workflow", choices=sorted(VALID_WORKFLOWS))
    state_parser.add_argument("--mode", choices=sorted(VALID_MODES))
    state_parser.add_argument("--status", choices=sorted(VALID_STATUSES))
    state_parser.set_defaults(func=cmd_state)

    validate_parser = subparsers.add_parser("validate", help="validate the skill package and optionally a project workspace")
    validate_parser.add_argument("--target")
    validate_parser.set_defaults(func=cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
