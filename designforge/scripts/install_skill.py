#!/usr/bin/env python3
"""Install the DesignForge skill into a coding-agent project directory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from installer import SUPPORTED_PROVIDERS, install_project_skill

SKILL_ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="install-designforge",
        description="Install DesignForge into a project-local coding-agent skill directory.",
    )
    parser.add_argument(
        "provider",
        choices=sorted(SUPPORTED_PROVIDERS),
        help="coding agent to install for",
    )
    parser.add_argument(
        "project",
        nargs="?",
        default=".",
        help="target project directory (default: current directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing project-local DesignForge skill",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        destination = install_project_skill(
            SKILL_ROOT,
            Path(args.project),
            args.provider,
            force=args.force,
        )
    except (FileExistsError, FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"Installed DesignForge for {args.provider}: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
