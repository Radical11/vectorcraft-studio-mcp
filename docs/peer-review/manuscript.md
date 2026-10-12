# Preserving design intent in agent assisted vector graphics

Research style report and prospective algorithm proposal

## Abstract

Agent assisted vector design can lose its central idea between reference research, a verbal plan, and the native document. A technically valid file may retain the requested objects while losing their gesture, hierarchy, or relationship to the copy. This paper documents an experimental companion around an existing vector editor. The contribution is a workflow enforcement and evidence system, not a newly trained graphics model. It connects inspected references and a selected visual target to concrete object mappings, revision-bound previews, independent critique, and retained versions. [10,11]

The development moved from instruction-led helpers to version-three enforcement and a stricter designer-v1 contract. Reported software evidence comprises 124 Windows checks, including 113 self-contained checks and 11 native integration checks. Hosted Linux CI exercises the self-contained subset. These counts concern behavior and compatibility, not aesthetic quality. In three fixed release briefs, two fresh model reviewers preferred the retained revised version in every matched comparison, and one owner made the same anonymous selections. Historical comparisons were mixed: an original infographic remained stronger, and an editorial revision improved recognition while losing cohesion. [10]

A future method is proposed: rough layouts, coarse two-dimensional vector studies, semantic decomposition, relationship-aware progressive assembly, and whole-scene critique. Object and part decomposition, relational geometry, purposeful prototypes, and raster/vector comparison provide relevant principles, but their published neural or optimization systems are not integrated here. [1–5] The proposal is specified through invariants, pseudocode, a repair-café example, and an unrun 54-output evaluation protocol. The current evidence supports feasibility of the companion and specific observed improvements; it does not establish general professional superiority or human-level design judgment.

Keywords: vector graphics; design intent; Model Context Protocol; semantic decomposition; visual critique; reproducibility.

## Scope and reading guide

Sections 1–10 describe the released system and recorded results. Sections 11–13 describe literature and future work. Appendices define prospective records and evidence access. No future algorithm experiment was run for this paper. The two editions share this manuscript; identifying project links appear only in the public edition. The manuscript is intended for peer review rather than presented as a peer-reviewed publication.

<!-- PAGE -->
## 1 Problem and contribution

The motivating observation was concrete: output copy felt interchangeable, layouts felt crowded, and an illustration described during planning did not reliably survive construction. A plan such as “two students repair a radio together” is underspecified. It says little about where the gaze converges, which hand steadies the case, or whether the screwdriver tip actually meets a screw. An agent can satisfy the object list without communicating the activity. The project treats this gap as loss of design intent. [10]

For this paper, design intent means the brief-specific relationships and visual choices needed for communication: exact content, reading order, focal silhouette, meaningful gesture, image treatment, and production requirements. Intent is not identical to pixel similarity with a target. A revised artwork may communicate the brief better while departing deliberately from its reference. Conversely, a visually close reconstruction may obscure required information. The system therefore records target fidelity separately from common-brief suitability. [11]

The released contribution has three parts. First, a gateway makes important workflow prerequisites inspectable and enforceable before substantial authoring. Second, structured specifications connect intentions to native document objects and current previews. Third, independent review compares a candidate with retained artwork and, when available, an untouched original. An original is allowed to win. Evidence and lessons remain linked to their context rather than becoming universal style prescriptions. [10,11]

The host agent supplies research, copy development, image generation when available, and design judgment. The gateway checks records, document identity, revision state, and authoring routes. The existing editor supplies paths, live text, document operations, rendering, and exports. No model weights were trained, no new renderer was introduced, and no separate paid model API is required by the companion. These boundaries matter when assessing novelty and attributing capabilities. [8,11]

The guiding questions are practical. Can workflow enforcement reduce skipped steps and stale evidence? Do matched examples show communication and craft gains rather than mere stylistic differences? What representation would make interaction failures easier to detect before expensive drawing? The existing checks address the first question. The small case series offers observations about the second. The coarse-to-fine proposal and its future protocol address the third; they do not answer it experimentally.

An auditable decision rationale records the constraint, alternatives, chosen action, observed consequence, and remaining uncertainty. That is the meaning of “thinking process” in this paper. It does not claim access to hidden model reasoning or reconstruct undocumented personal intentions. Historical outcomes are retained even when they conflict with the desired improvement narrative. [10]

<!-- PAGE -->
## 2 Development history and consequential decisions

The preserved import identified gateway version 1.0.0 and Studio helper version 2. Earlier helper instructions already described research, thumbnails, construction, independent review, and a bounded correction loop. The later work did not invent those activities. It addressed weak enforcement and incomplete links between planning, edits, previews, and conclusions. The import archive was hashed and retained separately; 398 archived files were verified unchanged. [10]

!FIG[1](figures/01-timeline.png)

Figure 1. Recorded progression. Dates are local calendar dates; the pre-import helpers have no inferred development date. Arrows show development succession, not measured causal effects.

Version three introduced five workflow tools, structured run records, concrete object mappings, stage checkpoints, and edit invalidation. An early acceptance problem revealed that unequal comparison sizes could change the apparent winner. Reviews were repeated at equal intended dimensions. They judged the rain poster equal and preferred the original beginner infographic. The original was retained rather than forced through another cosmetic correction. [10]

The designer-v1 contract then added calibration, developed alternatives, concept review, and a representative construction study. Native focal construction became the preferred route when tracing lost contours. In the historical editorial example, tracing produced approximately 69,770 anchors; cleanup and selective reconstruction left approximately 27,925. Lower complexity alone did not prove better drawing. Fresh revisits found clearer subjects and a visible loss of stylistic cohesion. [10]

A further correction concerned review semantics. A score decrease across fresh reviewers could reflect different calibration, not an observed regression. The current contract requires explicit evidence of a consequential loss and keeps common-brief voting distinct from score thresholds. Disagreement retains the incumbent; an observed consequential regression can also prevent candidate promotion. The alpha release followed software checks, corrected comparisons, and the owner's anonymous artwork choices. [10,11]

<!-- PAGE -->
## 3 Architecture and responsibility boundaries

The system is an unofficial community companion for Codex on Windows and a separately installed VectorCraft CLI and desktop editor. It is not an upstream feature, a browser editor, or a graphics foundation model. The documented local integration uses Python 3.13 and VectorCraft 0.9. Hosted CI does not establish native support on other operating systems. [8,10,11]

!FIG[2](figures/02-architecture.png)

Figure 2. Current responsibilities. Dashed vault connections represent contextual knowledge retrieval and attributed lesson writing. The host observes images; the gateway cannot verify perception from hashes.

The host reads briefs, inspects accessible references, chooses a direction, invokes editor operations, and observes renders. Skills describe when substantial work should enter Studio and when a narrow edit should stay lightweight. Initialization instructions reinforce the workflow while preserving the native server's identity, instructions, resources, prompts, and command discovery. Official MCP guidance is relevant to this instruction placement; the project supplies the particular design policy. [7,8,11]

The gateway tracks a project-scoped run, document identity, specification revision, document revision, pending operation state, and evidence artifacts. Native operations are passed through the existing engine after applicable workflow checks. The knowledge vault preserves attributed source material and contextual lessons with immutable-source and concurrent-write protections inherited from the helper system. It does not become a training dataset or an automatically learned style model. [11]

Portable discovery resolves configured engine and manifest locations rather than assuming that gateway relocation moves the applications. The installer accepts CLI, desktop, Codex home, and vault paths, supports dry runs and selected rollback snapshots, and changes only the owned VectorCraft MCP settings and two owned skills. Backups remain private. Rollback preserves unrelated settings and detects later changes to owned files. [10,11]

<!-- PAGE -->
## 4 Current research build and critique method

Full runs begin with purpose, audience, medium, viewing size, required content, factual constraints, and desired character. Required wording is separated from editable copy. Calibration connects three to five actually inspected references to hierarchy, silhouette, gesture, typography, and image treatment. A reference count does not demonstrate understanding. Unavailable sources must be recorded honestly. [11]

!FIG[3](figures/03-current-workflow.png)

Figure 3. Current full workflow. Calibration and concept review precede the target and specification; an observed construction study is required before substantial imagery. Quick edits record their limited scope.

Three developed alternatives contain actual copy, composition, and image treatment. They must differ in the idea and reading experience, not only in color. A fresh concept reviewer compares them against the brief and references before autonomous direction selection. One extra exploration pass is permitted when all alternatives are weak. The target is a developed vector study or a generated illustration reference; final typography remains independently editable. [11]

The specification records placements, type roles, palette, focal features, exact copy, and semantic elements. Construction proceeds through composition, typography, imagery, and finishing, with a render and observed comparison after meaningful stages. Copy is assessed for specificity, clarity, tone, its image relationship, and subject substitution: would the same slogan still work if the subject changed? This is a diagnostic rather than a formula for good writing. [11]

Independent specialists assess communication and craft. Their packets exclude creator scores and persuasive explanations. The system retains eight criteria and adds explicit copy, target-fidelity, and common-brief judgments. Corrections address consequential findings; already resolved work need not receive forced negative findings. Three correction rounds are available, with a stop after two non-improving rounds. The screenshot, inspection, correction, and verification pattern also has precedent in design tooling. [9–11]

<!-- PAGE -->
## 5 Interface contracts and evidence records

The maintained interface has five workflow tools. Native command, resource, and prompt routes remain available. New full version-three runs default to quality_profile designer-v1; earlier records without that field keep their existing requirements. Version-one and version-two helper contracts and historical records are preserved. Proposed records later in this paper are not accepted record kinds in the current release. [11]

| Tool | Current responsibility |
|---|---|
| workflow_start | Create or resume a project-scoped full or quick run and associate its document |
| workflow_record | Attach research, calibration, alternatives, concept review, target, specification, study, preflight, packet, review, or unavailability evidence |
| workflow_begin | Declare the next construction stage, intended edits, and semantic object mappings |
| workflow_checkpoint | Capture then confirm native and full/use-size evidence for the current stage |
| workflow_status | Expose current revision, readiness, pending state, retained best, and configured vault |

Table 1. Tool responsibilities, summarized from the version-three implementation. This is a conceptual contract summary, not a replacement for discoverable parameter schemas. [11]

Prerequisite enforcement applies to command aliases, individual batch steps, convenience authoring tools, and UI edit routes. Inspection and controlled document setup remain possible. Mixed batches cannot make a later edit legitimate merely by beginning with a read. Originals are preserved before editing. Partial failures and document switches are treated as state changes, not silently ignored. [10,11]

A semantic mapping links a requirement such as “visible screwdriver contacting screw” to actual native objects. It is stronger than a narrative layout note because inspections can locate the mapped objects. Nevertheless, an object ID proves neither a convincing grip nor readable contact. The record needs an observed preview, and the reviewer still judges the visible relationship. Current mappings are not an explicit geometric constraint solver. [11]

Evidence has different epistemic roles. File hashes identify bytes. Document inspection reports object kinds, text, and bounds. Fixture assertions test rejection or acceptance behavior. Image observations describe what an agent actually inspected at full and intended size. Specialist judgments compare meaning and craft. Treating these categories as interchangeable would turn a valid file into an unsupported quality claim.

The strongest chain is requirement → chosen visual feature → mapped object → current render → observation → correction → reviewed version. Missing links should remain visible. The chain supports accountability and repeatability; it cannot compel an agent to notice every visual defect or guarantee that the reviewer has expert taste. [10,11]

<!-- PAGE -->
## 6 Revisions snapshots and interrupted work

Workflow evidence is bound to both the document and the current revision. A confirmed render from an earlier document state cannot authorize a final review of later edits. Changes clear review readiness. Preflight requires a confirmed current snapshot with no pending edits and matching specification state. This protects against stale previews rather than grading the design. [11]

!FIG[4](figures/04-revision.png)

Figure 4. Current revision and readiness logic. Saved versions remain retained evidence; new edits invalidate readiness, not the existence of those versions. Capture and observation confirmation are separate steps.

Capture saves native artwork and full/use-size previews. Confirmation adds actual visual observations, checks mapped components, and records deliberate departures from the target. Preflight then checks exports, exact content, fonts and bounds, editability, and vector-only requirements. A review packet is assembled from the eligible candidate, retained best, and untouched original when different. A subsequent edit requires new evidence before review readiness can be restored. [11]

Recovery prioritizes certainty over optimistic replay. Pending or partly completed actions are marked uncertain; interrupted work resumes by inspection and reconciliation with the document state. Uncertain operations are not automatically repeated. Connection-specific document ownership and desktop handoff prevent one connection's recovery from acquiring another connection's work. Filesystem roots remain ordinary project boundaries. [10,11]

This design accepts that the host can crash, a batch can partly succeed, or a user can switch documents. The appropriate response is not to assume an empty transaction. The agent must inspect what exists, preserve the best known version, and reconcile its plan with the observed state. The live Windows recovery checks and fixture tests exercise these mechanisms, although they cannot enumerate every possible editor interruption. [10]

<!-- PAGE -->
## 7 Construction typography and production judgment

A generated illustration target can help define expression, lighting, or gesture. It is saved and inspected before vector construction, and kept separate from final artwork. Typography is composed with live text after image decisions rather than baked into the generated bitmap. The reference is an instruction-bearing artifact, not a permitted raster substitute for a vector-only deliverable. [11]

The historical trace failure explains the construction policy. Whole-image tracing preserved many color fragments but damaged important contours and produced a heavy document. Simplification alone could not recover the cyclist's limb and frame relationships. Selective native rebuilding made the subject clearer, but replacing only some shapes introduced clean edges into a textured setting. The fresh comparison therefore exposed a second problem: local recognition and whole-scene cohesion can move in opposite directions. [10]

The current workflow asks for a representative construction pilot before substantial imagery. Native paths are preferred for focal subjects and coherent geometric components. Suitable flat imagery may be traced and expanded, but the pilot must show whether important contours and details survive. Textured references call for meaningful shape reconstruction rather than an automatic whole-image trace. A method choice should be justified by observed results and editable structure, not by nominal path count. [11]

Typography uses available fonts and actual bounds. Overflow is corrected by improving wrapping, placement, or the copy when rewriting is allowed, before shrinking text. Required content cannot be silently abbreviated. Font substitution, altered mandatory wording, missing mapped components, excessive trace artifacts, and embedded raster content are relevant production defects. Fixtures exercise rejection logic for such cases; actual image inspection is separately needed to determine readability and quality. [10,11]

The native final should reopen with paths and live Type objects. SVG should retain editable vector structure and text, and PDF should preserve the visual result without a flattened image. Intended-size PNG is a viewing export, not the editable master. The release evidence reopened all six selected native files and checked the SVG/PDF structures, then observed their rendered appearance. [10]

Those checks establish useful but limited facts. A zero raster count does not imply elegant drawing. More objects do not imply semantic organization. A fitted text box can still have weak hierarchy. Conversely, a wordless illustration legitimately has no live text. Professional evaluation needs these structural checks together with a judgment of what viewers can recognize, understand, and use at the specified size.

<!-- PAGE -->
## 8 Independent review and retained best selection

The eight inherited criteria are brief suitability, composition, alignment, typography, color, style, distinctiveness, and craft. Brief-specific quality profiles emphasize expressive posters, editorial illustrations, or information graphics without prescribing a universal style. An interchangeable functional result is insufficient for an expressive brief. Scores organize review but cannot independently establish improvement. [11]

!FIG[8](figures/08-selection.png)

Figure 5. Current retained-best and stopping logic. Candidate promotion requires agreed common-brief preference without an observed consequential regression. The original can be the retained version; “passed” and “best” answer different questions.

A fresh communication reviewer examines message, hierarchy, copy, and direction. A separate craft reviewer examines drawing, contours, geometry, typography, and production. Findings need a visible region, a consequence, and an actionable correction. Reviewers compare the candidate and prior artwork without creator self-scores. Process reviews also see the target; the final anonymous release comparison withheld targets and creator histories to reduce direction preference. [10,11]

The review contract's correction is consequential. A lower score, or a weakness present in both versions, does not by itself establish regression. The reviewer must describe a new material loss against retained artwork. If both reviewers prefer the candidate but either reports such a regression, the incumbent is retained. When reviewers disagree, the incumbent remains. This is intentionally conservative and can retain a version despite a locally improved feature. [11]

Corrections are bounded. A resolved retained version can stop; two successive corrections without promotion stop further iteration; three correction rounds exhaust the budget. Delivery includes the retained best and unresolved weaknesses. The repair example exhausted its budget with moderate target fidelity rather than being called fully resolved. Fresh context helps avoid creator persuasion, but same-model reviewers can still share biases and omissions. [6,10]

<!-- PAGE -->
## 9 Software verification and reproducibility

The local Windows report records 124 passing checks. Of these, 113 are self-contained and 11 require native Windows integration. Linux-hosted CI runs the 113 subset plus public packaging and site validation. These are separate scopes; the hosted result is not a second native 124-check run. The historical report timestamp and environment are preserved in the sanitized evidence. [10]

| Suite | Checks | Evidence type |
|---|---|---|
| Workflow version three | 37 | Self-contained fixtures |
| Designer contract | 23 | Self-contained fixtures |
| Portable installation | 14 | Self-contained fixtures |
| Legacy version one | 15 | Self-contained fixtures |
| Legacy version two and vault | 24 | Self-contained fixtures |
| Native MCP passthrough | 3 | Live Windows integration |
| Gateway workflow | 3 | Live Windows integration |
| Desktop handoff | 1 | Live Windows integration |
| Desktop recovery | 4 | Live Windows integration |
| Total | 124 | 113 self-contained plus 11 live |

Table 2. Recorded software suite. Counts describe checks, not independent users, design trials, or aesthetic judgments. [10]

Coverage includes skipped prerequisites, aliases and mixed batches, stale evidence, switching documents, partial failures, interrupted runs, earlier contract compatibility, installer discovery, clean configuration, rollback conflicts, and native passthrough. The installer was verified from a clean public checkout without access to the private baseline. It preserves unrelated settings while restoring owned configuration and skill bytes. [10]

Fresh-session activation was checked in two ways. A substantial request selected Studio through a routing probe; that probe was not a complete fresh-session artwork build. A smaller-model quick-edit run changed only three ellipse fill channels and the document modification timestamp, leaving text and geometry unchanged and requiring no research. These results distinguish activation evidence from end-to-end design evidence. [10]

Public source, selected examples, and sanitized relative-path evidence are distributed; raw run records, local configuration, backups, and vault sources remain private. The source package identifies public file hashes. Reproducibility still requires separately installed compatible editor binaries, fonts, host capabilities, and access to references. Exact artistic reproduction is not guaranteed by deterministic software checks. [10,11]

<!-- PAGE -->
## 10 Visual evaluation design

Three fixed release briefs tested an expressive campus-event poster, a wordless repair-café illustration, and an educational urban-heat infographic. Their content, dimensions, and viewing sizes were locked before profile tuning. Calibration examples were separate. Baselines used the preserved pre-3.1 gateway; revised candidates used designer-v1. Both sides received critique and consequential corrections. They are creator-authored case studies, not randomized independent-agent trials. [10]

The poster used a 900 × 1200 canvas and 450 × 600 viewing preview. The repair scene used 1536 × 1024 and 768 × 512. The heat infographic used 1200 × 900 and 600 × 450. Six native files and their exports were inspected. Poster files each had eight live text objects; the heat baseline had eleven and the revised file twelve. Both repair files were wordless. Native/SVG/PDF finals contained no embedded raster substitute. [10]

The final comparison used randomized neutral labels and equal full/use-size views. Two fresh gpt-6.1-sol reviewer contexts each observed twelve images and received the brief, factual constraints, and document inspections. They did not receive creator scores, targets, histories, or an expected verdict. The two roles independently agreed on clear common-brief improvement in all three cases and observed no consequential regression in the retained revisions. One owner then selected Q for the poster, P for repair, and Q for heat; these labels mapped to the revised versions. [10]

The gate had required agreement on at least two improvements and no consequential regression in the remaining brief, followed by the owner's anonymous review. It was satisfied for this release set. This is an operational launch decision, not a statistical estimate of professional quality. The same model family can share biases; a single owner provides a preference, not a peer panel. No controlled human study was conducted. [6,10]

Calibration coverage was three inspected references per brief, below the broader 15–25-work aspiration. Vault lessons were retrieved during critique rather than before initial construction. The study therefore cannot claim full execution of every ideal research behavior. Equal content and size do not remove creator involvement, unequal artistic choices, or training-distribution effects. Those qualifications apply to the comparisons on the next three pages. [10]

The paper reproduces the already released artwork without changing its drawing. Printed figures scale the previews to fit a page and are not a new intended-size evaluation. Captions disclose this distinction. The public reproducibility links provide the original pixel-size previews, live-text native files, SVG, PDF, and neutral review records. [10,12]

<!-- PAGE -->
## 10 1 Campus poster comparison

!PAIR[campus-poster]

Figure 6. Released campus poster baseline on the left and retained revision on the right. Both preserve the fictional AFTER DARK night-walk brief. Reproduced from 450 × 600 previews and scaled equally for print; not a new evaluation. [10]

The revised walker, torch body, and beam establish a clearer action and direct attention to a recognizable moth. Supporting copy names moths, shadows, and a familiar path seen differently; the image supports that wording. Both reviewers preferred Q and described a stronger reading route while retaining date, time, meeting point, and free-entry information. The owner also selected Q. [10]

The revision is not flawless. Reviewers noted ambiguous oversized leaves, simplified angular joins, and a rear shoe that appears weakly grounded. The scene does not independently establish a campus through architecture. These observations restrict the conclusion to better communication of the specified night-walk activity, not superior illustration for every poster purpose. [10]

<!-- PAGE -->
## 10 2 Repair café comparison

!PAIR[repair-cafe]

Figure 7. Released wordless repair scene baseline on the left and retained revision on the right. Original review previews were 768 × 512. Both include two students, an opened tabletop radio, a supporting hand, and tool contact. Scaled equally for print. [10]

The retained revision brings the faces and hands toward one shared focal object. The case reads as an opened radio rather than a shallow tray, with grille, knobs, wires, and a removed panel. A continuous screwdriver shaft meets a visible screw; a second hand steadies the casing. Both reviewers selected P and described better collaborative attention and object relationships. The owner selected P. [10]

Three correction rounds were used. The retained version improved the common brief but stopped with budget_exhausted and moderate target fidelity. The long diagonal right forearm, crowded grip, stylized finger contours, spare-tool geometry, and dense tiny components remain limitations. Target fidelity and brief communication should therefore be reported separately. [10]

This example motivates the future proposal without validating it. Local parts can look plausible in isolation while the whole action remains difficult to parse. A pre-detail hand–driver–screw contact study could expose the risk earlier. Whether explicit relationship records reduce these defects requires the planned experiment; the current scene was not produced by that proposed algorithm.

Adding more micro-components is not an adequate correction when the grip or posture is weak. The proposed refinement order prioritizes contact, gesture, and coherent focal contours before texture or bench detail. This is a design inference from the observed weaknesses, not a measured result. It can also fail if an overly rigid blockout fixes an awkward pose too early; the future method must permit revising the coarse study.

<!-- PAGE -->
## 10 3 Urban heat comparison

!PAIR[urban-heat]

Figure 8. Released urban-heat baseline on the left and retained revision on the right. Review previews were 600 × 450. Required mechanisms are shade and evapotranspiration; content avoids an unsupported numerical cooling claim. Scaled equally for print. [10]

The revised composition strengthens the causal reading of sun, canopy, shaded ground, roots, and rising moisture. The release reviewers agreed that the revised version better explains the educational brief without a consequential loss of factual qualification. Their Q selection matched the owner's Q preference. The text-bearing files remain editable, and the revised version retained twelve live text objects. [10]

The comparison concerns explanation as well as appearance. A stronger diagram should make its causal relationships visible instead of asking the viewer to infer them only from labels. Larger type and clearer routes can help, but arrows can also imply unwarranted certainty. The factual wording and qualified mechanism remain constraints rather than decorative content that may be rewritten freely. [10]

The historical rain-garden infographic provides a counterexample to universal improvement. Its original had a clearer numbered sequence and water annotations for beginners, even after the rebuild passed individual review. Passing a rubric or resembling a new target did not make the candidate the better teaching graphic. Retained-best selection must compare the same brief and intended audience, including the original when available. [10]

These results support release of the selected cases with limitations. They do not establish that all infographics benefit from this composition, that more native text objects improve learning, or that model preference predicts student comprehension. A comprehension task with human participants is a prospective evaluation measure, not a result of this release.

<!-- PAGE -->
## 10 4 Historical outcomes and threats to validity

Historical revisits are essential because an improvement story based only on the three favorable release pairs would conceal earlier failures. The rain poster was equal for the communication reviewer and favored the original for craft. Both reviewers preferred the original rain-garden infographic. The repaired editorial subject became clearer, yet both observed a consequential cohesion regression. The communication reviewer withheld an unqualified improvement; the craft reviewer favored recognition while still recording that regression. [10]

The editorial failure is specific: smooth rebuilt subject and building shapes contrasted with fragmented foliage, water, and surrounding architecture. Repeated clean windows and isolated reflection marks appeared pasted into the scene. Focal reconstruction solved part of the problem but lost the shared edge and lighting treatment. Anchor reduction did not measure that loss. This is why local and whole-scene inspection both matter. [10]

The comparison-size correction and the score-based regression correction changed decisions, not merely documentation. Equal viewing dimensions challenged early favorable verdicts. Explicit observed-regression evidence replaced inference from score movement across reviewer contexts. These are recorded design rationales supported by artifacts and implementation; neither is evidence that future reviewers will be unbiased. [10,11]

The principal validity threats are a small purposive case series, one creator using both routines, limited inspected references, shared model-family judgments, and one owner preference. Baselines were preserved and corrected, but the study was not blinded during creation or replicated across independent designers. Artwork ratings were not calibrated against a controlled human panel. No effect size, confidence interval, or significance claim is justified by these records.

The system also depends on host capabilities. A reviewer can attest to images without noticing a defect; file validation cannot prove sincere inspection. Native editability does not automatically mean convenient editability, especially with thousands of anchors. Reference access can fail, and the current system does not infer a robust interaction graph from the artwork. Recovery and installer checks are bounded demonstrations, not exhaustive proofs. [10,11]

Codex assisted implementation, research synthesis, diagram and manuscript preparation, construction, and model review. Human input established the problem, constraints, release expectations, and anonymous final preferences. The reviewers were fresh contexts of the same model family, not independent human experts. The paper reports that assistance explicitly rather than implying wholly manual authorship. Publication is unofficial; the upstream maintainer proposal remains prepared and unsent. [10,12]

<!-- PAGE -->
## 11 Related work and borrowed principles

SVGDreamer++ uses hierarchical image vectorization to separate objects and finer parts, together with adaptive primitive control and optimization-guided synthesis. Its decomposition suggests that editable structure should follow meaning. The proposal below borrows that principle, not its segmentation, diffusion guidance, or training procedure. An agent-authored hierarchy with native object IDs has different mechanisms and must be evaluated independently. [1]

SketchGraphs represents two-dimensional CAD primitives and designer-imposed geometric constraints as graphs. It offers a useful distinction between shapes and the relationships connecting them. Here, a contact or occlusion relationship concerns visual communication, not necessarily a CAD constraint solvable to exact dimensions. The companion does not import the dataset or run its learned constraint models. [2]

diffvg bridges vector parameters and raster observations through differentiable rasterization. Its project demonstrates that image-space objectives can inform vector editing. This proposal instead uses editor renders and agent observations; no differentiable renderer or gradient loss is installed. Pixel agreement may be useful diagnostically, but cannot independently establish readable copy, sound metaphor, or credible tool contact. [3]

NeuralSVG describes a neural scene representation and regularization intended to make shapes independently meaningful within a layered SVG. That is relevant to avoiding arbitrary fragmentation. Its learned representation and score-distillation mechanism are different from explicit entity records and native editor construction. The abstract, rather than the full method, was inspected for this comparison; no experimental detail is inferred. [4]

Camburn and colleagues review purposeful prototyping and connect prototype choices with the questions being investigated. This supports giving each coarse study a specific test: hierarchy, silhouette, gesture, or contact. It does not prove that coarse studies improve agent-made posters. Alipour and Faizi describe an intermediate sketching approach to fixation in an architectural student context. Its publisher abstract was inspected; the analogy motivates alternatives without transferring its human-study outcomes to this project. [5,13]

Zheng and colleagues identify position, verbosity, and self-enhancement biases in language-model judging and examine mitigation through evaluation design. Their task is language assessment, not vector-art appraisal. The future protocol therefore counterbalances order, limits persuasive explanations, separates creator and reviewer contexts, and includes a voluntary human panel rather than assuming the published agreement findings apply here. [6]

The distinct contribution is integration of inspectable workflow contracts with an existing vector editor and host agent. The literature supplies representation and evaluation principles. The release supplies a small observed case series. The proposed algorithm supplies a testable extension. Keeping those roles distinct prevents borrowing credibility from results that were never reproduced.

<!-- PAGE -->
## 12 Proposed coarse to fine method

The future method would externalize composition and interaction before detailed drawing. Its input is a locked brief, attributed inspected references, exact versus editable copy, canvas and viewing dimensions, production constraints, and a fixed resource budget. Its output would be a reviewed native vector document, live text, exports, entity mappings, observations, and unresolved limitations. This method is proposed and unimplemented.

!FIG[5](figures/05-proposed-pipeline.png)

Figure 9. Proposed pipeline. Every stage is prospective. “Coarse” means temporary two-dimensional silhouettes and geometry, not a required polygonal final style or a three-dimensional scene.

Rough layouts would record normalized positions and sizes, reading order, actual copy blocks, and negative space. Three alternatives would change the idea or reading experience. Coarse native studies would test subject proportion, gesture, and interactions using simple forms. Concept review would then select a study, refine its visual target, and preserve the meaning-bearing features before decomposition.

The selected scene would be decomposed into objects, meaningful parts, and native primitives. Build dependencies would define what must exist before a later part is constructed. Spatial relationships would separately describe contact, containment, alignment, and occlusion. Dependencies must be acyclic for a feasible assembly order; contact relationships can contain cycles. A grasp is not a reason to impose a cyclic build order.

Progressive assembly would establish focal forms and critical interactions first, then context and details visible at use size. Each meaningful batch would receive local inspection and a whole-scene render. Refinement would prioritize a missing contact or unreadable silhouette over invisible texture. The retained-best and stopping rules would remain bounded. A failed coarse study could be revised rather than treated as immutable permission to add detail.

Invariants are exact required copy, live editable text, vector-only final artwork, mapped meaningful entities, preserved critical relationships, current revision-bound evidence, and honest unresolved findings. Geometry checks would flag risks, not replace visual judgment. The hypothesis is that early representation makes consequential losses easier to see and correct; the paper reports no test of that hypothesis.

<!-- PAGE -->
## 12 1 Semantic entities and relationship preservation

!FIG[6](figures/06-hierarchy.png)

Figure 10. Conceptual repair hierarchy. A part is defined by meaning and editability. A coherent hand contour need not be fragmented into arbitrary fingers or tiny polygons.

!FIG[7](figures/07-relationships.png)

Figure 11. Conceptual relationship graph versus assembly dependencies. Contact edges describe the final interaction; directed dependency edges define a feasible build sequence. The two graphs answer different questions.

For a conceptual repair study, place the radio near the lower center, faces above it, and a bench across the lower field. Record an illustrative normalized radio box (0.38, 0.48, 0.27, 0.22), with origin at the upper left. These are proposed coordinates, not measurements of the released scene. The support hand overlaps the case; the gripping hand surrounds a handle; the shaft follows the chosen gesture toward a screw.

Each entity would have a stable ID, role, parent, bounds, anchors, critical features, and native object mappings. The screw anchor and driver tip must share visible contact within an explicitly recorded tolerance; occlusion must keep the tip readable. Construct the case and screw anchor first, then shaft and handle, then the grip and support contours. Updating the pose would revisit contact and the whole scene, not just move one hand.

“Atomic” means the smallest useful editable unit for this brief. It does not mean the smallest mathematically possible primitive. Decomposition is excessive when it destroys coherent contours, increases selection effort, or produces detail that disappears at viewing size. The proposed graph should support artists' correction decisions rather than enforce uniform geometric neatness.

<!-- PAGE -->
## 13 Prospective evaluation and technical appendix

Nine unseen briefs would cover three posters, three editorial scenes, and three information graphics, with references disjoint from calibration examples. Three conditions would be current 3.1, a layout/blockout-only extension, and the complete proposed method. Two independent builds per condition yield 9 × 3 × 2 = 54 outputs. This protocol is unrun. Content, dimensions, intended size, host model version, references, tool access, and total time/token/correction budgets would be matched and logged.

Randomize build order and counterbalance left/right comparison order. Fresh model contexts would inspect neutral full/use previews and document structure without creator scores or condition names. A voluntary peer panel would receive the same briefs and viewing instructions; participants could decline, and identifying responses would not be published. Record relevant design experience without claiming expert status. Do not infer a population effect from nine briefs.

Communication and craft ratings would use anchored descriptions plus visible-region reasons. Count consequential relationship defects, exact-copy failures, raster substitutes, and editability failures separately. For graphics, add short comprehension questions. Log build effort, object count, correction rounds, and practical editing tasks. Analyze paired results by brief and report both builds, disagreements, failed outputs, and missing observations. Predeclare the decision rule and any exploratory analyses before production. Order-swap reviews and human/model disagreement checks address possible biases. [6]

### Appendix A Proposed algorithm and evidence records

```text
INPUT brief B, references R, budget U, constraints C
L := develop three rough layouts with actual copy
S := construct coarse studies for L; inspect full and use views
T := independently review S; select and save target/specification
E, Gspatial, Gbuild := decompose T by meaning
assert Gbuild is acyclic; map critical anchors and features
best := preserve original when available
for batch in focal-first topological assembly(E, Gbuild):
    check remaining U; stop and disclose if exhausted
    build native paths/live text; inspect local and whole scene
    repair meaning-bearing losses; refresh revision evidence
for round in initial review plus at most three corrections:
    preflight; obtain fresh communication and craft comparisons
    retain common-brief best including original
    stop if resolved, budget used, round 3, or two without gain
    otherwise correct highest-impact visible findings
OUTPUT best, exports, mappings, observations, limitations
```

Proposed workflow_record extensions are layout (boxes/copy/reading order), blockout (study files/gesture observations), entity_graph (parents/anchors/two graphs), and assembly (batch mappings/relationship checks). None is implemented. A future schema would preserve the five-tool interface, explicitly version the contract, and keep existing runs on their prior requirements. Prospective relationship tolerances would be brief-specific, not universal pixel constants. Geometry failure would trigger inspection rather than an aesthetic score.

<!-- PAGE -->
## References and evidence appendix

!REFERENCES

### Appendix B Evidence access and interpretation

Evidence labels [10] and [11] refer to implementation artifacts rather than scholarly validation. The evidence index maps chronology, suite counts, activation, rollback, artwork structure, historical losses, and final comparisons to relative files. Public records are explicitly sanitized derivatives; private paths, raw logs, and identifying commits are excluded. The blind edition removes identifying project links and personal metadata, but cannot guarantee that already public artwork is unrecognizable.

!EDITION

Full HTML methods were inspected for SVGDreamer++, SketchGraphs, and LLM-as-a-Judge; the prototyping review was inspected in publisher PDF form. diffvg was inspected through its author project and abstract. NeuralSVG and the middle-sketching study were inspected through abstracts only. No inaccessible full-text experimental claims are asserted. All eight technical diagrams are original explanatory drawings; Figures 9–11 are conceptual. Comparison Figures 6–8 reuse released project assets without changing the artwork. No publisher figures, font files, or upstream branding assets are distributed.

Reproduction distinguishes software behavior from visual replication. Run the self-contained Python checks, configure compatible separately installed native software, and inspect the selected native and exported files. The 54-output proposal remains future work. Peer review should challenge the evidence chain, threat handling, and proposed evaluation rather than treating favorable model scores as proof of professional competence.
