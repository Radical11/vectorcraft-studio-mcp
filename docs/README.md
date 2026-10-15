# Repository map

Start with [how the process works](PROCESS.md), [current progress](research/PROGRESS.md), or [installation](INSTALLATION.md).

| Folder | Purpose | How to treat it |
| --- | --- | --- |
| `src/` | Maintained Python gateway and workflow policy | Frozen authoring files stay unchanged during the current study |
| `skills/` | Two deployable skills: VectorCraft and Studio | Installed through the installer; current study uses frozen versions |
| `tests/` | [Policy, legacy, installer, publication, and integration checks](../tests/README.md) | Fixtures are software checks, not real artwork evidence |
| `scripts/` | [Installation, verification, and publication tools](../scripts/README.md) | Explicit entry points; private staging scripts are superseded |
| `benchmarks/` | [Study preparation, isolated hosts, and reporting](../benchmarks/README.md) | Frozen study helpers and historical authoring utilities |
| `public-evidence/` | [Sanitized inspection packages](../public-evidence/README.md) | Keep dated snapshots intact; add supplements separately |
| `site/` | Static public showcase and stage explorer | Serves documentation and images; never edits artwork |
| `docs/research/` | Current method, progress, claims, and paper sources | Protocol and dated editions stay intact |
| `docs/peer-review/` | Original dated paper and its artifacts | Historical claims remain attached to their edition |
| `examples/` | Editable public examples | Distinct from current held-out study outcomes |
| `work/` | Local trial roots, private inputs, public staging checkout | Ignored; preserve evidence and recovery state |
| `outputs/` | Generated documents, test logs, local verification | Ignored; selected outputs are published only after review |
| `baseline/` | Historical imported local evidence | Immutable and ignored |
| `.local/` | Local helpers, snapshots, and private backups | Ignored; never publish configuration or raw context |

## Technical references

- [Focused task and acceptance contracts](FOCUSED-EXECUTION.md)
- [Native studies and relationship contracts](DESIGNER-PROCESS.md)
- [Deferred coarse-to-fine extensions](COARSE-TO-FINE-ROADMAP.md)
- [Supported environment](SUPPORTED.md) and [contribution rules](../CONTRIBUTING.md)
- [Research index](research/README.md), [claims](research/CLAIMS.md), and [original evaluation](EVALUATION.md)

The repository has two histories: a local authoring checkout with private evidence kept outside Git, and a sanitized public branch. Public uploads copy explicit inputs and record source/public hashes. They never push private local history.
