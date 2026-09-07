"""Workflow transition policy for the DesignForge operational toolkit."""

from __future__ import annotations

VALID_MODES = {"conservative", "refactor", "reimagine"}
VALID_WORKFLOWS = {
    "init",
    "map",
    "discuss",
    "direct",
    "systemize",
    "plan",
    "build",
    "review",
    "continue",
    "guard",
}
VALID_STATUSES = {"initialized", "ready", "in-progress", "blocked", "review", "complete"}

# These transitions encode the normal DesignForge lifecycle. They intentionally
# allow bounded loops for design iteration while preventing accidental jumps
# across major prerequisites. Low-level state updates remain available for
# recovery and explicit overrides.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "init": {"map", "discuss", "direct", "continue"},
    "map": {"discuss", "direct", "systemize", "plan", "continue"},
    "discuss": {"direct", "systemize", "plan", "build", "continue"},
    "direct": {"discuss", "systemize", "plan", "continue"},
    "systemize": {"direct", "plan", "build", "continue"},
    "plan": {"discuss", "direct", "systemize", "build", "continue"},
    "build": {"plan", "review", "build", "continue"},
    "review": {"build", "plan", "guard", "continue"},
    "continue": set(VALID_WORKFLOWS) - {"init"},
    "guard": {"build", "review", "guard", "continue"},
}


def can_transition(current: str, target: str) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())


def allowed_targets(current: str) -> list[str]:
    return sorted(ALLOWED_TRANSITIONS.get(current, set()))
