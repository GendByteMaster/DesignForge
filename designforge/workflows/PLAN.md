# Workflow: plan

Turn the active design direction into a bounded implementation roadmap and phase plan.

## Goal

Create an implementation sequence that preserves design coherence, respects dependencies, and makes visual verification possible at each meaningful step.

## Reads

- `.DesignForge/PROJECT.md`
- `.DesignForge/STATE.md`
- `.DesignForge/DESIGN.md`
- `.DesignForge/DESIGN_SYSTEM.md` when available
- relevant `.DesignForge/codebase/` artifacts
- active phase context when replanning

## Writes

- `.DesignForge/ROADMAP.md`
- `.DesignForge/phases/<phase>/CONTEXT.md` when useful
- `.DesignForge/phases/<phase>/PLAN.md`
- `.DesignForge/phases/<phase>/DESIGN.md` when phase-specific design decisions are needed
- `.DesignForge/STATE.md`

## Procedure

1. Load the active redesign mode and current state.
2. Identify structural dependencies before visual polish dependencies.
3. Derive phases from the actual product architecture and user workflows.
4. Prefer high-leverage foundations first when appropriate:
   - application shell;
   - navigation;
   - token/system foundations;
   - core reusable primitives;
   - highest-value workflow surfaces.
5. Avoid a generic fixed roadmap when the product does not need it.
6. For each phase, define:
   - intended outcome;
   - scope;
   - dependencies;
   - affected UI areas;
   - design-system impact;
   - accessibility concerns;
   - responsive concerns;
   - implementation checks;
   - visual review expectations;
   - completion criteria.
7. Keep phases small enough to implement and visually inspect without mixing unrelated redesign concerns.
8. Record explicit user decisions in `CONTEXT.md` rather than burying them in the plan.
9. Set one active phase in `STATE.md` and define the next workflow, usually `build`.

## Rules

- Plan from product workflows and UI architecture, not from file count.
- Do not schedule decorative polish before unresolved structure or hierarchy.
- Do not create unnecessary phase documents.
- Every visual phase must have a verification strategy.
- Replanning must preserve completed work unless the new direction intentionally supersedes it.

## Completion

Planning is complete when:

- `ROADMAP.md` reflects the actual product;
- one phase is clearly active;
- the active phase has a bounded implementation plan;
- dependencies and verification are explicit;
- `STATE.md` points to the next concrete action.
