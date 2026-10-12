# VectorCraft Studio 3.1

An **unofficial community companion** for Codex on Windows and the local VectorCraft MCP. It connects research, concept selection, native vector construction and independent critique through revision-bound evidence. It is experimental software, not an endorsed integration or a guarantee of professional design quality.

Codex supplies research, built-in image generation and visual judgment. VectorCraft supplies editable paths, live typography, rendering and exports. This Python gateway preserves native MCP instructions, commands, resources and prompts while adding five workflow tools. No paid service or separate model API is required.

## Install locally

Requirements: Windows, Python **3.13**, local Codex with MCP/skills support, and compatible VectorCraft **CLI and desktop executables** installed separately. The locally verified engine is VectorCraft 0.9. Other versions and operating systems are unverified. Ordinary web ChatGPT is not a supported installation host.

Clone or extract this project into a permanent folder, then use PowerShell from that folder:

```powershell
py -3.13 scripts/test_suite.py --unit-only
py -3.13 scripts/install.py --cli 'C:\Apps\VectorCraft\vectorcraft-cli.exe' --desktop 'C:\Apps\VectorCraft\vectorcraft.exe' --vault 'C:\Design Brain' --dry-run
py -3.13 scripts/install.py --cli 'C:\Apps\VectorCraft\vectorcraft-cli.exe' --desktop 'C:\Apps\VectorCraft\vectorcraft.exe' --vault 'C:\Design Brain'
```

Use your actual executable/vault paths. `--codex-home` overrides `CODEX_HOME`, then the current user's `.codex` folder. Executables resolve from arguments, `VECTORCRAFT_CLI`/`VECTORCRAFT_DESKTOP`, a configured `CRAFTING_APPS_MANIFEST`, adjacent executable discovery, PATH or the supported Program Files location. Discovery does not scan drives. Existing Crafting Apps manifests remain supported; portable applications stay installed where they are. The gateway itself uses only Python's standard library.

Installation snapshots the owned configuration and both owned skill directories under ignored `.local/install-snapshots/`. It changes only the VectorCraft MCP table and managed skill files, preserving other MCP servers and unrelated settings. Existing extra files inside owned skills are preserved and snapshotted. Restart the MCP connection or begin a new Codex chat after installation; an already loaded connection retains its prior tool catalog. Keep the checkout in place because configuration points to its launcher.

```powershell
py -3.13 scripts/install.py --rollback --snapshot SNAPSHOT_ID --dry-run
py -3.13 scripts/install.py --rollback --snapshot SNAPSHOT_ID
```

Omitting `--snapshot` selects the latest installation in this checkout. Rollback detects subsequent owned-file/configuration changes and aborts before writing. It restores the snapshot while retaining unrelated later settings. Resolve a conflict explicitly after preserving your edits; there is no force-overwrite flag.

## Design workflow

Substantial requests activate Studio implicitly. Small scoped edits and an explicit regular-VectorCraft request use quick mode with a recorded scope. The tools are `workflow_start`, `workflow_record`, `workflow_begin`, `workflow_checkpoint` and `workflow_status`; status exposes authoritative schemas.

New full runs default to `designer-v1`:

1. Establish purpose, audience, medium, viewing size and exact required copy. Research actual references, then calibrate against three to five inspected works. Choose the expressive-poster, editorial-illustration or information-graphic profile appropriate to the brief. Profiles describe priorities and common weaknesses, not a universal visual style.
2. Develop three alternatives with actual copy and different ideas/reading experiences. A fresh concept reviewer compares them before autonomous selection. If all are weak, allow one further exploration pass and disclose remaining weaknesses. Evaluate editable copy for specificity, clarity, tone, image relationship and subject substitution.
3. Establish a visual target and concrete specification. Generate illustration separately from typography when useful. Confirm a representative native construction or trace-rebuild pilot; textured imagery calls for meaningful shape reconstruction rather than automatic whole-image tracing.
4. Build composition, fit typography, construct imagery and finish. Each planned batch maps important elements to native objects, then requires actual full/use-size inspection against the target. Check silhouette/spacing/proportions/gesture early, contours/type/detail later. Record deliberate departures and repair accidental losses.
5. Two fresh specialists independently assess communication/art direction and drawing/production craft. Neutral packets include candidate, retained best and untouched original when different. Common-brief suitability is separate from target fidelity; the original can win. Revise consequential findings, allow three rounds and stop after two non-improving rounds. Deliver the strongest reviewed version with limitations disclosed.

The gateway checks ordering, document revisions, actual fonts/copy, overflow, mappings, raster content and current export provenance. It cannot prove that an agent looked at an image or that artwork is good. Fixture assertions, object counts and scores are not aesthetic evidence. Research shortfalls, unavailable sources and visual losses remain explicit.

Project roots stay scoped to the current working directory. Copy authorized external inputs into the project instead of widening filesystem access. Sessions own separate desktop windows/recovery files. Interrupted or uncertain edits are inspected and resumed without replay. Historical v1/v2 helpers and v3 runs without the new profile retain their contracts; they are not rewritten.

## Verification and release status

`py -3.13 scripts/test_suite.py --unit-only` runs self-contained policy, installer and legacy-helper checks. Full `scripts/test_suite.py` additionally requires installed Windows binaries and exercises native passthrough, live gateway, desktop handoff and isolated recovery. Hosted CI does not claim to reproduce those local integration results. Optional official skill validation uses `scripts/validate_skills.py --validator PATH` and requires PyYAML.

The experimental release is [`v3.1.0-alpha.1`](https://github.com/Radical11/vectorcraft-studio-mcp/releases/tag/v3.1.0-alpha.1). The Windows suite passed 124 checks; the sanitized checkout passed 113 self-contained checks plus native fresh installation and rollback. Two fresh blind reviewers agreed on clear common-brief improvements in all three locked briefs without consequential regression. The owner also selected the retained Studio version in all three anonymous pairs. These case studies do not prove general professional superiority; repair target fidelity and anatomical detail remain limited. Public evidence is a sanitized derivative with relative paths; private baselines, raw vault contents, configuration and run histories are excluded.

See [supported versions](docs/SUPPORTED.md), [evaluation protocol](docs/EVALUATION.md), [contribution instructions](CONTRIBUTING.md), [asset provenance](ASSETS.md) and [the unsent maintainer proposal](docs/MAINTAINER-PROPOSAL.md). The [public repository](https://github.com/Radical11/vectorcraft-studio-mcp) contains maintained source, tests and editable examples. The [GitHub Pages showcase](https://radical11.github.io/vectorcraft-studio-mcp/) hosts documentation and comparisons only. MCP and VectorCraft run locally.

Owned contributions are licensed **MIT OR Apache-2.0**. VectorCraft and its branding are separate upstream works; no upstream branding assets or font binaries are distributed. [Upstream asset/contribution guidance](https://github.com/storytold/vectorcraft/blob/main/AGENTS.md). The inspection loop draws on [Figma Console MCP](https://github.com/southleft/figma-console-mcp); no additional server was installed. [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) serves the static showcase.
