# Workflow: build

Implement the active DesignForge phase and close the loop between design intent, code, and rendered UI.

## Goal

Produce a working implementation that follows the active design direction and design-system contracts, then verify it technically and visually with persistent render evidence when tooling allows.

## Reads

- `.DesignForge/STATE.md`
- `.DesignForge/PROJECT.md`
- `.DesignForge/DESIGN.md`
- active phase `CONTEXT.md`, `PLAN.md`, and `DESIGN.md` when present
- active phase `VISUAL_QA.md` when already initialized
- only relevant `.DesignForge/system/` artifacts
- affected source files

## Writes

- product source code
- `.DesignForge/phases/<phase>/VISUAL_QA.md` when visual validation applies
- `.DesignForge/phases/<phase>/visual-evidence/*` for persistent rendered evidence
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
8. When the affected UI can be rendered or captured with available browser, emulator, simulator, preview, screenshot, native-app, or equivalent tooling, initialize phase-scoped visual QA if needed:

   ```bash
   python designforge/scripts/designforge.py visual init /path/to/project --phase <phase>
   ```

9. Render the affected state using the provider already available in the runtime. The provider may write the screenshot/video anywhere accessible to the agent; DesignForge does not require Playwright or any single browser/native tool.
10. Inspect that exact rendered artifact before registering it as checked evidence. Review hierarchy, spacing, alignment, typography, density, color/contrast, component states, responsive behavior, clipping/overflow, focus visibility, obvious accessibility defects, and fidelity to `DESIGN.md` plus active system contracts.
11. After inspection, import the artifact into the managed phase evidence directory and register the checked capture through the public DesignForge CLI:

   ```bash
   python designforge/scripts/designforge.py visual capture /tmp/render.png /path/to/project \
     --surface "Main Workspace" \
     --state "default" \
     --viewport "1440x900" \
     --phase <phase>
   ```

   `visual capture` validates the declared media format, rejects empty or invalid-signature files, copies external evidence into the correct managed `visual-evidence/` directory without overwriting existing captures, and writes the checked capture-matrix row. Calling it is therefore a claim that the supplied render was actually inspected.
12. Record visual findings and accessibility observations in `VISUAL_QA.md`; record material implementation defects in phase `REVIEW.md` when they require follow-up work.
13. Fix material defects that are in scope.
14. Re-render changed states and inspect again when possible. Register a fresh capture after each materially changed state. Do not keep an old checked capture as proof of a state that changed after the capture.
15. Set the Visual QA verdict through the public CLI rather than editing the status blindly:

   ```bash
   python designforge/scripts/designforge.py visual verdict pass /path/to/project --phase <phase>
   ```

   Valid verdicts are:
   - `pass` — inspected required states have no material visual defect;
   - `pass-with-notes` — inspected states are acceptable with documented non-blocking observations;
   - `fail` — inspected evidence shows unresolved material defects;
   - `blocked` — visual QA is expected but a blocking environment/product condition prevents it;
   - `unavailable` — no suitable render/capture tooling or artifact is available in the current runtime;
   - `pending` — visual QA has not been completed yet.

   `visual verdict` validates the resulting Visual QA contract and rolls the status change back if a conclusive verdict is not supported by inspected evidence.
16. Validate the mechanical visual-evidence contract:

   ```bash
   python designforge/scripts/designforge.py visual validate /path/to/project --phase <phase>
   ```

   Mechanical validation confirms that claimed inspected rows reference managed, existing, non-empty render artifacts with supported signatures. It does not judge visual quality.
17. If visual tooling is unavailable, still record the limitation explicitly when visual validation is material. Never manufacture an evidence path, register an uninspected render, or use `pass`/`fail` without inspected evidence.
18. Write `RESULT.md` with what was implemented, technical checks run, the Visual QA verdict/artifact path, unresolved issues, and follow-up work.
19. Update `STATE.md` accurately.

## Visual evidence rules

- Prefer persistent project-relative render artifacts over transient chat-only screenshots when the runtime can save them safely.
- Use `designforge visual capture` as the canonical handoff from renderer-specific tooling into DesignForge-managed evidence.
- Run `visual capture` only after inspecting the exact artifact being registered; it creates a checked capture row by design.
- Capture only states that materially support verification; do not create large screenshot inventories without decision value.
- A screenshot or video file is evidence that a state was rendered, not proof that the design is correct. Human/agent inspection and findings remain required.
- `pass`, `pass-with-notes`, and `fail` require at least one checked capture backed by an existing non-empty supported image/video artifact.
- `blocked`, `unavailable`, and `pending` must not imply that rendered inspection occurred.
- Use multiple viewports/form factors when responsive or adaptive behavior is in scope.
- Include focus, loading, empty, error, disabled, hover, pressed, selected, or other states only when they are relevant to the changed surface.

## Rules

- Compilation alone is not completion for visual work.
- Do not expand the phase into unrelated redesign work.
- Do not introduce one-off colors, spacing, radii, or component behavior when an active system contract exists.
- If visual tooling is unavailable, say so in `VISUAL_QA.md` and `RESULT.md`; do not claim visual validation occurred.
- Do not register a capture until the referenced render artifact was actually inspected.
- Do not reuse stale render evidence after materially changing the represented UI state.
- Repository reality wins over stale plan text. Repair the plan/state if implementation conditions materially changed.

## Completion

A build phase is complete when:

- requested scope is implemented;
- relevant technical checks pass or failures are explicitly documented;
- rendered UI was inspected with persistent evidence when tooling allowed it;
- renderer output was handed off through managed Visual QA evidence rather than an untracked external path;
- the Visual QA verdict accurately reflects what was and was not inspected;
- material in-scope visual defects were addressed or explicitly remain as blockers/follow-up;
- visual QA mechanical validation passes when a phase `VISUAL_QA.md` is used;
- `RESULT.md` and `STATE.md` match repository reality.
