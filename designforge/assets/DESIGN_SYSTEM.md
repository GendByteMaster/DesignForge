# Design System

## System intent

<!-- Summarize how the design system supports the product experience. -->

## Token architecture

Preferred layering where useful:

`primitive -> semantic -> component`

### Primitive tokens

<!-- Raw scales such as neutral palettes, spacing scales, radius scales, typography sizes, duration values. -->

### Semantic tokens

<!-- Product meaning such as surface.workspace, text.muted, border.subtle, status.danger. -->

### Component tokens

<!-- Use only when a component has a stable need that semantic tokens cannot express cleanly. -->

## Color

<!-- Surface, text, border, accent, status, selected, hover, focus, disabled, and contrast rules. -->

## Typography

<!-- Families, roles, sizes, weights, line heights, hierarchy, truncation/wrapping behavior. -->

## Spacing

<!-- Canonical spacing scale and layout rhythm. Avoid arbitrary one-off values. -->

## Radius and geometry

<!-- Canonical radii and geometry rules; explain where different values are justified. -->

## Borders and elevation

<!-- Border hierarchy, shadow/elevation levels, overlays, separators, and depth strategy. -->

## Layout

<!-- Shell, content widths, grids, panes, navigation, density, overflow, and responsive transitions. -->

## Components

For each component that the product actually needs, define relevant aspects:

- role;
- anatomy;
- variants;
- sizes;
- interaction states;
- focus behavior;
- disabled/loading behavior;
- keyboard behavior;
- responsive behavior;
- motion;
- accessibility requirements.

Prefer implementation primitives in this order:

`platform/native primitive -> existing project component -> existing accessible UI library -> accessible headless primitive -> custom component`

## Patterns

<!-- Reusable interaction patterns: navigation, forms, overlays, empty states, feedback, tables/trees, command surfaces, etc. -->

## Motion

<!-- Duration scale, easing, enter/exit rules, state transitions, layout motion, and reduced-motion behavior. -->

## Responsive behavior

<!-- Breakpoint intent, priority changes, navigation transformations, compression rules, overflow strategy, touch/keyboard differences. -->

## Accessibility contract

<!-- Project-specific semantics, focus, keyboard, target size, contrast, error/status communication, reduced motion, and screen-reader requirements. -->

## Drift rules

<!-- Define what should be considered a design-system violation in this project. -->

## Detailed references

<!-- Link to additional `.DesignForge/system/*.md` artifacts only when needed. -->
