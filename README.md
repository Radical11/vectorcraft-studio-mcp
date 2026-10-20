# VectorCraft Studio

An experimental, unofficial design companion for Codex and local VectorCraft on Windows. It helps an AI designer research an idea, build editable vectors in small steps, inspect the result, and correct visible problems.

**Current progress:** 10 of 18 study attempts accounted for; 8 deferred. Four passed final construction review, one delivered artwork with unresolved acceptance, one retained partial artwork, and four were disrupted without final artwork. Comparative improvement is still unestablished. The default remains `designer-v1`.

## Start here

| Question | Read |
| --- | --- |
| How does the design process work? | [Plain-language process guide](docs/PROCESS.md) |
| What have we built and learned? | [Progress and stage comparisons](docs/research/PROGRESS.md) |
| Where is the paper and evidence? | [Interim publication](docs/research/INTERIM-PUBLICATION.md) |
| How do I run it? | [Installation and rollback](docs/INSTALLATION.md) |
| Where does everything belong? | [Repository map](docs/README.md) |

The [public research explorer](https://radical11.github.io/vectorcraft-studio-mcp/research.html) shows the recorded stages and corrections. Its [source page](site/research.html) also works locally. The [public showcase](https://radical11.github.io/vectorcraft-studio-mcp/) serves the documentation from main.

Start with the [observed before/after fixes](https://radical11.github.io/vectorcraft-studio-mcp/research.html#observed-fixes), [process diagram](https://radical11.github.io/vectorcraft-studio-mcp/research.html#process-changes), or [complete study status chart](https://radical11.github.io/vectorcraft-studio-mcp/research.html#study-accounting). These show local progress and remaining gaps; the project changes the workflow around an existing model and does not train new model weights.

## How it works

Codex plans and inspects the images. The Python gateway keeps the workflow, revisions, task checks, and evidence in order. VectorCraft creates the native paths, live text, previews, and exports. Fresh reviewer contexts assess communication and craft using actual images.

Research → concepts → native roughs where enabled → selection → composition → typography → imagery → finishing → review and correction → verified delivery.

The gateway adds five workflow tools while preserving native MCP tools. It checks recorded state and file integrity; visual judgment still comes from the host and reviewers. Passing software tests does not establish design quality.

## Profiles

| Profile | What it adds |
| --- | --- |
| **Standard** — `designer-v1` | Default research, concept selection, four production stages, and independent final reviews |
| **Focused build** — `focused-execution-v1` | One manageable construction task at a time, compact working packets, explicit task and stage acceptance |
| **Layout first** — `layout-blockout-v1` | Three isolated native roughs before concept selection |
| **Full process** — `designer-process-v1` | Native roughs, focused execution, semantic entities, and relationship checks |

Experimental profiles are full-mode opt-ins. See the [process guide](docs/PROCESS.md#choosing-a-profile) for selection and the [technical contracts](docs/DESIGNER-PROCESS.md) for exact behavior.

For opt-in **Efficient execution**, add `execution_profile:"efficient-v1"` to a full Focused build or Full process start. It uses smaller working packets and verified 0.12 drawing batches, while retaining image inspection, stage acceptance and recovery. See the [operating guidance](skills/vectorcraft-studio/references/efficient-v1.md). `standard` remains the default; 0.11 keeps its supported individual-drawing path.

Progress uses names such as **Repair · Full process · Run 1**, with numbered steps such as **T07.10 — Open the tyre edge**. Each step explains the change, recorded result, and remaining issue. [See how to read progress](docs/research/PROGRESS.md#simple-names-and-step-numbers). Original technical IDs stay available in the evidence.

## Development and evidence

Requires Windows, Python 3.13, local Codex, and separately installed VectorCraft CLI/desktop binaries. Self-contained checks run with `py -3.13 scripts/test_suite.py --unit-only`; native integration requires the compatible local engine. See [contributing](CONTRIBUTING.md) and the [test index](tests/README.md).

The existing release is [v3.1.0-alpha.1](https://github.com/Radical11/vectorcraft-studio-mcp/releases/tag/v3.1.0-alpha.1). Its [historical paper](docs/peer-review/README.md) is preserved separately from the [current interim study](docs/research/README.md). Neither the cleanup nor the interim upload promotes a new default or completes the pending study.

Owned contributions: **MIT OR Apache-2.0**. No engine binaries, font binaries, private configuration, or cached third-party reference images are distributed. See [asset provenance](ASSETS.md), [supported versions](docs/SUPPORTED.md), and [evidence limitations](docs/research/CLAIMS.md).
