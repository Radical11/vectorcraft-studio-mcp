# Coarse-to-fine roadmap

Status: experimental profiles calibrated and frozen for the eighteen-trial pilot, underway 14 October 2026. Comparative quality is unestablished. Early studies and relationship records are separate from focused-execution-v1. The existing [dated paper](peer-review/README.md) describes a then-unimplemented coarse-to-fine method and an unrun 54-output study. Those artifacts retain their original claims. See the [current contracts](DESIGNER-PROCESS.md) and unchanged frozen [research protocol](research/PROTOCOL.md).

## Current experimental process

Brief/research → three rough layouts → three isolated native 2D blockouts → independent concept selection → meaningful decomposition → progressive assembly → independent final review.

Layouts use actual copy and available fonts, normalized positions/sizes, reading order and negative space. Build all three alternatives as simple native silhouettes and flat shapes. These are temporary studies, not a mandated faceted final style or a 3D pipeline. Give each study a purpose: test hierarchy, proportion, gesture, contact or occlusion. layout-blockout-v1 and designer-process-v1 implement isolated study documents/revisions/recovery and explicit selected-study production transitions; focused-execution-v1 retains its original scope.

Select a blockout as the primary target and refine it in native vectors. Host image generation is optional for a difficult feature or style study, not a required polished whole-scene target. A representative focal pilot tests final contour/color feasibility before completing the scene. Revise a failed blockout rather than freezing its defects.

Decompose scene → objects → meaningful parts → primitives only where useful. Split difficult regions further in response to observed failures, not uniformly. Preserve coherent contours. Each part exposes bounds, critical features, native IDs and named anchors such as wrist, grip, tip and contact point.

Maintain separate graphs: construction dependencies must be acyclic; spatial contact/containment/alignment/occlusion may form cycles. The assembly owner reconciles interactions using the shared anchors. Geometry tolerances are recorded for the brief and remain diagnostic, never aesthetic scores.

The current gateway validates declared parent/dependency graphs and revision-bound relationship checks. The host chooses useful parts and construction order; automatic decomposition, dependency scheduling and semantic attachment solving are not implemented. Anchors are normalized against native bounds. They are useful geometric proxies and do not locate true anatomical/mechanical contact by themselves.

Build critical focal relationships first, supporting context next, and detail visible at intended size last. Use focused task packets and local plus whole-scene inspection. Carry shared palette, contour treatment, typography and lighting decisions through each part. Record meaningful progress and stop repeated changes that add no useful observed benefit.

## Agreed pilot after calibration

- Three fresh locked briefs: one poster, one interacting-subject illustration and one information graphic.
- Three conditions: current designer-v1, layout/blockout-only extension, and the complete new process. The full condition includes focused execution. Keep focused-profile feasibility evidence separate from this study.
- Two independent builds per condition: 3 × 3 × 2 = **18 outputs**. Match references, exact copy, canvas/use size, host model, tools and budgets; randomize build order.
- Each build has 60 minutes and 24 planned edit batches, including layouts/studies/corrections. Check limits before launching another batch; allow in-flight operations to settle without uncertain replay. The maximum construction allowance is 18 hours, excluding shared preparation and independent evaluation.
- Retain three final correction rounds and stop after two non-improving rounds. Record failures, timeouts, budget exhaustion and missing evidence.
- Fresh independent communication/craft comparisons inspect anonymous full/use images, counterbalanced order and observable brief requirements. Report defect counts, practical editability, effort, disagreements, and preferences separately.
- Call the full process promising only when both comparison reviewers and the owner's blind preference agree on clear improvement over current workflow in at least four of six matched pairs, covering at least two genres, with no consequential regression. Report its benefit over blockout-only separately. This small pilot cannot establish general professional superiority.
- Keep experimental profiles opt-in. Default promotion and expansion to the paper's 54-output protocol remain later decisions.

## Sources and hypothesis

[SVGDreamer++](https://arxiv.org/html/2411.17832v2) motivates object/part hierarchies and adaptive primitive allocation. [SketchGraphs](https://ar5iv.labs.arxiv.org/html/2007.08506) motivates explicit relational geometry. [NeuralSVG](https://openaccess.thecvf.com/content/ICCV2025/html/Polaczek_NeuralSVG_An_Implicit_Representation_for_Text-to-Vector_Generation_ICCV_2025_paper.html) motivates meaningful layers. [FigTree](https://arxiv.org/html/2609.01006) motivates component bounds/ports and local repairs. [Render-in-the-Loop](https://arxiv.org/html/2604.20730v2) motivates intermediate render verification while warning that naive feedback is insufficient.

Their learned systems and published outcomes are not integrated or reproduced. Our hypothesis is that externalized composition, narrow tasks and preserved relationships reduce consequential visual losses under a matched construction budget. The pilot must test that hypothesis; more stages, more objects or cleaner records are not evidence of better artwork.

Later work depends on the pilot: calibrated anchors and contact predicates, automatic grouping/connection ownership, broader genres, professional/reader evaluation, cross-model replication and a separate memory-transfer study. More machinery should be added only when observed failures justify it and its cost can be measured.
