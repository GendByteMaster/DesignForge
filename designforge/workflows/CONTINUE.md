# Workflow: continue

Resume DesignForge work from persistent project state with minimal rediscovery.

## Goal

Continue from repository-backed design state instead of relying on chat history or rebuilding context from scratch.

## Reads

Always read first:

- `.DesignForge/STATE.md`

Then load only what the active state requires, such as:

- `.DesignForge/PROJECT.md`
- `.DesignForge/DESIGN.md`
- `.DesignForge/DESIGN_SYSTEM.md`
- active phase artifacts
- relevant source files
- recent repository changes that may invalidate state

## Writes

- `.DesignForge/STATE.md` when stale or after progress
- active phase artifacts as required by the resumed workflow
- product source code only when the resumed workflow requires implementation

## Procedure

1. Read `STATE.md` before broader discovery.
2. Identify:
   - current phase;
   - current workflow;
   - mode;
   - current focus;
   - known blockers;
   - next action.
3. Verify that referenced phase/artifact paths still exist.
4. Check whether repository changes since the previous run materially invalidate the recorded state.
5. If state is stale, repair `STATE.md` from repository reality before continuing.
6. Load only the current phase context and relevant system contracts.
7. Continue from `Next` unless explicit user instructions supersede it.
8. After meaningful progress, update state with the new resume pointer.

## Rules

- Do not reread the entire `.DesignForge/` tree by default.
- Do not treat chat history as canonical when repository artifacts disagree.
- Repository reality wins over stale `STATE.md`.
- Preserve unresolved blockers; do not silently mark them complete.
- User instructions always override the stored next action.

## Completion

The workflow is successful when work resumes from durable project state without unnecessary rediscovery and `STATE.md` remains an accurate pointer for the next run.
