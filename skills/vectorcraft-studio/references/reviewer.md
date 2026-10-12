# Independent reviewer contract

## Designer-v1 runs

Use `workflow_record` packet, then two separate fresh specialists: `communication` and `craft`. Both return the eight criteria below, fidelity and copy assessments, plus `brief_comparison: {winner: candidate|incumbent|original|equal|no_baseline, reason}`. This common-brief judgment is separate from fidelity to the candidate's target. Include complete `incumbent_assessment` and `original_assessment` when those versions have not yet been reviewed; the same assessment can cover both when identical. Assess the original without penalizing it for an unrelated new target (fidelity may be null). View every packet full/use image and the target. An original is a legitimate best version; disagreement retains the incumbent.

The parent records `{version, reviews: [{role, reviewer_id, review, image_observation: {tool, evidence: string, observation}}]}`. Identities must be distinct and fresh for every round, including concept reviewers. In brief_comparison add `regression: {present: boolean, evidence: string}`: identify an actual consequential loss versus the retained artwork, or state why none is observed. A weakness shared by both or a different fresh reviewer's score calibration is not a regression. Earlier records without this field remain readable; never fabricate missing evidence. Describe visible regions and actionable fixes. Do not equate a score or different style with improvement, and do not force defects. The JSON remains an attestation; actual image-tool actions or delivered image attachments and observed judgments are recorded separately. Use three correction rounds maximum, stop after two non-improving rounds, deliver the strongest reviewed artwork and disclose weaknesses.

## Legacy version-three runs

For version-three gateway packets, use this contract with two additional fields: `visual_fidelity: {score: 1..5, reason: observed relationship to target}` and `copy_assessment: {score: 1..5|null, reason: subject/audience specificity and clarity}`. Include the target PNG in image_inspection.paths and actually view it. Read observable requirements and the brief; judge professional creative execution as well as technical usability. Both fields also belong in incumbent_assessment; when its original target is unknown, fidelity can be null with that reason. The new target does not redefine the original brief or establish that an old direction failed. Compare common-brief suitability separately from target matching; do not prefer a candidate merely because it follows its own target. Use identical intended-size previews. Findings can name visual_fidelity or copy_assessment. Store returned JSON in the project through the parent; reviewer tools/actions remain independent evidence, not a claim made solely by JSON. Full/use-size images of both versions are required when comparing. Do not operate editing tools, modify files or spawn further agents.

Give the reviewer this instruction with the brief and absolute evidence paths:

> Act as a candid design-school teacher reviewing student work for its stated audience and use. Read the brief and rubric. Actually view the full and intended-size images, with detail images when supplied. Read document measurements for specific geometry. Do not modify files, operate MCP editing tools, or create other agents. Do not infer the intended verdict. Judge the images rather than the creator's rationale. Return only the JSON contract below, grounded in observed evidence. If comparing, inspect both versions and choose the better fit; equal is a valid outcome. If you cannot inspect the required images, report that limitation rather than fabricate a review.

The parent uses `studio_run.py packet` to supply neutral A/B evidence copies without version history or previous scores. The helper accepts these copies by verifying their image hashes against the immutable snapshots. Reviewer `fork_turns` must be `none`. Parent checks the reviewer viewed the images using `view_image` or an equivalent supported image-inspection tool before recording the review. Reviewers only return text; the parent writes their response and makes edits.

Return this shape (all eight rubric keys required; numeric scores are integers 1..5):

```json
{
  "image_inspection": {
    "performed": true,
    "paths": ["absolute/path/full.png", "absolute/path/use-size.png"],
    "observations": ["Concrete visible observation about this artwork"]
  },
  "scores": {
    "brief": {"score": 4, "reason": "Evidence"},
    "composition": {"score": 4, "reason": "Evidence"},
    "alignment": {"score": 4, "reason": "Evidence"},
    "typography": {"score": null, "reason": "No text in this symbol"},
    "color": {"score": 4, "reason": "Evidence"},
    "style": {"score": 4, "reason": "Evidence"},
    "distinctiveness": {"score": 4, "reason": "Evidence"},
    "craft": {"score": 4, "reason": "Evidence"}
  },
  "findings": [
    {"criterion": "alignment", "severity": "minor", "location": "Region or object id", "evidence": "Observed relationship", "impact": "Why it matters", "fix": "Actionable correction"}
  ],
  "comparison": {"winner": "no_baseline", "reason": "Initial assessment; no incumbent"},
  "summary": "Short overall judgment and remaining weaknesses"
}
```

For comparison, winner is `candidate`, `incumbent` or `equal`; `no_baseline` is only for the first assessment. Findings may be empty for a resolved design. `preference` is allowed for explicitly subjective comments and is not a major defect. Never omit real problems to satisfy a threshold. If image inspection is unavailable, return `image_inspection.performed: false` and explain why; the parent must mark review unavailable instead of recording a pass.

## Research-led version-two runs

Critique is final-only. There is no external concept-selection or unfinished baseline review. The locked brief specifies intended use and style; the reviewer should not receive the creator's research narrative, persuasive rationale or scores. Research provenance is audited separately by the parent. After images and exports have been inspected, review the first completed candidate.

If comparing with a supplied untouched original on this first final assessment, return the ordinary top-level candidate review plus `incumbent_assessment`: a complete review of image B using the same eight-factor JSON contract, with its own image paths, findings, scores, summary and `comparison.winner: no_baseline`. Top-level comparison chooses candidate, incumbent or equal. Inspect both at use size. This establishes the original's independent assessment at the end, without requiring a teacher to direct initial design choices. On later corrections, compare against the recorded best; no embedded assessment is needed.
