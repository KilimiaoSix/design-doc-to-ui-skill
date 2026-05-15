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
2. Build or repair the assigned route as a formal React page inside the main-agent scaffold:
   - implement page UI as React components, not a full-screen screenshot or image hotspot map;
   - keep the approved image only as a visual reference, thumbnail, audit attachment, or cropped decorative asset when needed;
   - preserve the assigned route identity from prototype/src/prototype-data.js;
   - use the shared shell, route contract, CSS variables/tokens, typography, spacing scale, and component conventions created by the main agent;
   - do not create a competing global layout, router, style reset, or independent design system;
   - replicate the approved AI image as the visual contract for layout, typography, colors, density, controls, and page-local states;
   - implement interactions according to the source requirements and structured design document.
3. Implement and verify page-local interactions:
   - primary and secondary buttons on the assigned page;
   - forms, inputs, uploads/selectors, tabs/segmented controls, toggles, dialogs, toasts, loading states, success/error/empty/blocked/quota states declared for this page;
   - page-local route intents such as "go to detail", "back", "retry", or "continue" by emitting the expected route target contract for the main agent.
4. Run the prototype locally when feasible, inspect the assigned route, and exercise all assigned interactions.
5. Repair until the assigned page behaves like a coherent production page, or explicitly mark an infeasible blocker.
6. Record every outbound route target and any shared state dependency so the main agent can validate whole-app navigation.

Write these files:
- prototype/qa/react-page-workers/<page_id>/worker-result.json
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

Do not mark passed when the assigned route is implemented mainly by placing a full-page image, when visible controls are fake, when page-local primary actions are dead, when declared states are unreachable, when outbound route targets are missing, or when behavior contradicts the source requirements or structured design document.
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
      "interaction_audit": "prototype/qa/react-page-workers/<page_id>/interaction-audit.json"
    }
  ],
  "unresolved_blockers": []
}
```

The aggregate interaction audit must include `global_navigation_passed: true`, one passing page result per required page, and passing `cross_page_flow_results` for the whole product flow.

If the React worker cannot run Node/npm, cannot start the dev server, or cannot inspect routes, it must mark the exact capability as blocked instead of claiming the page or prototype is complete.
