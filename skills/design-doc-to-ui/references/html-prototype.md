# React Prototype

Default prototype output is a local runnable React frontend project. It must basically replicate the approved AI-generated page images and include the declared interactions. Treat this as a formal frontend demo, not a clickable image mockup.

## Prerequisites

Do not start React implementation until:

- the Design Completion Gate has passed;
- every non-deferred required page has an approved final design image;
- the main-agent audit has passed;
- no style-sampling, page-generation, or regeneration SubAgent is still running;
- the structured design document exists;
- `qa/structured-design-doc-audit.json` has passed.

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
    react-scaffold-audit.json
    react-page-worker-registry.json
    react-navigation-audit.json
    react-usability-audit.json
    react-worker-result.json
    react-interaction-audit.json
    react-page-workers/
      <page_id>/
        visual-decomposition.json
        dom-element-inventory.json
        visual-replica-audit.json
```

Use `assets/react-prototype-template/` as the starting project when useful.

Generate route/page data with:

```bash
python scripts/build_prototype_data.py --run-dir <output-run-dir> --template react --copy-template
```

The script writes `prototype/src/prototype-data.js` and `prototype/prototype-data-report.json`.

## Process Management Files

React prototype work must be managed through intermediate files, not only a final demo folder. Treat these files as the React equivalent of page-image worker outputs in `ui-run.json`:

- `prototype/prototype-data-report.json`: route/page source of truth generated from the approved page inventory.
- `prototype/qa/react-scaffold-audit.json`: main-agent scaffold, style system, route registry, page slots, and ownership map.
- `prototype/qa/react-page-worker-registry.json`: main-thread registry of every React page worker result.
- `prototype/qa/react-page-workers/<page_id>/worker-result.json`: page worker implementation result.
- `prototype/qa/react-page-workers/<page_id>/visual-decomposition.json`: page worker's structured decomposition of the approved AI image before implementation.
- `prototype/qa/react-page-workers/<page_id>/dom-element-inventory.json`: implemented DOM/component inventory mapped back to the visual decomposition.
- `prototype/qa/react-page-workers/<page_id>/visual-replica-audit.json`: page-local screenshot-to-approved-image audit after implementation.
- `prototype/qa/react-page-workers/<page_id>/interaction-audit.json`: page-local interaction audit.
- `prototype/qa/react-page-workers/<page_id>/review.md`: page worker self-review and repair notes.
- `prototype/qa/react-navigation-audit.json`: main-agent global navigation, route target, cross-page state, and recovery-flow audit.
- `prototype/qa/react-usability-audit.json`: main-agent demo usability audit for right-side page switching, scrollability, and content reachability.
- `prototype/qa/react-worker-result.json`: aggregate implementation result.
- `prototype/qa/react-interaction-audit.json`: aggregate interaction and whole-flow audit.
- `qa/visual-parity-audit.json`: visual parity gate against approved design images.

After each React page worker returns, register it from the main thread:

```bash
python scripts/record_react_page_worker_result.py \
  --run-dir <output-run-dir> \
  --page-id <page_id> \
  --worker-result prototype/qa/react-page-workers/<page_id>/worker-result.json \
  --interaction-audit prototype/qa/react-page-workers/<page_id>/interaction-audit.json \
  --visual-decomposition prototype/qa/react-page-workers/<page_id>/visual-decomposition.json \
  --dom-inventory prototype/qa/react-page-workers/<page_id>/dom-element-inventory.json \
  --visual-replica-audit prototype/qa/react-page-workers/<page_id>/visual-replica-audit.json \
  --review prototype/qa/react-page-workers/<page_id>/review.md
```

The registry must contain one passing page entry per non-deferred required page before the main agent writes aggregate React results.

## Main-Agent React Scaffold Gate

Before starting page-level React workers, the main agent must create the shared React scaffold that all workers will build inside. This is a main-agent responsibility because it sets product-level style, prevents page workers from drifting into unrelated designs, and establishes the route contract before parallel page work begins.

The scaffold must include:

- app shell and route registry based on `prototype/src/prototype-data.js`;
- stable page slots or page modules for every non-deferred required route;
- shared layout primitives, base components, CSS variables/tokens, typography, spacing, radius, color, and interaction state conventions;
- responsive constraints and shared navigation patterns;
- a right-side demo page switcher outside the replicated page frame, covering every required route without affecting visual parity screenshots;
- a scroll container contract that prevents accidental page/body scroll lock and defines how long pages handle wheel, trackpad, and touch scrolling;
- page worker ownership map showing which files each worker may edit;
- integration contract for outbound route targets and shared state.

Write `prototype/qa/react-scaffold-audit.json` before starting page workers:

```json
{
  "passed": true,
  "app_shell_created": true,
  "route_registry_created": true,
  "style_system_locked": true,
  "page_slots_created": true,
  "demo_route_switcher_created": true,
  "route_switcher_covers_all_pages": true,
  "route_switcher_outside_replica_frame": true,
  "scroll_container_contract_created": true,
  "body_or_page_scroll_not_blocked": true,
  "worker_ownership_map_created": true,
  "shared_navigation_contract_created": true,
  "required_page_count": 7,
  "page_slots": [
    {
      "page_id": "home",
      "route": "#home",
      "owned_files": ["prototype/src/pages/Home.jsx"]
    }
  ],
  "hard_failures": []
}
```

Do not start React page workers until this audit exists and has `passed: true`. Page workers must use the scaffold, style tokens, and owned file map instead of creating their own global layout or style system.

The right-side page switcher is demo chrome, not part of the replicated product page. It must sit outside the phone/page frame on desktop or collapse into a non-obstructive menu on narrow screens. It must be excluded from page visual parity screenshots by capturing only the replica frame or by marking demo chrome with a stable selector such as `data-demo-chrome="true"`.

## React Page Worker Gate

After prototype data is generated and `prototype/qa/react-scaffold-audit.json` has passed, start one page-level React SubAgent per non-deferred required page using `references/react-prototype-worker-prompt.md`.

Run page workers in batches with at most 6 active SubAgents across the whole design-doc-to-ui run. A page worker owns exactly one route/page and its local states/interactions. It must not own unrelated pages or global router logic.

Each page worker must implement its assigned page as a real component-level frontend slice:

- read the original requirements/source bundle, approved AI page images, page briefs, structured design document, style contract, worker reviews, main audit, and generated prototype data;
- read `prototype/qa/react-scaffold-audit.json`, shared style tokens/CSS, route registry, and the worker ownership map;
- before writing page UI code, create `visual-decomposition.json` from the approved AI image and list every visible section, card, control, icon group, illustration, decorative stroke, nav/status area, copy block, and nonstandard layout;
- implement the assigned route/view from `prototype/src/prototype-data.js`;
- work only inside the assigned page slot and owned files unless the main agent explicitly grants shared-file ownership;
- follow the main-agent style system and page frame instead of redefining product-level visual direction;
- implement page-local interactions according to the original requirements and structured design document, not only the visual image;
- after implementation, create `dom-element-inventory.json` mapping every decomposed visual element to a React component, DOM node, CSS construction, SVG/vector, or isolated asset;
- render the assigned route, compare it with the approved AI image, and create `visual-replica-audit.json` before claiming page completion;
- test the assigned route and page-local interaction states locally;
- verify wheel/trackpad scrolling, touch-style scrolling when feasible, bottom-content reachability, and absence of accidental scroll lock for the assigned route;
- record outbound route targets and shared state dependencies for main-agent integration;
- repair visual and behavioral issues before returning;
- write `prototype/qa/react-page-workers/<page_id>/worker-result.json`, `prototype/qa/react-page-workers/<page_id>/interaction-audit.json`, and `prototype/qa/react-page-workers/<page_id>/review.md`.

After all page workers return, the main agent owns:

- shared app shell, shared components, and route table integration;
- cross-page state, navigation guards, back/retry/recovery routes, and handoff between pages;
- whole-product flow verification;
- `prototype/qa/react-navigation-audit.json`;
- `prototype/qa/react-usability-audit.json`;
- aggregate `prototype/qa/react-worker-result.json` and `prototype/qa/react-interaction-audit.json`.

Do not mark the React phase complete from the main thread alone. If React page SubAgent capability is technically unavailable, mark React prototype generation blocked. Do not replace required page workers with a quick main-thread implementation.

React page workers must not edit `ui-run.json`, page briefs, design image worker outputs, unrelated routes, or unrelated files.

## Scrollability And Demo Navigation Gate

Every React demo must be usable before it is visually polished. A page that cannot scroll, clips bottom content, or traps the user above hidden content is non-compliant even if the first viewport looks close to the approved image.

Main-agent scaffold requirements:

- provide a right-side page switcher listing every non-deferred required route;
- route switcher buttons must navigate to the corresponding route and show the active page;
- the switcher must be outside the replicated page frame or excluded from visual parity screenshots;
- each route must have a defined scroll container contract;
- do not set `overflow: hidden` on `body`, root, or page containers unless an inner, tested scroll container handles all page scrolling;
- fixed headers, bottom navs, and floating controls must not cover final content.

Each page worker must verify:

- wheel/trackpad scroll changes scroll position when content exceeds the viewport;
- touch-style scrolling works where browser tooling can simulate it;
- the last meaningful content row/card/button is reachable;
- bottom navigation or fixed call-to-action areas do not hide content;
- scroll restoration or page switching does not leave the page in a broken scroll position.

The main agent must write `prototype/qa/react-usability-audit.json`:

```json
{
  "passed": true,
  "right_side_page_menu_present": true,
  "page_menu_position": "right",
  "page_menu_outside_replica_frame": true,
  "page_menu_covers_all_routes": true,
  "page_menu_route_switching_passed": true,
  "page_menu_does_not_affect_visual_parity": true,
  "scroll_behavior_passed": true,
  "all_scrollable_pages_verified": true,
  "no_page_scroll_locked": true,
  "fixed_navigation_does_not_hide_content": true,
  "page_scroll_results": [
    {
      "page_id": "",
      "route": "",
      "expected_scrollable": true,
      "wheel_scroll_passed": true,
      "touch_scroll_passed": true,
      "bottom_content_reachable": true,
      "content_not_clipped": true,
      "fixed_ui_not_obscuring_content": true,
      "notes": ""
    }
  ],
  "hard_failures": []
}
```

Do not mark React complete when any required page has inaccessible lower content, when wheel/touch scrolling is broken, or when the route switcher cannot navigate to every required page.

## Page Visual Decomposition Gate

The page worker must analyze the approved AI image before coding. This is not optional, because a React page can otherwise satisfy requirements while silently replacing the approved design with a generic layout.

`visual-decomposition.json` must include:

```json
{
  "passed": true,
  "page_id": "",
  "approved_image": "",
  "approved_image_analyzed": true,
  "all_major_regions_listed": true,
  "all_visible_controls_listed": true,
  "nonstandard_layouts_identified": true,
  "must_not_simplify_rules_created": true,
  "screen_regions": [
    {
      "region_id": "top-status-and-title",
      "type": "status_bar|nav|filter_group|card|graph|task_list|bottom_nav|illustration|decorative",
      "position": "top|middle|bottom",
      "visual_notes": "",
      "visible_copy": [],
      "must_replicate": true
    }
  ],
  "element_inventory": [
    {
      "element_id": "",
      "region_id": "",
      "kind": "text|button|chip|icon|card|divider|progress|avatar|illustration|connector|tab|task-row",
      "visual_role": "",
      "copy_or_icon": "",
      "must_replicate": true
    }
  ],
  "nonstandard_layouts": [
    {
      "layout_id": "",
      "description": "",
      "must_not_replace_with": "generic grid/list/card"
    }
  ],
  "hard_failures": []
}
```

For example, if the approved image contains a knowledge-tree graph with connectors, branch cards, icons, and playful marks, the React page must recreate that graph structure. Replacing it with a two-column button grid is a hard failure. If the approved image has top status chips, a progress mascot, a daily-task card, handwritten decorative lines, or a four-item bottom navigation, those visible elements must be represented unless a documented approved revision removes them.

## DOM Inventory And Visual Replica Gate

After coding, the page worker must map the implementation back to the image decomposition:

```json
{
  "passed": true,
  "page_id": "",
  "all_required_sections_implemented": true,
  "all_visible_controls_implemented": true,
  "component_mapping_complete": true,
  "no_unmapped_required_elements": true,
  "mappings": [
    {
      "element_id": "",
      "implemented_as": "React component / DOM / CSS / SVG / asset",
      "file": "prototype/src/pages/Page.jsx",
      "notes": ""
    }
  ],
  "unmapped_required_elements": []
}
```

Then render the route and write `visual-replica-audit.json`:

```json
{
  "passed": true,
  "page_id": "",
  "route": "",
  "visual_similarity_score": 0.9,
  "visual_replica_passed": true,
  "all_visible_ai_elements_represented": true,
  "structural_layout_matched": true,
  "copy_and_iconography_matched": true,
  "nonstandard_layouts_preserved": true,
  "no_unapproved_simplification": true,
  "screenshot_path": "prototype/qa/react-page-workers/<page_id>/screenshots/route.png",
  "approved_image": "",
  "missing_visible_elements": [],
  "simplified_structures": [],
  "layout_drift": [],
  "copy_mismatches": [],
  "icon_or_asset_mismatches": [],
  "hard_failures": []
}
```

Do not mark the page worker passed when visible AI-image elements are missing, when a specific visual structure is converted into a generic grid/list/card, when icons/illustrations are replaced with unrelated placeholders, when bottom/top navigation changes structure, or when the rendered route visibly drifts from the approved page image.

## Runtime Setup

The React prototype is expected to run locally.

- If `node` and `npm` are available in the shell, use them.
- If the local environment lacks Node.js, use the bundled Codex workspace runtime when available.
- If dependencies are missing, run `npm install` in `prototype/`.
- Run the app with `npm run dev -- --host 127.0.0.1` or the command in `package.json`.
- If the requested environment cannot install dependencies or run React, mark the React phase blocked with the exact missing capability.

## Visual Recreation Requirement

The React UI must be rebuilt as components, not shown as full-screen screenshots. Treat the approved AI page image as the visual contract, not a loose mood board.

Explicitly forbidden implementations:

- full-page approved image rendered as the app UI;
- image hotspot maps;
- screenshot carousel/image browser with route labels;
- fake controls overlaid on static images;
- primary UI implemented as non-semantic absolute-positioned overlays when components could be built normally.

For every required page, use the approved AI page image as the visual source of truth for:

- page frame, status/nav bars, route layout, and scroll behavior;
- card positions, component density, spacing, border radius, shadows, dividers, and background;
- typography scale, weight, alignment, and visible copy language;
- button styles, tab/segmented controls, chips, inputs, dialogs, toasts, and selectors;
- colors, accent use, icon style, mascot/illustration placement, and image-derived decorative elements;
- default, success, error, empty, loading, modal, and blocked states declared in the brief.

Baseline replication means:

- major regions appear in the same order and relative position as the approved image;
- primary navigation, page title, hero/summary area, core content blocks, and primary actions are all present;
- component shapes, density, color palette, type scale, and visual rhythm remain recognizably the same;
- responsive adjustments preserve hierarchy instead of collapsing into a different product layout;
- intentional deviations are documented in the visual parity report with a practical reason.

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

React is not complete when it only looks correct. Primary interactions must be exercised and either work or be explicitly marked blocked with the reason. Dead primary buttons, broken route targets, inactive controls that appear interactive, unreachable modals/states, and missing success/error/empty states are hard failures.

Each page worker must verify page-local behavior against the original requirements, page brief, and structured design document. The main agent must verify cross-page behavior against all `route_targets`, page-worker outbound route records, and whole-product flows. When sources conflict, document the conflict and follow the structured design document only if it explicitly resolved the requirement; otherwise mark the flow blocked for main-agent review.

## React Worker Output Gate

Before visual parity scoring, require:

- `prototype/qa/react-worker-result.json` exists and has `passed: true`;
- `implementation_type` is `component_frontend`;
- `screenshot_or_hotspot_demo` is `false`;
- `main_agent_scaffold_passed`, `style_system_locked`, `page_workers_started_after_scaffold`, `page_workers_used_shared_scaffold`, `demo_page_switcher_passed`, and `scroll_behavior_passed` are `true`;
- `all_required_routes_implemented`, `all_declared_interactions_implemented`, `source_requirements_aligned`, `structured_design_doc_aligned`, and `approved_images_replicated` are all `true`;
- `max_active_subagents` is present and is no greater than `6`;
- `global_navigation_passed` and `cross_page_state_passed` are `true`;
- `implemented_route_count` is at least the non-deferred required page count;
- `prototype/qa/react-page-worker-registry.json` exists, has `passed: true`, and registers every required page worker;
- every registered page worker has passing `visual-decomposition.json`, `dom-element-inventory.json`, and `visual-replica-audit.json`;
- `prototype/qa/react-navigation-audit.json` exists, has `passed: true`, and verifies global navigation plus cross-page state;
- `prototype/qa/react-usability-audit.json` exists, has `passed: true`, verifies the right-side page switcher, and includes a passing scroll result for every required page;
- `page_worker_results` contains one passing result for every non-deferred required page;
- `prototype/qa/react-interaction-audit.json` exists and has `passed: true`;
- every required page has a passing interaction audit entry;
- the aggregate interaction audit has `global_navigation_passed: true` and passing `cross_page_flow_results`;
- `hard_failures` and `unresolved_blockers` are empty.

If this gate fails, repair the prototype or mark the exact failing flow blocked. Do not proceed to Feishu/Figma delivery with a failed React worker gate.

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
- broken primary interactions, dead navigation targets, or unreachable declared states.
- broken scroll behavior, clipped bottom content, or a missing/broken right-side page switcher.

Do not mark Final Functional Audit as passed until visual parity is passed or every failure is explicitly blocked with a reason.

Write `prototype/qa/visual-parity-report.md` for human review and `qa/visual-parity-audit.json` for script gates. The JSON audit must include one entry per required page and every `visual_similarity_score` must be at least `0.80`. It must also record interaction hard failures separately from visual scores so a visually similar but non-functional prototype cannot pass.

## Verification

Before final response:

- Confirm `package.json`, `index.html`, `src/main.jsx`, `src/styles.css`, and `src/prototype-data.js` exist.
- Confirm every non-deferred required page has one route/view in `src/prototype-data.js`.
- Confirm `prototype/qa/react-scaffold-audit.json` exists, passes, covers every required page slot, and locks the shared style system before page worker outputs.
- Confirm every linked approved AI reference image exists.
- Confirm `prototype/prototype-data-report.json` exists and route count covers all non-deferred required pages.
- Confirm `prototype/qa/react-worker-result.json` and `prototype/qa/react-interaction-audit.json` exist and pass.
- Confirm `prototype/qa/react-usability-audit.json` exists, passes, covers every required route, and verifies page menu navigation plus scroll behavior.
- Run `npm install` if dependencies are missing.
- Run `npm run build` when feasible.
- Run the React app locally and inspect routes/interactions when browser tools are available.
- Capture or inspect route screenshots and complete the React Visual Parity Gate.
- Confirm `qa/visual-parity-audit.json` exists and every required page has `visual_similarity_score >= 0.80`.
- Report the local folder path, run command, visual parity result, and Final Functional Audit result.
