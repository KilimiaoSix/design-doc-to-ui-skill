# Bento Dashboard

Catalog id: 08
Slug: bento-dashboard
Status: approved
Sample: ../../generated-samples/08-bento-dashboard-style-board.png

## Intent

Modular dashboard style for analytics, operations, finance, product health, and team command centers where users scan mixed information blocks quickly.

## Visual Language

- Asymmetric card grid with varied card sizes.
- Metric tiles, charts, maps, alert cards, lists, and status widgets.
- Clean rounded rectangles, clear spacing, restrained shadows, and strong hierarchy.
- Mostly neutral base with functional blue, green, amber, and red accents.

## Endpoint Adaptation

- Web: executive overview with sidebar, metrics, charts, map card, and ranked lists.
- PC: denser command center with filters, operational map, system health, and alerts.
- Mobile: stacked bento cards with compact charts, alerts, and bottom navigation.
- Tablet: two-column team operations dashboard with task and performance cards.

## Prompt Guidance

Request mixed card sizes and real dashboard modules rather than a uniform grid. Include endpoint-specific density: wide dashboards for Web and PC, stacked cards for Mobile, and two-column bento for Tablet.

## Negative Constraints

Avoid generic card collage, hero layouts, decorative dashboards with fake widgets only, unreadable microtext, and one-note color palettes.

## Risks

- Bento layouts can become visually busy; production versions need a strict grid, content priority rules, and responsive ordering.
- Dense cards require careful text sizing and chart label simplification.
- Status colors need accessible alternatives beyond color alone.
