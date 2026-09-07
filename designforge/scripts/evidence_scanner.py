"""Deterministic repository evidence collection for the DesignForge map workflow.

This module intentionally reports observable signals instead of making design
judgments. The MAP workflow remains responsible for interpreting the evidence.
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

EXCLUDED_DIRS = {
    ".git",
    ".DesignForge",
    ".next",
    ".nuxt",
    ".svelte-kit",
    ".turbo",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "target",
    "vendor",
}

SOURCE_EXTENSIONS = {
    ".tsx",
    ".ts",
    ".jsx",
    ".js",
    ".vue",
    ".svelte",
    ".dart",
    ".swift",
    ".kt",
    ".kts",
    ".rs",
    ".py",
    ".html",
}
STYLE_EXTENSIONS = {".css", ".scss", ".sass", ".less", ".styl"}
MAX_TEXT_FILE_BYTES = 1_000_000
MAX_FILES = 10_000
MAX_LIST_ITEMS = 60
MAX_MANIFESTS = 100
MAX_MANIFEST_DEPTH = 3

MANIFESTS = (
    "package.json",
    "pubspec.yaml",
    "Cargo.toml",
    "pyproject.toml",
    "requirements.txt",
    "composer.json",
    "go.mod",
)

PACKAGE_SIGNALS: dict[str, dict[str, tuple[str, ...]]] = {
    "Frameworks": {
        "Next.js": ("next",),
        "React": ("react", "react-dom"),
        "Vue": ("vue",),
        "Nuxt": ("nuxt",),
        "Svelte": ("svelte", "@sveltejs/kit"),
        "Angular": ("@angular/core",),
        "Solid": ("solid-js",),
    },
    "UI libraries / primitives": {
        "Radix UI": ("@radix-ui/",),
        "Material UI": ("@mui/",),
        "Chakra UI": ("@chakra-ui/",),
        "Ant Design": ("antd",),
        "HeroUI": ("@heroui/", "@nextui-org/"),
        "Headless UI": ("@headlessui/",),
        "React Aria": ("react-aria", "react-aria-components", "@react-aria/"),
    },
    "Styling": {
        "Tailwind CSS": ("tailwindcss", "@tailwindcss/"),
        "styled-components": ("styled-components",),
        "Emotion": ("@emotion/",),
        "Sass": ("sass",),
        "Vanilla Extract": ("@vanilla-extract/",),
    },
    "Motion": {
        "Motion / Framer Motion": ("motion", "framer-motion"),
        "GSAP": ("gsap",),
        "React Spring": ("@react-spring/",),
    },
    "Icons": {
        "Lucide": ("lucide", "lucide-react"),
        "Heroicons": ("@heroicons/",),
        "React Icons": ("react-icons",),
        "Phosphor": ("@phosphor-icons/",),
    },
    "State management": {
        "Zustand": ("zustand",),
        "Redux": ("redux", "@reduxjs/toolkit", "react-redux"),
        "Jotai": ("jotai",),
        "MobX": ("mobx", "mobx-react-lite"),
        "Pinia": ("pinia",),
    },
}

HEX_COLOR_RE = re.compile(r"(?<![\w-])#[0-9a-fA-F]{3,8}\b")
FUNCTION_COLOR_RE = re.compile(r"\b(?:rgb|rgba|hsl|hsla)\s*\(", re.IGNORECASE)
CSS_VAR_DEF_RE = re.compile(r"--[a-zA-Z0-9_-]+\s*:")
CSS_VAR_USE_RE = re.compile(r"var\(\s*--[a-zA-Z0-9_-]+")
RADIUS_RE = re.compile(r"\bborder-radius\s*:", re.IGNORECASE)
SHADOW_RE = re.compile(r"\bbox-shadow\s*:", re.IGNORECASE)
IMPORTANT_RE = re.compile(r"!important\b", re.IGNORECASE)


def iter_repo_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirs, filenames in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
        current_path = Path(current)
        for filename in sorted(filenames):
            path = current_path / filename
            try:
                if path.is_symlink() or path.stat().st_size > MAX_TEXT_FILE_BYTES:
                    continue
            except OSError:
                continue
            files.append(path)
            if len(files) >= MAX_FILES:
                return files
    return files


def relative_paths(root: Path, files: Iterable[Path]) -> list[str]:
    return [path.relative_to(root).as_posix() for path in files]


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def discover_manifests(paths: list[str]) -> list[str]:
    """Return known manifests from the bounded repository file inventory.

    Discovery deliberately reuses ``iter_repo_files`` output instead of starting
    an independent recursive glob. This preserves the same exclusions and file
    cap while supporting common layouts such as ``desktop/package.json`` and
    ``apps/web/package.json``.
    """

    manifests: list[str] = []
    for path in paths:
        candidate = Path(path)
        if candidate.name not in MANIFESTS:
            continue
        directory_depth = len(candidate.parts) - 1
        if directory_depth > MAX_MANIFEST_DEPTH:
            continue
        manifests.append(path)
        if len(manifests) >= MAX_MANIFESTS:
            break
    return manifests


def load_package_jsons(root: Path, manifests: Iterable[str]) -> tuple[dict[str, str], list[str]]:
    packages: dict[str, str] = {}
    errors: list[str] = []

    for relative in manifests:
        if Path(relative).name != "package.json":
            continue
        package_path = root / relative
        try:
            raw = json.loads(package_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            errors.append(f"`{relative}` exists but could not be parsed as JSON")
            continue

        for section in ("dependencies", "devDependencies", "peerDependencies"):
            values = raw.get(section, {})
            if isinstance(values, dict):
                for name, version in values.items():
                    if isinstance(name, str):
                        packages[name] = str(version)

    return packages, errors


def package_matches(packages: dict[str, str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    package_names = tuple(packages)
    for category, signals in PACKAGE_SIGNALS.items():
        detected: list[str] = []
        for label, prefixes in signals.items():
            if any(any(name == prefix or name.startswith(prefix) for prefix in prefixes) for name in package_names):
                detected.append(label)
        if detected:
            result[category] = detected
    return result


def detect_platform_signals(paths: list[str], manifests: Iterable[str]) -> list[str]:
    found: list[str] = []
    manifest_names = {Path(path).name for path in manifests}
    if "pubspec.yaml" in manifest_names:
        found.append("Flutter/Dart manifest (`pubspec.yaml`)")
    if "Cargo.toml" in manifest_names:
        found.append("Rust manifest (`Cargo.toml`)")
    if "pyproject.toml" in manifest_names or "requirements.txt" in manifest_names:
        found.append("Python project manifest")
    if "package.json" in manifest_names:
        found.append("Node.js package manifest (`package.json`)")
    if "composer.json" in manifest_names:
        found.append("PHP/Composer manifest (`composer.json`)")
    if "go.mod" in manifest_names:
        found.append("Go module manifest (`go.mod`)")
    if any(path.startswith("ios/") for path in paths):
        found.append("iOS project directory")
    if any(path.startswith("android/") for path in paths):
        found.append("Android project directory")
    if any(path.endswith(".xcodeproj/project.pbxproj") for path in paths):
        found.append("Xcode project")
    if any(path.endswith(".csproj") for path in paths):
        found.append(".NET project")
    return found


def summarize_extensions(files: list[Path]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in files:
        suffix = path.suffix.lower()
        if suffix in SOURCE_EXTENSIONS or suffix in STYLE_EXTENSIONS:
            counts[suffix or "[no extension]"] += 1
    return counts


def candidate_paths(paths: list[str], directory_names: set[str], extensions: set[str]) -> list[str]:
    matches: list[str] = []
    for path in paths:
        parts = Path(path).parts
        if not any(part.lower() in directory_names for part in parts[:-1]):
            continue
        if Path(path).suffix.lower() not in extensions:
            continue
        matches.append(path)
    return matches[:MAX_LIST_ITEMS]


def detect_structure(paths: list[str]) -> dict[str, list[str]]:
    source_like = SOURCE_EXTENSIONS | STYLE_EXTENSIONS
    return {
        "Component candidates": candidate_paths(paths, {"components", "ui", "widgets"}, source_like),
        "Screen / route candidates": candidate_paths(
            paths,
            {"app", "pages", "screens", "views", "routes"},
            SOURCE_EXTENSIONS,
        ),
        "Style / theme candidates": candidate_paths(
            paths,
            {"styles", "style", "theme", "themes", "tokens"},
            source_like | {".json", ".yaml", ".yml"},
        ),
    }


def scan_style_signals(files: list[Path]) -> dict[str, int]:
    totals = {
        "hex color literals": 0,
        "rgb/hsl color functions": 0,
        "CSS custom property definitions": 0,
        "CSS custom property uses": 0,
        "border-radius declarations": 0,
        "box-shadow declarations": 0,
        "!important occurrences": 0,
        "style files scanned": 0,
    }
    for path in files:
        if path.suffix.lower() not in STYLE_EXTENSIONS:
            continue
        text = read_text(path)
        if text is None:
            continue
        totals["style files scanned"] += 1
        totals["hex color literals"] += len(HEX_COLOR_RE.findall(text))
        totals["rgb/hsl color functions"] += len(FUNCTION_COLOR_RE.findall(text))
        totals["CSS custom property definitions"] += len(CSS_VAR_DEF_RE.findall(text))
        totals["CSS custom property uses"] += len(CSS_VAR_USE_RE.findall(text))
        totals["border-radius declarations"] += len(RADIUS_RE.findall(text))
        totals["box-shadow declarations"] += len(SHADOW_RE.findall(text))
        totals["!important occurrences"] += len(IMPORTANT_RE.findall(text))
    return totals


def find_config_signals(paths: list[str]) -> list[str]:
    names = (
        "tailwind.config",
        "postcss.config",
        "components.json",
        "vite.config",
        "next.config",
        "nuxt.config",
        "svelte.config",
        "tsconfig.json",
    )
    return [path for path in paths if any(Path(path).name.startswith(name) for name in names)][:MAX_LIST_ITEMS]


def markdown_list(items: Iterable[str], empty: str = "None detected") -> list[str]:
    values = list(items)
    if not values:
        return [f"- {empty}"]
    return [f"- `{item}`" for item in values]


def build_evidence_report(root: Path) -> str:
    files = iter_repo_files(root)
    paths = relative_paths(root, files)
    manifests = discover_manifests(paths)
    packages, package_errors = load_package_jsons(root, manifests)
    package_groups = package_matches(packages)
    platform_signals = detect_platform_signals(paths, manifests)
    extension_counts = summarize_extensions(files)
    structure = detect_structure(paths)
    style_signals = scan_style_signals(files)
    configs = find_config_signals(paths)

    lines: list[str] = [
        "# Codebase Evidence",
        "",
        "> Generated by the DesignForge evidence scanner. This file records observable repository signals; it is not a design audit and does not replace the `map` workflow's reasoning.",
        "",
        "## Scan scope",
        "",
        f"- Files inspected: **{len(files)}**",
        f"- File cap: **{MAX_FILES}**",
        f"- Maximum text file size: **{MAX_TEXT_FILE_BYTES} bytes**",
        f"- Manifest discovery depth: **{MAX_MANIFEST_DEPTH} directories**",
        f"- Manifest cap: **{MAX_MANIFESTS}**",
        "- Excluded generated/dependency directories: " + ", ".join(f"`{name}`" for name in sorted(EXCLUDED_DIRS)),
        "",
        "## Detected manifests",
        "",
        *markdown_list(manifests),
        "",
        "## Platform / ecosystem signals",
        "",
    ]
    lines.extend(f"- {item}" for item in platform_signals or ["None detected from known manifests/directories"])

    lines.extend(["", "## Detected package signals", ""])
    for package_error in package_errors:
        lines.append(f"- Warning: {package_error}")
    if package_groups:
        for category in sorted(package_groups):
            lines.append(f"### {category}")
            lines.append("")
            lines.extend(f"- {item}" for item in package_groups[category])
            lines.append("")
    elif not package_errors:
        lines.append("- No known frontend package signals detected")
        lines.append("")

    lines.extend(["## Relevant source/style extensions", ""])
    if extension_counts:
        lines.extend(f"- `{ext}`: {count}" for ext, count in sorted(extension_counts.items()))
    else:
        lines.append("- No known UI/source extensions detected")

    lines.extend(["", "## Configuration signals", "", *markdown_list(configs), ""])

    for title, candidates in structure.items():
        lines.extend([f"## {title}", "", *markdown_list(candidates), ""])

    lines.extend(["## Style signals", ""])
    for key, value in style_signals.items():
        lines.append(f"- {key}: **{value}**")

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "These counts and paths are evidence only. They do not prove that a value is a design-system violation, that a component is reusable, or that a route is user-facing. The DesignForge `map` workflow must inspect relevant files before turning these signals into `STACK.md`, `UI_ARCHITECTURE.md`, `COMPONENTS.md`, `STYLES.md`, `SCREENS.md`, or `CONCERNS.md` findings.",
            "",
        ]
    )
    return "\n".join(lines)


def write_evidence(root: Path) -> Path:
    workspace = root / ".DesignForge"
    if not (workspace / "STATE.md").exists():
        raise FileNotFoundError(".DesignForge/STATE.md not found; run init first")
    destination = workspace / "codebase" / "EVIDENCE.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_evidence_report(root), encoding="utf-8")
    return destination
