# React Prototype

Default prototype output is a local runnable React frontend project. It must visually recreate the approved AI-generated page images and include the declared interactions.

## Prerequisites

Do not start React implementation until:

- the Design Completion Gate has passed;
- every non-deferred required page has an approved final design image;
- the main-agent audit has passed;
- no style-sampling, page-generation, or regeneration SubAgent is still running;
- the structured design document exists.

Before creating or editing the prototype, run:

```bash
python scripts/validate_design_run.py --run-dir <output-run-dir> --phase design-completion
```

Proceed only when it reports `passed: true` and `react_allowed: true`. Existing manifests may also expose `html_allowed` with the same value.

## Folder Structure

Default output:

```text
prototype/
  package.json
  index.html
  src/
    main.jsx
    prototype-data.js
    styles.css
  assets/
  screens/
  qa/
```

Use `assets/react-prototype-template/` as the starting project when useful.

Generate route/page data with:

```bash
python scripts/build_prototype_data.py --run-dir <output-run-dir> --template react --copy-template
```

The script writes `prototype/src/prototype-data.js` and `prototype/prototype-data-report.json`.

## Runtime Setup

The React prototype is expected to run locally.

- If `node` and `npm` are available in the shell, use them.
- If the local environment lacks Node.js, use the bundled Codex workspace runtime when available.
- If dependencies are missing, run `npm install` in `prototype/`.
- Run the app with `npm run dev -- --host 127.0.0.1` or the command in `package.json`.
- If the requested environment cannot install dependencies or run React, mark the React phase blocked with the exact missing capability.

## Visual Recreation Requirement

The React UI must be rebuilt as components, not shown as full-screen screenshots.

For every required page, use the approved AI page image as the visual source of truth for:

- page frame, status/nav bars, route layout, and scroll behavior;
- card positions, component density, spacing, border radius, shadows, dividers, and background;
- typography scale, weight, alignment, and visible copy language;
- button styles, tab/segmented controls, chips, inputs, dialogs, toasts, and selectors;
- colors, accent use, icon style, mascot/illustration placement, and image-derived decorative elements;
- default, success, error, empty, loading, modal, and blocked states declared in the brief.

Generated page images may be used as:

- visual references in an audit panel;
- thumbnails in the design document;
- cropped/local decorative assets when a specific illustration or mascot cannot be recreated with CSS/React.

Do not use a whole approved UI image as the primary page implementation. A screenshot/image browser is non-compliant even when it has routes or hotspots.

## Interaction Requirement

Implement the interactions declared by page briefs and design documentation:

- route navigation and primary buttons;
- forms, inputs, toggles, selectors, tabs, segmented controls, dialogs, toasts, and simple state changes;
- success, error, empty, loading, modal, blocked, and quota states where specified;
- cross-page paths that match `route_targets` and `prototype_interactions`.

If a visual element exists only in the approved image but not in the page brief, still recreate it visually unless it conflicts with a documented requirement.

## React Visual Parity Gate

After implementation:

1. Start the React dev server locally.
2. Open each required route.
3. Capture a screenshot for each route into `prototype/qa/screenshots/`.
4. Compare each screenshot with the approved AI page image.
5. Record results in `prototype/qa/visual-parity-report.md` or `.json`.

The comparison may be manual, model-assisted, or script-assisted, but the report must name each page and list material differences. Blocking differences include:

- missing or rearranged major sections;
- visual style drift from the approved AI image;
- mismatched nav/status/footer structure;
- important cards, buttons, controls, dialogs, mascot/illustrations, or states missing;
- whole-page image used as the implementation;
- visible copy in the wrong language;
- layout overlap or unreadable text.

Do not mark Final Functional Audit as passed until visual parity is passed or every failure is explicitly blocked with a reason.

Write `prototype/qa/visual-parity-report.md` for human review and `qa/visual-parity-audit.json` for script gates. The JSON audit must include one entry per required page and every `visual_similarity_score` must be at least `0.80`.

## Verification

Before final response:

- Confirm `package.json`, `index.html`, `src/main.jsx`, `src/styles.css`, and `src/prototype-data.js` exist.
- Confirm every non-deferred required page has one route/view in `src/prototype-data.js`.
- Confirm every linked approved AI reference image exists.
- Confirm `prototype/prototype-data-report.json` exists and route count covers all non-deferred required pages.
- Run `npm install` if dependencies are missing.
- Run `npm run build` when feasible.
- Run the React app locally and inspect routes/interactions when browser tools are available.
- Capture or inspect route screenshots and complete the React Visual Parity Gate.
- Confirm `qa/visual-parity-audit.json` exists and every required page has `visual_similarity_score >= 0.80`.
- Report the local folder path, run command, visual parity result, and Final Functional Audit result.
