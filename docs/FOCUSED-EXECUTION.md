# Focused execution v1

Status: experimental implementation, opt-in. `designer-v1` remains the default. See the verification section for the distinction between policy checks and observed artwork. Existing v1/v2 helpers and historical v3 runs keep their original contracts.

## Purpose and algorithm

The builder should solve one visible construction problem at a time. More decomposition and more checklists can increase distraction. This profile inherits designer research, calibration, three alternatives, independent concept selection, a target/specification, representative construction study, two independent final specialists, and current export provenance. It changes construction acceptance, not the renderer or model.

1. Establish the inherited designer prerequisites.
2. Read `workflow_status {"view":"working"}`. Use its current task, object IDs, previews, applicable checks and next action. Retrieve full evidence only when relevant.
3. Plan one component or a connected group of up to three semantic entities. State the goal, preservation requirements and two or three observable checks.
4. Execute the batch through the normal gateway. Capture native/full/use evidence. Actually inspect both images, the target, and affected neighbors. Inspect an optional detail image when needed.
5. Confirm with `pass`, `revise`, or `blocked`. Capture/inspection, task success, and stage completion are separate events.
6. Correct the first queued finding. A failed task remains unresolved; do not begin unrelated work or a later stage.
7. Explicitly accept the stage when its required elements exist and its three stage checks pass. Later stages retain separate obligations.
8. Export/preflight, obtain fresh independent reviews, correct consequential findings in priority order, and deliver the independently retained best version.

Scope is declarative guidance, not a per-object sandbox. The gateway cannot infer the intent of every native command or prove a part is semantically connected. Review the actual effects afterward. A small packet also does not erase the host's existing conversation; the skill changes what the builder actively uses, not the model's context window.

For interactions, trace each arm/object to its endpoint before editing and explicitly name working/supporting roles in the goal and checks. A single native group can contain several hands; counting entity IDs is not a semantic complexity measure. The forward test exposed this distinction when a locally smooth wrist connection joined the wrong arm route.

## Contracts

Start with `workflow_start` in full mode and `quality_profile: "focused-execution-v1"`. The five-tool interface is preserved. Quick mode rejects this profile; ordinary quick edits remain unchanged. Resume uses the stored profile, never the caller's default. `workflow_status` without a view retains full status and schemas; `view:"working"` returns only the focused working packet. Other profiles retain their normal status.

Focused mutations that ordinarily return workflow status return the compact working packet instead, so every task does not repeat the full global schemas. Captures, export preflight and neutral review packets retain their specialized result shapes. Explicit full status remains the authoritative schema view. Default/historical profiles retain their existing responses.

The profile adds these fields to `workflow_begin.plan`; existing `purpose`, `changes`, and `expected_result` remain required:

```json
{
  "task_id": "repair-grip",
  "goal": "Make the hand visibly wrap around the screwdriver handle",
  "purpose": "Resolve the observed working-grip finding",
  "changes": "Refine the named working-hand contours around the fixed handle",
  "expected_result": "A readable enclosing grip with retained tool contact",
  "entities": ["hand", "driver"],
  "preserve": "Keep the wrist connection, tool tip contact and overall pose",
  "checks": [
    {"id":"grip", "description":"Fingers visibly enclose the handle at use size"},
    {"id":"contact", "description":"Continuous shaft still meets the screw"},
    {"id":"neighbors", "description":"Wrist and surrounding forms remain coherent"}
  ],
  "finding_id": "task-initial-grip"
}
```

This is illustrative, not evidence of a completed repair. `entities` must reference the current specification. Check IDs are unique, filename-safe, and assessed exactly once. Include `finding_id` only when addressing the first queued finding. Reuse a task ID only to correct that unresolved task, preserving its stage and entity scope. Passed or specification-stale tasks require new IDs.

Confirmations include `outcome`, actual `observations`, `preservation_observation`, cumulative `element_map`, `check_results`, and the same `image_inspection`/`image_observation` evidence contract used by designer records. Both full/use previews and the target must be included. Each result has an `id`, `outcome: pass|fail|not_applicable`, and visible `observation`; inapplicable checks also require a `reason`. A failed check cannot pass the task. `revise` and `blocked` require a concrete reason. `blocked` is a task outcome, not a terminal run status: new information or a correction may resolve it.

`stage_complete` is an explicit boolean, default false. When true, supply all stage keys below as `stage_checks`, each with outcome/observation and an inapplicable reason where needed. No failed stage check may complete the stage. All required elements introduced through that stage must map to actual native objects. A batch may map only its newly introduced parts plus previously introduced elements; a whole unfinished stage need not exist merely to inspect a component.

| Stage | Completion keys |
| --- | --- |
| composition | `placement_scale`, `reading_order`, `focal_separation` |
| typography | `exact_copy`, `live_text_fonts`, `use_size_readability` |
| imagery | `recognizable_forms`, `proportions`, `critical_interactions` |
| finishing | `scene_cohesion`, `visible_defects`, `production_readiness` |

The working packet reports current and specification revisions, task scope, last confirmed relevant object mappings, full/use paths, optional `detail_images`, preview freshness, stage checks, correction queue, authoritative next action, and paths to larger evidence. Object IDs from a stale packet must be reconciled with actual document inspection. Detail images are optional project images recorded with hashes; there is no automatic crop or claim of automatic inspection.

## Corrections, invalidation and recovery

A `revise`/`blocked` confirmation preserves native/image/observation evidence, clears the pending batch and creates an unresolved task finding. It does not complete the stage. The next batch addresses that finding using the same task ID. A passing correction resolves it. Independent reviews add major/critical candidate findings to the queue only while further correction remains allowed; critical findings come first, with stable reviewer order otherwise. Minor preferences are not forced into extra work.

Any authoring edit invalidates current export readiness and focused verification. Editing an already accepted stage reopens that stage and all later stages. Earlier acceptance remains historical and is rechecked through the passing task's preservation observation; the gateway cannot prove that preservation visually succeeded. Target/specification changes invalidate all stage acceptance and mappings, mark historical tasks/findings stale, and require new task IDs. Unresolved findings remain visible rather than silently disappearing; obsolete entity references are removed from their active scope so they can be reconciled against the amended specification.

Preflight requires all four explicit stage acceptances, a passing observation at the current document revision, current specification binding, no pending batch, and no unresolved tasks/findings. Existing font/copy/bounds/vector/export-byte checks still run. Numerical checks do not certify readability or aesthetic quality.

Resume restores the stored task, queue, mappings, pending capture and recovery document. Never replay uncertain operations. Preserve connection-owned windows and recovery files, project filesystem roots, original artwork, independently retained best, three final correction rounds, and the two-non-improving stop rule. A task correction is not a new final review budget.

## Research and limitations

- [Plan-and-Act](https://proceedings.mlr.press/v267/erdogan25a.html) separates high-level planning from environment actions. It motivates sequential planning/construction roles; its trained web-agent results do not establish vector-design gains here.
- [FigTree](https://arxiv.org/html/2609.01006) builds scientific diagrams from local SVG programs with occupied-space reports and connection ports. It motivates addressable local repairs and later connection anchors; its recursive multi-agent implementation is not integrated here.
- [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/) studies position sensitivity in long-context retrieval tasks. Compact packets are a hypothesis, not proof of current host-model distraction or its remedy.
- [Constrained iterative SVG refinement](https://arxiv.org/html/2608.28678) reports that repeated feedback and syntactic constraints do not consistently improve visual quality in tested models. Retained-best selection and observed corrections remain necessary.

This profile does not add a model API, separate image generator, automatic segmentation, learned geometry solver, or additional editing agents. Independent reviewers remain the existing fresh concept and final specialists. Whole-scene observations are mandatory because good local parts can still produce a poor global composition.

## Verification

Self-contained fixtures test enforcement, invalidation and recovery state. Native integration tests exercise the production gateway and actual editable documents; neither establishes design quality. A real interaction illustration, observed correction, native reopening, export inspection and fresh image reviews are required for forward-test evidence. Results and remaining weaknesses are recorded separately in the verification report. The larger comparative pilot is deferred; no general quality improvement or default promotion is claimed.

The [verification report](FOCUSED-EXECUTION-VERIFICATION.md) records 151 passing checks, the actual maintenance test, a rejected local correction, retained-best behavior, the final passed version and remaining limitations.
