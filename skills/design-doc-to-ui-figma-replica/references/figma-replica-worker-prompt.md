# Figma Page Replica Worker Prompt

Use this prompt when delegating one page/frame of the Figma replica after the main agent has already prepared the Figma scaffold. Each worker owns exactly one required page frame and its local assets. The main agent owns the Figma file structure, global prototype links, cross-frame navigation, shared components/tokens, page frame slots, and final delivery audit.

Run page workers in batches with at most 6 active SubAgents across the run. If more pages are required, wait for workers to finish before starting the next batch.

```text
You are responsible for creating or updating exactly one editable Figma frame for a completed design-doc-to-ui run.

You are not alone in the workspace. The main agent has already prepared the Figma file scaffold, shared styles/variables/components where practical, page frame slots, and global prototype contract. Own only the assigned page frame, assigned local components/assets, and assigned figma-assets/ artifacts. Do not modify source docs, page image worker outputs, React files, page briefs, ui-run.json, unrelated Figma frames, global styles/variables, or unrelated files. Do not revert others' edits. If a shared component, token, or prototype target must change, record the required change for the main agent instead of silently editing another worker's scope.

Assigned page:
- page_id: <page_id>
- route: <route>
- page name: <page_name>
- Figma frame target: <frame or creation instructions>
- owned asset directory: figma-assets/<page_id>/
- output audit directory: qa/figma-page-workers/<page_id>/

Inputs:
- ui-run.json: <path, read-only>
- source document or normalized source bundle: <paths>
- app_requirements_summary: <path or pasted summary>
- structured design document and audit: <paths>
- main-agent Figma scaffold audit: qa/figma-scaffold-audit.json
- shared Figma styles/variables/components and frame ownership map: <paths or notes>
- approved AI page image for this page: <path>
- rendered React route screenshot and audits for this page: <paths>
- assigned page brief, worker review, and main audit entry: <paths>
- Figma file/link or target file instructions: <link or output target>

Task:
1. Read the approved AI page image, structured design document, source requirements, assigned page brief, and React screenshot before writing Figma.
2. Build or repair one editable Figma frame for the assigned page inside the main-agent Figma scaffold:
   - use frames, auto layout, text layers, vector shapes, component instances, variables/styles where practical;
   - do not use a full-page screenshot as the implementation;
   - keep the approved image and React screenshot only as locked references or side-by-side references outside the implementation frame;
   - use the assigned frame slot, shared styles/variables/components, naming conventions, and prototype target contract prepared by the main agent;
   - do not create a competing global Figma structure, style system, or prototype convention;
   - recreate layout, typography, spacing, color, controls, states, icons, illustrations, and image assets from the approved design;
   - add page-local prototype links or interaction annotations for primary actions where Figma supports them;
   - record outbound prototype targets for the main agent to wire and verify globally.
3. Ensure the page frame is frontend-handoff ready:
   - layers are named clearly;
   - repeated UI within the page is componentized where practical;
   - colors/type/spacing use reusable styles, variables, or documented layer notes where practical;
   - icons are vector or individual replaceable components/assets;
   - complex illustrations/mascots are individual isolated assets, not embedded full-screen screenshots.
4. Handle missing assets for this page:
   - crop the desired source element from the approved AI design image or React screenshot as a local reference;
   - start an asset SubAgent with image_gen to generate a clean, single isolated asset on a plain or transparent-friendly background;
   - remove/crop the background locally when needed;
   - save the processed asset under figma-assets/<page_id>/ with source page, prompt, and usage notes;
   - place the isolated asset in Figma as its own editable/replaceable layer;
   - record it for the main `figma-assets/asset-manifest.json`.
5. Review the assigned frame against the approved AI image and React route:
   - visual 1:1 baseline replication;
   - editable element coverage;
   - icon/asset replication;
   - page-local prototype links or target records;
   - frontend handoff readiness.

Write these files:
- qa/figma-page-workers/<page_id>/worker-result.json
- qa/figma-page-workers/<page_id>/frame-audit.json
- qa/figma-page-workers/<page_id>/review.md
- figma-assets/<page_id>/asset-manifest.fragment.json when generated or processed assets exist

worker-result.json:
{
  "passed": true,
  "status": "passed|blocked|infeasible",
  "page_id": "",
  "route": "",
  "figma_frame_name": "",
  "figma_frame_node_id": "",
  "implementation_type": "editable_figma_frame",
  "full_screen_image_implementation": false,
  "main_figma_scaffold_used": true,
  "shared_styles_followed": true,
  "owned_frame_slot_used": true,
  "visual_similarity_score": 0.9,
  "editable_element_coverage": 0.98,
  "baseline_replica_passed": true,
  "editable_elements_passed": true,
  "icons_replicated": true,
  "assets_reconstructed": true,
  "frontend_handoff_ready": true,
  "page_prototype_links_recorded": true,
  "outbound_prototype_targets": [
    {
      "trigger": "",
      "target_page_id": "",
      "target_route": "",
      "notes": ""
    }
  ],
  "asset_manifest_fragment": "figma-assets/<page_id>/asset-manifest.fragment.json",
  "unresolved_blockers": [],
  "changed_files": []
}

frame-audit.json:
{
  "passed": true,
  "page_id": "",
  "visual_similarity_score": 0.9,
  "baseline_replica_passed": true,
  "editable_elements_passed": true,
  "icon_replication_passed": true,
  "asset_reconstruction_passed": true,
  "prototype_links_or_targets_recorded": true,
  "frontend_handoff_ready": true,
  "hard_failures": [],
  "missing_assets": [],
  "repair_required": []
}

Do not mark passed when the assigned frame is missing, a full-page screenshot is used as implementation, major UI elements are flattened, icons/assets are generic substitutes, page-local prototype targets are not recorded, or frontend handoff would require rebuilding the frame from scratch.
```

## Main-Agent Aggregate Contract

After all page workers finish, the main agent wires global Figma structure, shared components/tokens, cross-frame prototype links, and final audit. It writes:

- `qa/figma-worker-result.json`
- `qa/figma-replica-audit.json`
- `qa/figma-scaffold-audit.json`
- `qa/figma-page-worker-registry.json`
- `qa/figma-prototype-link-plan.json`
- `qa/figma-integration-audit.json`
- `figma-assets/asset-manifest.json` when generated or processed assets exist

The aggregate result must include:

```json
{
  "passed": true,
  "figma_url": "",
  "implementation_type": "editable_figma_frames",
  "full_screen_image_implementation": false,
  "max_active_subagents": 6,
  "figma_scaffold_passed": true,
  "page_workers_started_after_scaffold": true,
  "page_workers_used_shared_frame_slots": true,
  "required_page_count": 0,
  "editable_frame_count": 0,
  "editable_element_coverage": 0.98,
  "all_required_frames_created": true,
  "all_major_elements_editable": true,
  "icons_replicated": true,
  "assets_reconstructed": true,
  "frontend_handoff_ready": true,
  "prototype_links_verified": true,
  "global_prototype_links_passed": true,
  "page_worker_results": [
    {
      "page_id": "",
      "route": "",
      "passed": true,
      "worker_result": "qa/figma-page-workers/<page_id>/worker-result.json",
      "frame_audit": "qa/figma-page-workers/<page_id>/frame-audit.json"
    }
  ],
  "unresolved_blockers": [],
  "asset_manifest": "figma-assets/asset-manifest.json"
}
```

The aggregate Figma audit must include one passing page score per required page, `global_prototype_links_passed: true`, and passing `cross_frame_navigation_results` for whole-product jumps.

If Figma tools, SubAgent delegation, image generation, or local image processing are technically unavailable, mark the exact capability blocked and do not present the Figma output as complete.
