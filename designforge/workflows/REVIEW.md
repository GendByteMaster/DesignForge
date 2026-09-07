# Workflow: review

Inspect implemented UI against the active design direction, system contracts, and product constraints without expanding scope unnecessarily.

## Goal

Produce evidence-based findings that distinguish blocking defects, meaningful design regressions, and minor polish issues, with persistent rendered evidence whenever visual review is claimed.

## Reads

- `.DesignForge/STATE.md`
- `.DesignForge/DESIGN.md`
- `.DesignForge/DESIGN_SYSTEM.md`
- relevant `.DesignForge/system/` artifacts
- active phase `PLAN.md`, `DESIGN.md`, `RESULT.md`, and `VISUAL_QA.md` when present
- product-wide `.DesignForge/reviews/VISUAL_QA.md` when reviewing across phases
- relevant `visual-evidence/` artifacts
- affected source files
- rendered UI or screenshots when tooling allows

## Writes

- active phase `.DesignForge/phases/<phase>/VISUAL_QA.md`, or product-wide `.DesignForge/reviews/VISUAL_QA.md` when visual review applies
- corresponding `visual-evidence/*` artifacts when new captures are produced
- active phase `.DesignForge/phases/<phase>/REVIEW.md`, or
- product-wide `.DesignForge/reviews/*.md`
- `.DesignForge/STATE.md` when review changes the next action

## Review dimensions

Evaluate only dimensions relevant to the surface:

- information hierarchy;
- layout and alignment;
- spacing rhythm;
- typography;
- color and contrast;
- density;
- component consistency;
- interaction states;
- focus and keyboard behavior;
- responsive behavior;
- clipping and overflow;
- accessibility;
- motion;
- design-system compliance;
- fidelity to Design DNA.

## Procedure

1. Read `STATE.md` and determine review scope.
2. Load only relevant design/system contracts.
3. Inspect implementation code for obvious contract violations.
4. Decide whether this is phase-scoped or product-wide visual review.
5. When rendered inspection is possible and no suitable Visual QA artifact exists, initialize one:

   Phase-scoped:

   ```bash
   python designforge/scripts/designforge.py visual init /path/to/project --phase <phase>
   ```

   Product-wide:

   ```bash
   python designforge/scripts/designforge.py visual init /path/to/project
   ```

6. Reuse existing persistent render evidence only when it still represents the implementation being reviewed. Otherwise create a fresh screenshot/video with whatever browser, emulator, simulator, preview, screenshot, native-app, or equivalent tooling the current runtime provides.
7. Inspect the exact render before registering it as checked evidence. A checked row is a claim that this output was actually reviewed.
8. After inspection, import the render and register it through the public DesignForge capture handoff.

   Phase-scoped:

   ```bash
   python designforge/scripts/designforge.py visual capture /tmp/render.png /path/to/project \
     --surface "Main Workspace" \
     --state "default" \
     --viewport "1440x900" \
     --phase <phase>
   ```

   Product-wide:

   ```bash
   python designforge/scripts/designforge.py visual capture /tmp/render.png /path/to/project \
     --surface "Application Shell" \
     --state "default" \
     --viewport "1440x900"
   ```

   The handoff validates media type/signature, copies external evidence into the correct managed `visual-evidence/` directory without overwriting existing captures, and creates the checked capture-matrix row. Do not call it for an artifact that has not actually been inspected.
9. Record visual and accessibility observations in `VISUAL_QA.md`. Record actionable defects in `REVIEW.md` with evidence and impact.
10. Classify defect severity:
    - `blocker` — prevents correct use, accessibility, or intended workflow;
    - `major` — materially harms hierarchy, consistency, responsiveness, or design direction;
    - `minor` — limited polish issue;
    - `note` — observation or future improvement.
11. Prefer concrete statements such as "Toolbar action spacing uses three unrelated values" over vague judgments such as "looks inconsistent".
12. Recommend the smallest effective fix.
13. Set the Visual QA verdict through the public CLI:

   Phase-scoped:

   ```bash
   python designforge/scripts/designforge.py visual verdict pass /path/to/project --phase <phase>
   ```

   Product-wide:

   ```bash
   python designforge/scripts/designforge.py visual verdict pass /path/to/project
   ```

   Valid verdicts are:
   - `pass` — inspected required states have no material visual defect;
   - `pass-with-notes` — inspected states are acceptable with documented non-blocking observations;
   - `fail` — inspected evidence shows unresolved material defects;
   - `blocked` — visual review is expected but blocked by an environment/product condition;
   - `unavailable` — suitable rendered evidence cannot be produced or accessed in the current runtime;
   - `pending` — review has not been completed.

   `visual verdict` validates the updated contract and rolls the status change back when a conclusive verdict is not supported by inspected evidence.
14. Validate the mechanical evidence contract:

   Phase-scoped:

   ```bash
   python designforge/scripts/designforge.py visual validate /path/to/project --phase <phase>
   ```

   Product-wide:

   ```bash
   python designforge/scripts/designforge.py visual validate /path/to/project
   ```

15. If validation fails, fix the evidence contract or verdict rather than weakening the validator. Mechanical validation confirms managed artifact existence, signatures, and traceability; it does not judge visual quality.
16. Do not rewrite unrelated code as part of review.
17. Update `STATE.md` if blockers or required follow-up change the next workflow.

## Visual evidence rules

- Do not claim visual review if no rendered output was inspected.
- Use `designforge visual capture` as the canonical renderer-to-DesignForge evidence handoff.
- Run `visual capture` only after inspecting the exact supplied artifact because registration creates a checked row.
- `pass`, `pass-with-notes`, and `fail` require at least one checked capture backed by an existing non-empty supported render artifact.
- `pending`, `blocked`, and `unavailable` must not imply rendered inspection occurred.
- Prefer persistent project-relative render evidence over chat-only screenshots when the runtime can save artifacts safely.
- User-provided screenshots may inform a review, but when a persistent DesignForge verdict depends on them, store an approved project-local equivalent when practical or record the limitation explicitly.
- Do not reuse a capture after the represented UI state materially changed.
- A render artifact proves that a state was captured, not that the design is correct. Findings still require inspection and reasoning.
- Capture only states that matter to the review. Do not create large screenshot inventories for completeness alone.

## Rules

- Design preference alone is not a defect unless it conflicts with product intent or the active system.
- Preserve intentional platform conventions.
- Avoid duplicate findings across phase and product-wide review artifacts.
- Never manufacture an evidence path or register an uninspected capture.
- If rendering is unavailable, use an honest `blocked`, `unavailable`, or `pending` verdict and state what could not be verified.

## Completion

Review is complete when:

- findings are prioritized, evidence-based, actionable, and clear enough that a build workflow can resolve them without reinterpreting the entire design direction;
- any claimed rendered inspection is represented by checked persistent evidence imported through the managed Visual QA contract;
- the Visual QA verdict matches what was actually inspected;
- visual QA mechanical validation passes when a `VISUAL_QA.md` artifact is used;
- unavailable or blocked visual states are explicitly recorded rather than silently assumed correct.
