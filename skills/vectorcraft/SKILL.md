---
name: vectorcraft
description: Operate VectorCraft for small scoped edits, engine inspection, and explicitly requested regular VectorCraft work. Substantial new designs automatically use vectorcraft-studio's research, build and critique workflow.
---

# VectorCraft through chat

Deliver the requested artwork without requiring the user to learn VectorCraft. Use the configured companion MCP server; discover tools when they are not exposed. The launcher is `src/launch_mcp.py vectorcraft` in the installed checkout. Executable paths come from installation configuration; inspect connection status rather than assuming a drive location.

For substantial new designs use [VectorCraft Studio](../vectorcraft-studio/SKILL.md). For a simple edit or explicitly requested regular VectorCraft, call `workflow_start` with `mode: quick` and the concrete edit scope before authoring. Full mode authoring is gated by research/specification and planned batches; use `workflow_status` for schemas. Document setup/inspection is available without a run, and original artwork is preserved before replacement. Quick mode keeps ordinary save/export/preview operation lightweight.

The experimental `focused-execution-v1` profile is available only for explicitly selected full runs. Read Studio's [focused contract](../vectorcraft-studio/references/focused-execution-v1.md), then use `workflow_status {view:"working"}` for one task and current evidence. It preserves ordinary native operations, project roots and recovery. Scope guidance is not a per-object sandbox; inspect effects on neighbors and the whole artwork. Quick mode and the default full profile are unchanged.

## Create and revise

Opt-in `execution_profile:efficient-v1` supports full Focused build and Full process.
Read [Efficient execution](../vectorcraft-studio/references/efficient-v1.md).
Reuse current packets; retrieve omitted context explicitly. Discover commands with
`filter` and inspect IDs with bounded `document.node` summaries. On verified 0.12
use coherent drawing batches with explicit paint and returned-ID references, at
most 32 steps. A named atomic batch is an undo group, not rollback. Never replay
a partial/uncertain edit. On 0.11 choose supported individual drawing calls first.

The opt-in full profiles `layout-blockout-v1` and `designer-process-v1` add isolated native study contexts. Read [Studio process](../vectorcraft-studio/references/designer-process-v1.md). Study authoring uses a separate connection and an explicit transition into production.

Check the working packet's preview context/current flag before acting. Study packets expose their own goal and checks; the selected blockout is the initial production preview. Neither is an accepted production stage.

- Inspect the active document before editing. For a continuation, reopen the saved `.vectorcraft` original rather than reconstructing it from a flattened export. Preserve supplied originals and unrelated artwork.
- Use `command_list` / `list_commands` to discover current command IDs, parameters, and enabled state. Prefer engine commands for deterministic edits. Use convenience tools for paths, shapes, paint, text, transforms, graphs, and effects. Coordinates are points, y down; text x/y is the first baseline.
- Use object IDs from returned results and inspection, rather than guessing them. Rectangle and ellipse creation requires x, y, width, height. Discover effect IDs with `apply_effect` without an effect. For a fill gradient, explicitly pass `stroke: false` to `paint.editGradient`; an omitted flag can follow the active paint proxy instead.
- Choose appropriate dimensions, colors, typography, and geometry from the user's project context. State consequential assumptions briefly and continue. Ask only for information essential to the result.
- Save the editable original and the requested exports using explicit absolute project paths. Use this chat's output directory when supplied by its environment. Check reported import/export warnings and explain material losses or font substitutions.
- Inspect `render_preview` / `screenshot` images and iterate on the actual artwork. Confirm final files exist and reopen the native document to verify it remains editable. Return a preview and useful file links with a concise explanation of what was created.

## Desktop features

The gateway starts in background mode. UI inspection, window screenshots, text input, panels, and view/window commands automatically transfer the active artwork into a managed desktop window. For other interface-only actions or dialogs, call `enable_desktop` first, then rediscover commands and inspect the interface. The user has authorized this window to open automatically when needed; operate it through VectorCraft tools. No manual user operation is required.

Prefer structured commands when they achieve the requested result. For interactive work, use `select_tool`, `pointer_gesture`, `press_key`, `type_text`, `open_panel`, `invoke_menu`, and UI inspection/screenshot tools. Inspect state before sending focus-dependent text or keys. The transfer preserves artwork and selection but begins a new undo history. Save final files to explicit paths, since the desktop initially opens a recovery copy.

Each MCP session owns its own window and localhost port. Do not attach to, close, or change unrelated VectorCraft windows. Files are restricted to the current project root. When supplied inputs are elsewhere, copy them into the project when authorized by the task before opening them.

## Recovery and limits

`connection_status` reports the project root, mode, owned desktop, last error, and checkpoint path. The gateway keeps alternating native checkpoints under `work/vectorcraft/<session>/` after completed mutating tools; these are recovery files, not the final deliverables.

On timeout, partial batch failure, connection loss, or uncertain operation results, inspect the document and error before deciding what to do. Do not replay edits automatically. If the desktop died, start a fresh connection and reopen the reported recovery checkpoint. If a checkpoint cannot be saved, save the active document explicitly and report the problem; the gateway retains a running window when shutdown recovery fails.

Do not promise every app feature is flawless. Execute and verify the requested features. The supported host is local Codex on Windows; this does not install an integration into ordinary web ChatGPT.
