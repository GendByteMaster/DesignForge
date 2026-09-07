# Workflow: build

Implement the active DesignForge phase and close the loop between design intent, code, and rendered UI.

## Goal

Produce a working implementation that follows the active design direction and design-system contracts, then verify it technically and visually when tooling allows.

## Reads

- `.DesignForge/STATE.md`
- `.DesignForge/PROJECT.md`
- `.DesignForge/DESIGN.md`
- active phase `CONTEXT.md`, `PLAN.md`, and `DESIGN.md` when present
- only relevant `.DesignForge/system/` artifacts
- affected source files

## Writes

- product source code
- `.DesignForge/phases/<phase>/REVIEW.md` when findings exist
- `.DesignForge/phases/<phase>/RESULT.md`
- `.DesignForge/STATE.md`

## Procedure

1. Read `STATE.md` first and identify the active phase and intended next action.
2. Load only the design and system contracts relevant to the affected surface.
3. Inspect the current source implementation before editing.
4. Preserve required business logic and non-negotiable behavior.
5. Reuse existing/native accessible primitives before creating new custom primitives.
6. Implement the bounded phase scope.
7. Run the relevant available checks, such as lint, type checking, unit tests, integration tests, build, or platform-specific validation.
8. Render the affected UI when browser, emulator, simulator, preview, screenshot, or equivalent tooling is available.
9. Inspect the rendered result for:
   - hierarchy;
   - spacing and alignment;
   - typography;
   - density;
   - color and contrast;
   - component states;
   - responsive behavior;
   - focus and keyboard behavior;
   - obvious accessibility defects;
   - fidelity to `DESIGN.md`.
10. Record material defects in `REVIEW.md`.
11. Fix material defects that are in scope.
12. Re-render and inspect again when possible.
13. Write `RESULT.md` with what was implemented, checks run, visual inspection status, unresolved issues, and follow-up work.
14. Update `STATE.md` accurately.

## Rules

- Compilation alone is not completion for visual work.
- Do not expand the phase into unrelated redesign work.
- Do not introduce one-off colors, spacing, radii, or component behavior when an active system contract exists.
- If visual tooling is unavailable, say so in `RESULT.md`; do not claim visual validation occurred.
- Repository reality wins over stale plan text. Repair the plan/state if implementation conditions materially changed.

## Completion

A build phase is complete when:

- requested scope is implemented;
- relevant technical checks pass or failures are explicitly documented;
- rendered UI was inspected when tooling allowed it;
- material in-scope visual defects were addressed;
- `RESULT.md` and `STATE.md` match repository reality.
