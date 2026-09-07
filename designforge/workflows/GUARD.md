# Workflow: guard

Review recent or proposed UI changes for design-system drift and contract violations.

## Goal

Protect a project from gradual visual inconsistency without turning DesignForge into a generic style linter.

## Reads

- `.DesignForge/DESIGN.md`
- `.DesignForge/DESIGN_SYSTEM.md`
- relevant `.DesignForge/system/` artifacts
- `.DesignForge/STATE.md`
- changed UI/source files or diff
- rendered output when useful and available

## Writes

- `.DesignForge/reviews/DRIFT.md` or active phase `REVIEW.md`
- `.DesignForge/STATE.md` only if findings create a blocker or required next action

## Detect

Look for evidence of:

- hardcoded colors where semantic tokens already exist;
- one-off spacing, radius, elevation, typography, or motion values outside the active system;
- duplicated components or parallel primitives;
- custom controls that reduce accessibility compared with existing primitives;
- new dialog/menu/popover systems without justification;
- inconsistent interaction states;
- broken responsive rules;
- reduced-motion regressions;
- new decorative gradients, glass, shadows, or animation that conflict with `DESIGN.md`;
- changes that weaken established hierarchy or Design DNA;
- implementation that bypasses documented component contracts.

## Procedure

1. Determine the change scope from the current diff or files under review.
2. Load only design/system contracts relevant to those files.
3. Separate true contract violations from intentional exceptions.
4. Record each finding with:
   - evidence;
   - violated contract or principle;
   - impact;
   - recommended smallest effective fix;
   - severity.
5. Use severity:
   - `blocker` — accessibility, core interaction, or serious system break;
   - `major` — material drift that should be fixed before merge;
   - `minor` — low-impact inconsistency;
   - `note` — justified exception or follow-up opportunity.
6. If an exception is intentional and reasonable, recommend documenting it rather than forcing conformity.
7. Avoid rewriting unrelated code.

## Rules

- Guard is evidence-based, not taste-based.
- Do not flag a value merely because it is uncommon if the design system permits it.
- Do not force tokenization or abstraction where it adds complexity without reuse or semantic value.
- Accessibility regressions outrank cosmetic consistency issues.
- Existing system rules may be revised if the product direction intentionally evolves; guard should not freeze a bad system forever.

## Completion

Guard is complete when changed UI can be classified as compliant, intentionally exceptional, or requiring concrete fixes before the next workflow/merge step.
