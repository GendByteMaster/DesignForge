# Workflow: review

Inspect implemented UI against the active design direction, system contracts, and product constraints without expanding scope unnecessarily.

## Goal

Produce evidence-based findings that distinguish blocking defects, meaningful design regressions, and minor polish issues.

## Reads

- `.DesignForge/STATE.md`
- `.DesignForge/DESIGN.md`
- `.DesignForge/DESIGN_SYSTEM.md`
- relevant `.DesignForge/system/` artifacts
- active phase `PLAN.md`, `DESIGN.md`, and `RESULT.md` when present
- affected source files
- rendered UI or screenshots when tooling allows

## Writes

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
- accessibility;
- motion;
- design-system compliance;
- fidelity to Design DNA.

## Procedure

1. Read `STATE.md` and determine review scope.
2. Load only relevant design/system contracts.
3. Inspect implementation code for obvious contract violations.
4. Render or inspect screenshots when visual tooling exists.
5. Record findings with evidence and impact.
6. Classify severity:
   - `blocker` — prevents correct use, accessibility, or intended workflow;
   - `major` — materially harms hierarchy, consistency, responsiveness, or design direction;
   - `minor` — limited polish issue;
   - `note` — observation or future improvement.
7. Prefer concrete statements such as "Toolbar action spacing uses three unrelated values" over vague judgments such as "looks inconsistent".
8. Recommend the smallest effective fix.
9. Do not rewrite unrelated code as part of review.
10. Update `STATE.md` if blockers or required follow-up change the next workflow.

## Rules

- Do not claim visual review if no rendered output was inspected.
- Design preference alone is not a defect unless it conflicts with product intent or the active system.
- Preserve intentional platform conventions.
- Avoid duplicate findings across phase and product-wide review artifacts.

## Completion

Review is complete when findings are prioritized, evidence-based, actionable, and clear enough that a build workflow can resolve them without reinterpreting the entire design direction.
