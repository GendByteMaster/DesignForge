# Workflow: init

Initialize DesignForge in a target software project.

## Goal

Create the smallest trustworthy `.DesignForge/` state required to continue design work across sessions.

## Reads

- repository root documentation;
- package/project manifests;
- existing design-system or UI documentation when obvious;
- existing `.DesignForge/` files if present.

## Writes

At minimum:

- `.DesignForge/PROJECT.md`
- `.DesignForge/STATE.md`

Create additional artifacts only when they are immediately useful.

## Procedure

1. Detect whether the target is greenfield or an existing product.
2. Detect platform, framework, and obvious UI stack without performing a full codebase audit.
3. Determine the redesign freedom mode:
   - `conservative`
   - `refactor`
   - `reimagine`
4. If the user explicitly chose a mode, preserve it.
5. Otherwise infer the least destructive mode that can satisfy the request and record the assumption.
6. Create `.DesignForge/` if it does not exist.
7. Populate `PROJECT.md` from repository evidence and user instructions.
8. Populate `STATE.md` with:
   - current workflow: `init`;
   - current status;
   - selected mode;
   - completed initialization work;
   - current focus;
   - blockers or unresolved assumptions;
   - next workflow.
9. If the product already has a UI, set the next workflow to `map` unless a narrower task makes mapping unnecessary.
10. If the product is greenfield, usually set the next workflow to `direct` after product context is sufficient.

## Rules

- Do not scaffold every `.DesignForge/` file up front.
- Do not invent product facts that repository evidence does not support.
- Record unresolved assumptions instead of silently treating them as facts.
- User instructions override defaults in this workflow.
- Keep `STATE.md` concise.

## Completion

Initialization is complete when:

- `PROJECT.md` exists and captures the known product context;
- `STATE.md` exists and points to a concrete next workflow;
- selected redesign mode is recorded;
- unresolved assumptions are visible.
