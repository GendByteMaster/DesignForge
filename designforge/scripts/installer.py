"""Project-local installation helpers for DesignForge coding-agent skills."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

SUPPORTED_PROVIDERS = {"codex", "claude"}
PROVIDER_SKILL_ROOTS = {
    "codex": Path(".agents") / "skills",
    "claude": Path(".claude") / "skills",
}


def skill_destination(project: Path, provider: str, skill_name: str = "designforge") -> Path:
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"unsupported provider: {provider}")
    return project / PROVIDER_SKILL_ROOTS[provider] / skill_name


def _ignore_generated(_: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name == "__pycache__" or name.endswith((".pyc", ".pyo")):
            ignored.add(name)
    return ignored


def install_project_skill(
    source_skill: Path,
    project: Path,
    provider: str,
    *,
    force: bool = False,
) -> Path:
    source_skill = source_skill.resolve()
    project = project.resolve()

    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"unsupported provider: {provider}")
    if not project.exists() or not project.is_dir():
        raise FileNotFoundError(f"project directory does not exist: {project}")
    if not (source_skill / "SKILL.md").is_file():
        raise FileNotFoundError(f"source skill is missing SKILL.md: {source_skill}")

    destination = skill_destination(project, provider, source_skill.name)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists() and not force:
        raise FileExistsError(
            f"skill already exists at {destination}; use --force to replace it"
        )

    staging_parent = destination.parent
    staging = Path(
        tempfile.mkdtemp(prefix=f".{source_skill.name}-install-", dir=staging_parent)
    )
    backup: Path | None = None

    try:
        staged_skill = staging / source_skill.name
        shutil.copytree(source_skill, staged_skill, ignore=_ignore_generated)

        if not (staged_skill / "SKILL.md").is_file():
            raise RuntimeError("staged skill is missing SKILL.md")

        if destination.exists():
            backup = destination.with_name(f".{destination.name}.backup")
            if backup.exists():
                shutil.rmtree(backup)
            destination.rename(backup)

        staged_skill.rename(destination)

        if backup is not None and backup.exists():
            shutil.rmtree(backup)
    except Exception:
        if destination.exists() and backup is not None and backup.exists():
            shutil.rmtree(destination)
        if backup is not None and backup.exists() and not destination.exists():
            backup.rename(destination)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)

    return destination
