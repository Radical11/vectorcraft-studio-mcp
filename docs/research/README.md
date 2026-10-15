# Designer-process research programme

Status on 15 October 2026: interim publication at ten of eighteen accounted attempts. The owner deferred the remaining eight builds. Four attempts passed final construction review, one delivered a verified retained artwork with unresolved quality acceptance, one retained partial production captures, and four were disrupted without final artwork. Comparative image judgments, owner responses and editing evaluation remain pending. The existing dated peer-review report is preserved. This programme evaluates an experimental control policy rather than claiming a new model, vector engine, or unprecedented agent architecture.

The interim paper and sanitized evidence are linked from [the publication checkpoint](INTERIM-PUBLICATION.md). Publishing artwork before owner evaluation creates a further exposure limitation; future owner judgments must not be represented as guaranteed blind responses.

Approved choices: overall design quality first; experimental systems paper; autonomous builds with owner blind feedback; fresh sequential builders; staged 18-output pilot against the current default; human panel later. Default promotion is outside this release.

Start with the [plain-language process](../PROCESS.md) and [progress with stage comparisons](PROGRESS.md). This page retains the detailed research method and source foundation.

## Locked design of the first pilot

Three new genre briefs × three conditions × two independent-context builds = 18 outputs. Conditions: designer-v1; layout-blockout-v1; designer-process-v1. Compare the full method as a bundle, not as proof that each graph or checklist independently causes improvement. Both specialists and the owner's blind preference must agree on improvement in at least four of six default pairs spanning two genres, with no consequential regression in the remaining pairs. Report blockout-only comparisons separately. Three briefs are the independent task units; eighteen outputs are not eighteen independent tasks.

Each build has 60 active minutes and 24 planned batches, including studies and corrections. Independent-review waiting is excluded but reported separately. In-flight edits settle without replay. Match host model/settings, inputs, references, copy, dimensions, intended size and tool access. Two calibration cycles at most use old release briefs and never count as holdouts. Freeze the method and inputs before pilot production; do not feed trial outcomes or lessons to later trial builders.

## Research foundation

The planning pass screened 60 result entries across designer practice, editor-agent systems, vector representation, and evaluation. Relevant sections from 12 primary-source pages were read; this is a targeted review rather than an exhaustive systematic review.

| Source | Borrowed principle | Boundary |
| --- | --- | --- |
| [AIGA design development](https://www.aiga.org/sites/default/files/2021-03/3E_DesignProcess_DesignDevelopment.pdf) | Thumbnails, roughs, purpose-based selection and constructive refinement | Educational designer guidance, not empirical proof of this agent policy |
| [Design Council](https://www.designcouncil.org.uk/resources/framework-for-innovation/) | Divergence/convergence, audience needs, iterative testing | Broad design framework, not a universal fixed sequence |
| [Practitioner illustration process](https://randypreising.com/illustration-process/) | Audience brief, concepts, descriptive feedback, delivery | One practitioner's account |
| [VisPainter](https://arxiv.org/html/2510.27452v1) | Editable editor-agent construction and step/cost evaluation | Close architectural precedent; reported experiment is not reproduced here |
| [mcpInkscape](https://tspi.at/2026/09/13/llminkscape.html) | Structured native edits, explicit reviews and revision-linked export checks | Close practical precedent; author-documented examples |
| [FigTree](https://arxiv.org/html/2609.01006) | Local construction, shared style, occupied bounds, ports and connection ownership | Recursive multi-agent SVG approach; our builder remains sequential |
| [GeoSVG-RL](https://arxiv.org/html/2605.25447) | Executable geometric diagnostics | Training-based diagram method; no RL or semantic-contact guarantee is imported |
| [Hierarchical SVG parsing](https://arxiv.org/html/2609.14657v1) | Meaningful semantic parts and practical editability | Raster-grounded reconstruction differs from native construction |
| [PaperVizAgent](https://github.com/google-research/papervizagent) | Reference-grounded planning and visual refinement | Close research-to-visual workflow; external model/API implementation not integrated |
| [Constrained SVG refinement](https://arxiv.org/html/2608.28678) | Test refinement benefits; preserve incumbents and failures | Syntax improvements do not imply appearance improvements |
| [AesEval](https://arxiv.org/html/2603.01083v1) | Typography/layout/color/graphics and localized judgments | Model aesthetic judgments require calibration |
| [TASTE](https://arxiv.org/html/2605.20731) | Separate preference dimensions and report disagreement | Raster-design dataset; no learned scorer is deployed here |

## Evidence and milestones

1. Experiment ledger and isolated native studies.
2. Early-study profiles and relationship-aware construction, unit/native verification.
3. Calibration, freeze and all 18 pilot builds, including failures.
4. Fresh actual-image specialist reviews and owner blind package.
5. Claim/evidence ledger, manuscript, reproducible sanitized package and verified installation.

Every result is labeled proposed, implemented, technically tested, model-observed or human-observed. Technical fixtures are never artwork evidence. Hashes establish bytes, not perception or externally authenticated provenance. Reviewer contexts are model contexts; human comprehension and professional preference remain a later study gate.

Maintained records: [calibration](CALIBRATION.md), the unchanged frozen [protocol](PROTOCOL.md), [execution notes](EXECUTION-NOTES.md), [results and accounting](RESULTS.md), [human evaluation preparation](HUMAN-EVALUATION.md), [claims](CLAIMS.md), and the append-only [development log](LOG.md).

The new [development manuscript](manuscript.md) and [BibTeX bibliography](bibliography.bib) distinguish current evidence from pending pilot results. The [response to the supplied assessment](REVIEW-RESPONSE.md) maps prior-art and evaluation concerns to changes and remaining gates. These are maintained research documents; they do not replace the historical paper.

## Reproduction commands

Run Python commands with Python 3.13 from the repository root. Prepare an attributed project-local reference pack and frozen common-context.md with its sibling context-provenance.json, then commit the method before running:

```powershell
py -3.13 benchmarks/prepare_process_pilot.py --name STUDY_ID --reference-pack PACK_PATH --model HOST_MODEL --effort HOST_EFFORT --context COMMON_CONTEXT_PATH
```

Start each pending ledger trial immediately before dispatching its fresh sequential builder. All authoring uses benchmarks/process_host.py Session; it enforces the locked inputs, planned batches and shared timing. Account for every stopped or failed build before collecting and preparing anonymous comparisons with prepare_blind_comparisons.py. The frozen collect_process_results.py assumes startup files exist; a documented reporting supplement is needed for a legitimate never-initialized attempt, preserving absent files rather than manufacturing them. See EXECUTION-NOTES.md and RESULTS.md. prepare_edit_tasks.py creates separate anonymous copies for benchmarks/edit_host.py EditSession. Parent dispatch seeds the same ten-minute clock before every editor starts, including preparation. Each maintained helper exposes its arguments with --help. These scripts do not create observations, human responses or quality scores.

The maintained document sources use bundled Node docx/sharp: run build-figures.mjs then build-document.mjs with the output DOCX path. Render the saved DOCX using render-word.ps1 with explicit DOCX/PDF paths, then use bundled Poppler to inspect every page. This Windows run uses isolated read-only Word rendering because the packaged LibreOffice renderer was unavailable; the deviation and diagnostics are retained. Re-render after substantive manuscript changes. Working renders remain in outputs. Explicitly verified, dated publication editions are retained under docs/research/editions; those editions are not overwritten by later working renders.

A local source archive preserves commit 9d47373. The private exact-byte input archive separately preserves all 84 manifest files and the frozen protocol, including non-Git environment/common-context files and cached reference images. Five older skill files have checkout line endings that differ from Git archive bytes while normalized content matches; the exact-byte archive retains their frozen SHA values. Verification is outputs/research32/frozen-source-verification.json. The private input archive must not be redistributed by default because it includes third-party reference images; a sanitized sharing package is a separate artifact.
