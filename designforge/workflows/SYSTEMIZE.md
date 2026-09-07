# Workflow: systemize

Translate the active design direction into implementation-ready design-system contracts.

## Goal

Prevent ad hoc styling during implementation by defining the minimum coherent system the product needs.

## Reads

- `.DesignForge/PROJECT.md`
- `.DesignForge/STATE.md`
- `.DesignForge/DESIGN.md`
- relevant `.DesignForge/codebase/` artifacts
- existing project design-system files and UI libraries

## Writes

- `.DesignForge/DESIGN_SYSTEM.md`
- relevant `.DesignForge/system/*.md` artifacts
- `.DesignForge/STATE.md`

## Procedure

1. Load the active design thesis and Design DNA.
2. Identify which design-system domains are necessary for the product.
3. Reuse existing valid project tokens and accessible primitives where possible.
4. Define token architecture, preferring:
   - primitive;
   - semantic;
   - component only where necessary.
5. Define relevant domains:
   - color;
   - typography;
   - spacing;
   - radius/geometry;
   - borders;
   - elevation;
   - opacity;
   - motion;
   - breakpoints;
   - layout;
   - components;
   - patterns;
   - accessibility.
6. For each required component, define only the relevant contract details:
   - role;
   - anatomy;
   - variants;
   - size;
   - states;
   - focus behavior;
   - disabled/loading behavior;
   - keyboard behavior;
   - responsive behavior;
   - motion;
   - accessibility.
7. Prefer implementation primitives in this order:
   `platform/native -> existing project component -> existing accessible UI library -> accessible headless primitive -> custom component`.
8. Define drift rules that later `guard` reviews can enforce.
9. Update `STATE.md` with systemization status and next workflow.

## Rules

- Do not create tokens or variants that have no product use.
- Do not introduce a parallel component system without a documented reason.
- Do not encode arbitrary visual preferences as universal rules.
- Preserve valid platform conventions and accessibility behavior.
- The system must reflect `DESIGN.md`; it must not invent a competing aesthetic.

## Completion

Systemization is complete when implementation can proceed without repeatedly inventing colors, spacing, geometry, component states, motion, or accessibility behavior ad hoc.
