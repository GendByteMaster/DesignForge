# Workflow: continue

Resume DesignForge work from persistent project state with minimal rediscovery.

## Goal

Continue from repository-backed design state instead of relying on chat history or rebuilding context from scratch, while refusing to silently reuse stale interpreted codebase maps.

## Reads

Always read first:

- `.DesignForge/STATE.md`

Then load only what the active state requires, such as:

- `.DesignForge/PROJECT.md`
- `.DesignForge/DESIGN.md`
- `.DesignForge/DESIGN_SYSTEM.md`
- active phase artifacts
- relevant source files
- relevant `.DesignForge/codebase/*.md` mapping artifacts
- `.DesignForge/codebase/MAP_STATE.md` when mapping freshness matters
- recent repository changes that may invalidate state

## Writes

- `.DesignForge/STATE.md` when stale or after progress
- affected mapping artifacts when a required saved map is stale
- `.DesignForge/codebase/MAP_STATE.md` only after the affected mapping has been revalidated and refreshed
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
4. Determine whether the resumed workflow depends on interpreted codebase mapping such as `STACK.md`, `UI_ARCHITECTURE.md`, `COMPONENTS.md`, `STYLES.md`, `SCREENS.md`, or `CONCERNS.md`.
5. When interpreted mapping is required and `MAP_STATE.md` exists, check freshness before relying on the saved map:

   ```bash
   python designforge/scripts/designforge.py mapping check /path/to/project
   ```

6. If the freshness check is stale:
   - treat the affected saved findings as potentially outdated;
   - inspect the reported source/UI changes;
   - refresh only affected map areas when practical;
   - rerun mapping provenance validation;
   - stamp a new baseline only after the affected findings are current.
7. If interpreted mapping is required but `MAP_STATE.md` does not exist, treat freshness as unknown. For older workspaces, validate the relevant map, inspect its cited sources, and stamp a baseline before treating it as current.
8. Check whether other repository changes since the previous run materially invalidate `STATE.md`, phase plans, design-system assumptions, or implementation notes.
9. If state is stale, repair `STATE.md` from repository reality before continuing.
10. Load only the current phase context and relevant system contracts.
11. Continue from `Next` unless explicit user instructions supersede it.
12. After meaningful progress, update state with the new resume pointer.

## Mapping freshness scope

A failed freshness check is a signal to re-evaluate the affected mapping, not proof that every DesignForge artifact is invalid.

Expected behavior:

- cited source changes invalidate the corresponding mapping baseline;
- changes to interpreted mapping artifacts after stamping invalidate the baseline;
- UI-relevant working-tree or committed changes may invalidate the baseline;
- documentation-only Git drift should not invalidate mapping by itself;
- non-Git projects still receive digest-based freshness checks.

Do not automatically run a mapping freshness check for workflows that do not depend on interpreted mapping. For example, a narrowly scoped phase result or user-provided design decision may remain valid even when the codebase map is stale.

## Rules

- Do not reread the entire `.DesignForge/` tree by default.
- Do not treat chat history as canonical when repository artifacts disagree.
- Repository reality wins over stale `STATE.md` or stale interpreted maps.
- Preserve unresolved blockers; do not silently mark them complete.
- User instructions always override the stored next action.
- Never restamp stale mapping merely to make `mapping check` pass.
- Do not globally invalidate persistent design decisions when only a bounded codebase mapping area changed.

## Completion

The workflow is successful when work resumes from durable project state without unnecessary rediscovery, any required interpreted mapping is known to be current or has been refreshed, and `STATE.md` remains an accurate pointer for the next run.
