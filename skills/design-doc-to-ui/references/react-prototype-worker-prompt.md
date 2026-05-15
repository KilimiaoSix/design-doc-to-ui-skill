# React Page Worker Prompt

Use this as the base prompt when delegating one page or route of the React prototype after the main agent has already created the React scaffold. Each worker owns exactly one assigned page/route and its local states/interactions. The main agent owns the app shell, shared router, global style system, page slots, cross-page state, and whole-flow navigation validation.

Run page workers in batches with at most 6 active SubAgents across the run. If more pages are required, wait for workers to finish before starting the next batch.

```text
You are responsible for implementing and verifying exactly one assigned page/route in the runnable React prototype for a completed design-doc-to-ui run.

You are not alone in the workspace. The main agent has already created the React app scaffold, route registry, shared layout, shared style tokens, base CSS, and page slots. Own only the assigned page files, assigned local components, assigned local styles, and assigned QA output. Do not modify source documents, design image worker outputs, page briefs, ui-run.json, unrelated pages, app shell, route registry, global style tokens, or unrelated shared code. Do not revert others' edits. If a shared component, style token, or route contract must change, record the required change for the main agent instead of silently editing another worker's scope.

Assigned page:
- page_id: <page_id>
- route: <route>
- page name: <page_name>
- owned files/components: <paths>
- allowed shared files, if any: <paths>

Inputs:
- source document or normalized source bundle: <paths>
- app_requirements_summary: <path or pasted summary>
- ui-run.json: <path, read-only>
- structured design document: <path>
- structured design document audit: <path>
- global_style_contract: <path>
- main-agent React scaffold audit: prototype/qa/react-scaffold-audit.json
- shared React shell, route registry, style tokens, and CSS conventions: <paths>
- assigned page brief: <path>
- approved AI page image for this page: <path>
- worker review and main audit entries for this page: <paths>
- generated prototype data: prototype/src/prototype-data.js
- output directory for this page audit: prototype/qa/react-page-workers/<page_id>/

Task:
1. Read the source requirements, structured design document, assigned page brief, approved UI image, and prototype data before editing.
2. Before coding, decompose the approved AI image into `visual-decomposition.json`:
   - list every visible region, card, control, progress indicator, chip, task row, icon, illustration/mascot, decorative stroke, connector, top navigation/status area, and bottom navigation item;
   - identify nonstandard structures that must not be simplified, such as tree/graph layouts, timeline connectors, hand-drawn marks, mascot callouts, circular progress cards, or custom tab/filter groups;
   - write explicit "must not simplify" rules for this page.
3. Build or repair the assigned route as a formal React page inside the main-agent scaffold:
   - implement page UI as React components, not a full-screen screenshot or image hotspot map;
   - keep the approved image only as a visual reference, thumbnail, audit attachment, or cropped decorative asset when needed;
   - preserve the assigned route identity from prototype/src/prototype-data.js;
   - use the shared shell, route contract, CSS variables/tokens, typography, spacing scale, and component conventions created by the main agent;
   - do not create a competing global layout, router, style reset, or independent design system;
   - replicate the approved AI image as the visual contract for layout, typography, colors, density, controls, and page-local states;
   - recreate specific visual structures rather than replacing them with generic equivalents;
   - preserve top/bottom navigation structure, visible chips/filters, card sequence, decorative motifs, icon language, and illustrations unless an approved revision explicitly removes them;
   - implement interactions according to the source requirements and structured design document.
4. Create `dom-element-inventory.json` after coding, mapping every required visual element from `visual-decomposition.json` to its implemented React component, DOM element, CSS construction, SVG/vector, or isolated asset.
5. Render the route and create `visual-replica-audit.json` by comparing the route screenshot with the approved AI image. Repair until structural simplification, missing visible elements, copy mismatches, icon/asset mismatches, and major layout drift are gone.
6. Implement and verify page-local interactions:
   - primary and secondary buttons on the assigned page;
   - forms, inputs, uploads/selectors, tabs/segmented controls, toggles, dialogs, toasts, loading states, success/error/empty/blocked/quota states declared for this page;
   - page-local route intents such as "go to detail", "back", "retry", or "continue" by emitting the expected route target contract for the main agent.
7. Run the prototype locally when feasible, inspect the assigned route, and exercise all assigned interactions.
8. Repair until the assigned page behaves like a coherent production page and visually matches the approved image, or explicitly mark an infeasible blocker.
9. Record every outbound route target and any shared state dependency so the main agent can validate whole-app navigation.

Write these files:
- prototype/qa/react-page-workers/<page_id>/worker-result.json
- prototype/qa/react-page-workers/<page_id>/visual-decomposition.json
- prototype/qa/react-page-workers/<page_id>/dom-element-inventory.json
- prototype/qa/react-page-workers/<page_id>/visual-replica-audit.json
- prototype/qa/react-page-workers/<page_id>/interaction-audit.json
- prototype/qa/react-page-workers/<page_id>/review.md
- route screenshots or inspection evidence under prototype/qa/react-page-workers/<page_id>/screenshots/ when feasible

worker-result.json:
{
  "passed": true,
  "status": "passed|blocked|infeasible",
  "page_id": "",
  "route": "",
  "implementation_type": "component_frontend",
  "screenshot_or_hotspot_demo": false,
  "main_scaffold_used": true,
  "style_system_followed": true,
  "owned_page_slot_used": true,
  "visual_decomposition_completed": true,
  "dom_inventory_matches_design": true,
  "visual_replica_audit_passed": true,
  "all_visible_ai_elements_represented": true,
  "nonstandard_layouts_preserved": true,
  "no_unapproved_simplification": true,
  "source_requirements_aligned": true,
  "structured_design_doc_aligned": true,
  "approved_image_replicated": true,
  "page_interactions_verified": true,
  "declared_states_reachable": true,
  "outbound_route_targets_recorded": true,
  "dev_server_verified": true,
  "build_verified": true,
  "outbound_route_targets": [
    {
      "trigger": "",
      "target_route": "",
      "required_state": "",
      "notes": ""
    }
  ],
  "shared_state_requirements": [],
  "unresolved_blockers": [],
  "changed_files": []
}

visual-decomposition.json:
{
  "passed": true,
  "page_id": "",
  "approved_image": "",
  "approved_image_analyzed": true,
  "all_major_regions_listed": true,
  "all_visible_controls_listed": true,
  "nonstandard_layouts_identified": true,
  "must_not_simplify_rules_created": true,
  "screen_regions": [],
  "element_inventory": [],
  "nonstandard_layouts": [],
  "hard_failures": []
}

dom-element-inventory.json:
{
  "passed": true,
  "page_id": "",
  "all_required_sections_implemented": true,
  "all_visible_controls_implemented": true,
  "component_mapping_complete": true,
  "no_unmapped_required_elements": true,
  "mappings": [],
  "unmapped_required_elements": []
}

visual-replica-audit.json:
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
  "missing_visible_elements": [],
  "simplified_structures": [],
  "layout_drift": [],
  "copy_mismatches": [],
  "icon_or_asset_mismatches": [],
  "hard_failures": []
}

interaction-audit.json:
{
  "passed": true,
  "page_id": "",
  "route": "",
  "route_reachable": true,
  "primary_actions_passed": true,
  "declared_states_reachable": true,
  "forms_and_controls_passed": true,
  "recovery_paths_passed": true,
  "outbound_route_targets_recorded": true,
  "tested_interactions": [
    {
      "interaction": "",
      "expected_result": "",
      "passed": true,
      "notes": ""
    }
  ],
  "hard_failures": []
}

Do not mark passed when the assigned route is implemented mainly by placing a full-page image, when visible controls are fake, when page-local primary actions are dead, when declared states are unreachable, when outbound route targets are missing, when visible approved-image elements are absent, when a custom structure is simplified into a generic grid/list/card, or when behavior contradicts the source requirements or structured design document.
```

## Main-Agent Aggregate Contract

After all page workers finish, the main agent integrates shared app shell, routing, cross-page state, and whole-flow navigation. It writes the aggregate files:

- `prototype/qa/react-worker-result.json`
- `prototype/qa/react-interaction-audit.json`
- `prototype/qa/react-page-worker-registry.json`
- `prototype/qa/react-navigation-audit.json`

The aggregate result must include:

```json
{
  "passed": true,
  "implementation_type": "component_frontend",
  "screenshot_or_hotspot_demo": false,
  "max_active_subagents": 6,
  "main_agent_scaffold_passed": true,
  "style_system_locked": true,
  "page_workers_started_after_scaffold": true,
  "page_workers_used_shared_scaffold": true,
  "required_page_count": 0,
  "implemented_route_count": 0,
  "all_required_routes_implemented": true,
  "all_declared_interactions_implemented": true,
  "global_navigation_passed": true,
  "cross_page_state_passed": true,
  "page_worker_results": [
    {
      "page_id": "",
      "route": "",
      "passed": true,
      "worker_result": "prototype/qa/react-page-workers/<page_id>/worker-result.json",
      "visual_decomposition": "prototype/qa/react-page-workers/<page_id>/visual-decomposition.json",
      "dom_inventory": "prototype/qa/react-page-workers/<page_id>/dom-element-inventory.json",
      "visual_replica_audit": "prototype/qa/react-page-workers/<page_id>/visual-replica-audit.json",
      "interaction_audit": "prototype/qa/react-page-workers/<page_id>/interaction-audit.json"
    }
  ],
  "unresolved_blockers": []
}
```

The aggregate interaction audit must include `global_navigation_passed: true`, one passing page result per required page, and passing `cross_page_flow_results` for the whole product flow.

If the React worker cannot run Node/npm, cannot start the dev server, or cannot inspect routes, it must mark the exact capability as blocked instead of claiming the page or prototype is complete.
