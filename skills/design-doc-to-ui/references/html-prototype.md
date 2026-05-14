# HTML Prototype

Default output is a local component-level interactive prototype folder.

## Prerequisites

Do not start HTML implementation until:

- the Design Completion Gate has passed;
- every non-deferred required page has an approved final design image;
- the main-agent audit has passed;
- no style-sampling, page-generation, or regeneration SubAgent is still running;
- the structured design document exists.

Build the HTML prototype from the approved design images, structured design document, page briefs, and worker reviews. Do not build HTML from requirements alone while design images are still pending. If any required design image is missing or unapproved, stop and report the HTML phase as blocked unless the user explicitly approves a partial prototype.

Before creating or editing HTML, run:

```bash
python scripts/validate_design_run.py --run-dir <output-run-dir> --phase design-completion
```

Proceed only when it reports `passed: true` and `html_allowed: true`.

After HTML generation and verification, update the structured design document with the local prototype path and Final Functional Audit result.

## Folder Structure

```text
prototype/
  index.html
  assets/
  screens/
  styles.css
  prototype-data.js
```

## Default Interactive Prototype

Default behavior:

- Build real HTML/CSS/JS components for each generated page.
- Use `prototype-data.js` to define routes, copy, sections, controls, actions, states, and optional visual-reference thumbnails.
- Implement a route/view for every non-deferred required page.
- Implement page navigation, primary buttons, form controls, selectors, tabs, dialogs, success/error/empty/loading/blocked states, and any interactions declared in page briefs.
- Use generated UI images only as reference thumbnails or review attachments. Do not use full-screen images as the main UI.
- Set HTML `lang`, document title, navigation labels, metadata, and visible prototype UI copy from `requested_output_language`.
- Keep source screenshots in `prototype/screens/` only when they help reviewers compare visual direction.

The prototype is non-compliant if it only switches whole-page screenshots with buttons or hotspots. If that is the only possible output, mark the HTML phase `blocked/non-compliant` and do not call the delivery complete.

## Implementation Notes

- Copy `assets/html-prototype-template/` as the starting point when useful.
- Generate or verify `prototype-data.js` with `scripts/build_prototype_data.py --run-dir <output-run-dir> --copy-template`.
- Replace or extend generated page data only with data derived from the structured design document, approved design images, page briefs, and worker results.
- Add custom CSS only when needed for the selected product style; keep the route and interaction behavior intact.
- Keep all visible default labels in `requested_output_language`.
- Build from the completed design package. The approved UI images should guide spacing, hierarchy, and style, while the structured design document should guide routes, copy, states, and interaction behavior.

## Verification

Before final response:

- Confirm `index.html`, `styles.css`, and `prototype-data.js` exist.
- Confirm every non-deferred required page has one route/view in `prototype-data.js`.
- Confirm every linked reference image exists.
- Confirm `prototype/prototype-data-report.json` exists and route count covers all non-deferred required pages.
- Open or inspect the prototype if browser tools are available.
- Click or inspect primary actions, navigation, controls, dialogs, and declared states.
- Confirm the prototype is not a full-screen image browser.
- Report the local folder path and Final Functional Audit result.
