# Structured Design Document Quality Gate

Use this gate before React, Feishu, or Figma work. A structured design document is not a screenshot catalog, delivery index, or page-by-page summary. It must be a decision-quality product design artifact that lets product, design, engineering, and QA understand what is being built, why it is shaped that way, how pages connect, and how implementation will be accepted.

## Standards Basis

This gate is based on durable design-documentation principles from:

- GOV.UK Service Manual: write user stories with actor, need, goal, and acceptance criteria; map the wider journey to avoid dead ends and confusing/duplicative content.
- Nielsen Norman Group UX deliverables: design systems are standards for reusable components/patterns; maps document screens, elements, and cross-channel workflow consistency.
- Atlassian Design System: design tokens are the source of truth for repeatable UI decisions and reduce handoff ambiguity; accessibility still requires pattern, content, and interaction review.
- Figma handoff guidance: annotations, measurements, status, component/style alignment, and change comparison reduce implementation misinterpretation.
- W3C WCAG 2.2: accessibility conformance should be part of design and evaluation, especially focus, target size, authentication, status messages, and low-vision/mobile support.

## Non-Compliance Signals

Mark the document non-compliant when it has any of these issues:

- mostly page screenshots plus one-line callouts;
- generic design adjectives without source evidence or design tradeoffs;
- no clear user problem, target user, scenario, or user story;
- no acceptance criteria for product behavior, page completion, or implementation quality;
- task flow diagram exists but does not explain decision points, failure paths, recovery, or cross-page dependencies;
- component system lists component names but omits states, behavior, tokens, and reuse rules;
- page specs omit visible copy, input/output data, interaction states, error/empty/loading states, and dependencies;
- no accessibility, responsive, content, or localization notes;
- no handoff instructions for React/Figma visual replication and interaction verification;
- no evidence traceability to source requirements, page briefs, approved images, or audits.

## Required Quality Pillars

Every structured design document must cover these pillars.

### 1. Executive Decision Summary

Include:

- product and audience in one paragraph;
- design proposition and what problem it solves;
- top 3-5 product/design decisions;
- what was intentionally not solved;
- current delivery status and blocking risks.

### 2. Source Traceability

Include a matrix mapping source requirements to:

- page ids;
- user stories;
- approved AI image paths;
- page brief paths;
- prototype route ids;
- open questions or assumptions.

Do not present unsupported product claims as confirmed requirements.

### 3. User Stories And Acceptance Criteria

For each core scenario, document:

- actor / user segment;
- user need and goal;
- trigger and success outcome;
- acceptance criteria in testable language;
- evidence or source reference.

Use the "as a / I need / so that" structure only when it is natural in the requested output language. Other formats are allowed, but actor, need, goal, and done criteria are required.

### 4. Journey, Information Architecture, And Page Linkage

Include:

- end-to-end journey map from entry to activation, core task, success, monetization, and recovery;
- page map and information architecture;
- primary route graph;
- decision points and branch logic;
- dead ends, recovery paths, and cross-page dependencies;
- where offline, external, backend, or data dependencies affect the journey.

### 5. Design Rationale And Tradeoffs

For major decisions, include:

- decision;
- rationale tied to user need, source evidence, or style contract;
- alternatives considered;
- why the selected option was chosen;
- risks and how the prototype handles them.

### 6. Visual System And Design Tokens

Include a reusable visual system, not only a style description:

- color roles and token-like names;
- typography scale and usage;
- spacing/grid/density rules;
- radius, border, elevation, and surface rules;
- icon, illustration, mascot, image, and motion rules;
- responsive adaptation rules;
- negative rules that prevent style drift.

### 7. Component And Pattern Matrix

For each repeated component/pattern, include:

- purpose;
- pages used;
- anatomy;
- variants;
- default, hover, focus, disabled, loading, success, error, empty, and selected states as applicable;
- content rules;
- accessibility notes;
- React/Figma replication notes.

### 8. Page Specifications

Every required page needs a detailed spec. Minimum fields:

- page id/name/route/endpoint;
- source requirement references;
- user story and page goal;
- information hierarchy;
- major regions and component list;
- visible copy and data examples;
- inputs, outputs, validations, and dependencies;
- states: default/loading/empty/error/success/blocked/modal/quota where relevant;
- primary and secondary interactions;
- route targets and back/recovery paths;
- approved AI image path and worker review path;
- implementation acceptance criteria;
- accessibility and responsive notes.

### 9. Interaction, State, And Error Matrix

Include a matrix covering:

- trigger;
- source page;
- target page/state;
- visible feedback;
- async/loading behavior;
- error or empty fallback;
- recovery action;
- whether React implements it;
- whether Figma links/annotates it when Figma is requested.

### 10. Accessibility, Content, And Localization

Include:

- contrast and token risks;
- keyboard/focus expectations;
- target size and touch considerations;
- semantic role expectations for buttons, links, forms, dialogs, lists, tables, and status messages;
- readable language and content tone rules;
- localization/copy-length risks;
- reduced motion or accessibility-sensitive animation notes where relevant.

### 11. Handoff And Acceptance

Include:

- React implementation source of truth: approved image + page brief + document spec;
- Figma replication source of truth when requested;
- per-page visual similarity threshold and hard failures;
- interaction acceptance criteria;
- QA checklist;
- assets, exports, and run commands;
- known blockers and residual risks.

### 12. Revision History

Include:

- initial version id/date;
- feedback revisions;
- affected pages/channels;
- regenerated images or React/Figma patches;
- gates rerun;
- unresolved risks.

For first delivery, state that no user feedback revisions have occurred yet.

## Required Document Audit

Before running `validate_design_run.py --phase design-completion`, write `qa/structured-design-doc-audit.json` or the path recorded in `ui-run.json` under `artifacts.structured_design_doc_audit`.

The audit must be produced after reading the structured design document and run manifest. It must not be a placeholder.

Required JSON:

```json
{
  "passed": true,
  "quality_score": 0.9,
  "required_page_count": 12,
  "documented_page_spec_count": 12,
  "source_traceability_present": true,
  "design_rationale_present": true,
  "user_story_acceptance_criteria_present": true,
  "journey_and_ia_present": true,
  "page_specs_complete": true,
  "interaction_state_matrix_present": true,
  "component_token_system_present": true,
  "accessibility_review_present": true,
  "handoff_acceptance_criteria_present": true,
  "revision_history_present": true,
  "screenshot_catalog_only": false,
  "blockers": [],
  "warnings": [],
  "repair_actions": []
}
```

Do not mark `passed: true` unless all required quality pillars are present and the document is useful for implementation, review, and QA.

## Minimum Score Guidance

Use this scoring model:

- 15% source traceability and evidence;
- 15% user stories, goals, and acceptance criteria;
- 15% journey, IA, and page linkage;
- 15% page specs and interaction/state completeness;
- 15% component system, tokens, and visual rules;
- 10% accessibility/content/localization;
- 10% handoff and QA acceptance;
- 5% revision history and residual risk clarity.

The document passes only when `quality_score >= 0.85`, every required page has a detailed spec, and there are no blockers.
