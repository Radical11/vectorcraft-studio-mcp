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

The [research webpage](site/research.html) provides an interactive stage explorer when served from `site/`. The [public showcase](https://radical11.github.io/vectorcraft-studio-mcp/) reflects the deployed main branch; research-branch pages are available locally until separately deployed.

## How it works

Codex plans and inspects the images. The Python gateway keeps the workflow, revisions, task checks, and evidence in order. VectorCraft creates the native paths, live text, previews, and exports. Fresh reviewer contexts assess communication and craft using actual images.

Research → concepts → native roughs where enabled → selection → composition → typography → imagery → finishing → review and correction → verified delivery.

The gateway adds five workflow tools while preserving native MCP tools. It checks recorded state and file integrity; visual judgment still comes from the host and reviewers. Passing software tests does not establish design quality.

## Profiles

| Profile | What it adds |
| --- | --- |
| `designer-v1` | Default research, concept selection, four production stages, and independent final reviews |
| `focused-execution-v1` | One manageable construction task at a time, compact working packets, explicit task and stage acceptance |
| `layout-blockout-v1` | Three isolated native roughs before concept selection |
| `designer-process-v1` | Native roughs, focused execution, semantic entities, and relationship checks |

Experimental profiles are full-mode opt-ins. See the [process guide](docs/PROCESS.md#choosing-a-profile) for selection and the [technical contracts](docs/DESIGNER-PROCESS.md) for exact behavior.

## Development and evidence

Requires Windows, Python 3.13, local Codex, and separately installed VectorCraft CLI/desktop binaries. Self-contained checks run with `py -3.13 scripts/test_suite.py --unit-only`; native integration requires the compatible local engine. See [contributing](CONTRIBUTING.md) and the [test index](tests/README.md).

The existing release is [v3.1.0-alpha.1](https://github.com/Radical11/vectorcraft-studio-mcp/releases/tag/v3.1.0-alpha.1). Its [historical paper](docs/peer-review/README.md) is preserved separately from the [current interim study](docs/research/README.md). Neither the cleanup nor the interim upload promotes a new default or completes the pending study.

Owned contributions: **MIT OR Apache-2.0**. No engine binaries, font binaries, private configuration, or cached third-party reference images are distributed. See [asset provenance](ASSETS.md), [supported versions](docs/SUPPORTED.md), and [evidence limitations](docs/research/CLAIMS.md).
