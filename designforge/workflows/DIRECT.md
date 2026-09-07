# Workflow: direct

Create or refine the product-specific visual and UX direction.

## Goal

Produce a coherent design thesis and Design DNA that can guide systemization, planning, implementation, and review.

## Reads

- `.DesignForge/PROJECT.md`
- `.DesignForge/STATE.md`
- relevant `.DesignForge/codebase/` artifacts for existing products
- relevant `.DesignForge/research/` artifacts
- user-provided references, screenshots, or constraints

## Writes

- `.DesignForge/DESIGN.md`
- relevant `.DesignForge/research/REFERENCES.md` when reference analysis is material
- `.DesignForge/STATE.md`

## Procedure

1. Load product purpose, users, key workflows, platform, mode, and non-negotiable behavior.
2. For existing products, load only mapped UI concerns that materially affect the direction.
3. Identify the experience qualities required by the product, not by trend.
4. Internally evaluate more than one plausible direction when useful, but do not burden the user with superficial style choices.
5. Select or refine one direction based on product fit.
6. Write a concise design thesis.
7. Define Design DNA using explicit axes:
   - density;
   - geometry;
   - contrast;
   - depth;
   - typography character;
   - motion character;
   - chrome;
   - color character;
   - information hierarchy;
   - interaction character.
8. Define visual hierarchy, layout philosophy, responsive philosophy, and accessibility implications.
9. Define explicit anti-patterns and originality constraints.
10. If references are used, extract principles and adaptation rationale; never write instructions to clone a named product.
11. Update `STATE.md` with the active direction status and next workflow.

## Rules

- Originality must be explainable from product context.
- Do not default to generic SaaS dashboards, excessive cards, gradients, glassmorphism, oversized typography, or decorative animation.
- Named products and platform guidelines are references for principles, not visual templates.
- Accessibility and platform conventions constrain the direction.
- The selected redesign mode determines how much existing UX structure may be changed.

## Completion

Direction is complete when `DESIGN.md` is specific enough that two independent agents should make broadly compatible choices about hierarchy, density, geometry, color, typography, motion, and interaction style.
