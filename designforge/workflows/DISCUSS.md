# Workflow: discuss

Capture durable design decisions, constraints, preferences, and rejected directions before implementation work proceeds.

## Goal

Move important context out of transient chat history and into project-local DesignForge artifacts.

## Reads

- `.DesignForge/PROJECT.md`
- `.DesignForge/STATE.md`
- `.DesignForge/DESIGN.md` when present
- active phase context when present
- explicit user instructions and decisions

## Writes

Depending on scope:

- `.DesignForge/PROJECT.md`
- `.DesignForge/DESIGN.md`
- `.DesignForge/phases/<phase>/CONTEXT.md`
- `.DesignForge/STATE.md`

## Procedure

1. Identify which decisions are product-wide and which are phase-specific.
2. Extract explicit user decisions, including:
   - desired redesign freedom;
   - non-negotiable behavior;
   - platform constraints;
   - interaction preferences;
   - accessibility requirements;
   - references the user wants to use;
   - references or styles the user explicitly rejects;
   - areas that may or may not be restructured.
3. Store product-wide facts in `PROJECT.md`.
4. Store global visual/UX direction decisions in `DESIGN.md`.
5. Store phase-specific decisions in `phases/<phase>/CONTEXT.md`.
6. Distinguish confirmed decisions from assumptions.
7. Remove or supersede stale statements when the user changes direction.
8. Update `STATE.md` if the next workflow or active focus changes.

## Rules

- Do not turn temporary implementation details into permanent design principles.
- Do not preserve contradictory decisions without marking which one supersedes the other.
- Do not invent preferences that the user did not state and the repository does not imply.
- Keep phase context focused enough that a new agent can recover the decision without rereading chat history.

## Completion

Discussion capture is complete when the decisions that would materially affect later design or implementation are represented in durable project artifacts and the next workflow is clear.
