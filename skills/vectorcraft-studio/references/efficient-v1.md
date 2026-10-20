# Efficient execution

Explicitly select `execution_profile:"efficient-v1"` with full-mode
`quality_profile:"focused-execution-v1"` (Focused build) or `"designer-process-v1"`
(Full process). Other combinations are rejected. `standard` remains the default.
This changes execution overhead, not the host model or quality requirements.

Use the current returned working packet until edits invalidate it. Request
`workflow_status {view:"working"}` when needed; `view:"full"` retrieves complete
schemas. The packet binds a hashed `run.json` reference to document/spec revisions.
Retrieve prerequisite records from its records index only when needed. Reuse
already inspected research rather than repeating the complete study every batch.
If `context_complete:false`, retrieve **every relevant omitted field before
dependent edits**. An 8 KiB target never excuses dropping a blocker, task or mapping.
Images still require actual inspection; a fresh path or hash is not perception.

Discover commands with a narrow `command_list {filter:"..."}`. Enabled states are
live and must not be cached. For individual objects use `document.node` with
`summary:true, depth:0, childLimit:0`; request deeper details only as needed.

On a verified engine with drawing batches, construct one coherent component in
at most 32 steps. Supply explicit fill/stroke, names and supported inline styles.
Use returned IDs or `$0.id` / `$last.id` references to earlier batch results.
The gateway defaults to `stop_on_error:true`, `atomic:true` and a nonempty undo
label; give a descriptive component label. **Atomic means one undo group, not
guaranteed rollback.** Inspect completed/failed/results/created. Partial failure
or timeout requires recovery inspection; never retry the batch automatically.
On 0.11 choose individually supported drawing calls before mutation. Do not probe
unsupported edits in an artwork and then fall back after they partly succeed.

Persistent saved selections are edits. Text preflight uses explicit-ID area
queries; a definite disabled query alone permits a selection-preserving fallback.
Unknown query results fail verification. Keep live text and editable vector parts.

If completion cannot be accepted, record `workflow_record {kind:"stop",
data:{reason:"...",unresolved_findings:["..."]}}`. This records
`stopped_unresolved`, preserving pending captures, findings, retained artwork and
correction counters. It grants no task/stage/final acceptance. Resume in a fresh
connection using explicit `reopen_reason` and a project `feedback_path`, within
the stored budget. Resume retains the execution profile and exact engine binary
identity. Uncertain recovery must reopen and match a new native export before
editing; a missing/mismatched snapshot is a blocker. Do not clone an exhausted run.

Connection-local `work/vectorcraft/<session>/metrics.jsonl` records counts, byte
sizes, image dimensions, durations and recovery exports without prompts/pixels.
Actual model tokens are unavailable unless a run-scoped host receipt provides
them. Do not estimate tokens from character counts or claim better aesthetics
from a smaller packet or faster engine.
