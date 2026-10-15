# Maintenance tools

Run Python tools with Python 3.13 from the repository root. Commands do not establish visual quality.

| Tool | Purpose |
| --- | --- |
| `install.py` | Scoped installation, dry run, snapshots, and rollback of the two owned skills and VectorCraft MCP section |
| `test_suite.py` | Self-contained suite; full mode adds local native/desktop/recovery checks |
| `verify_installation.py` | Inspect the installed configuration and owned files |
| `validate_skills.py` | Optional official skill validation |
| `check_public.py` | Validate public links, assets, privacy, and evidence presentation |
| `prepare_release.py --check` | Validate sanitized packaging without publishing a release |
| `export_interim_study.py` | Create a new explicit study checkpoint, preserving failures and pending rows |
| `build_stage_evidence.py` | Export a new additive stage supplement, or render/check its public explorer |
| `stage_public.py` | Stage committed public inputs into a clean public Git checkout; preserve dated artifacts and bind derivative hashes |
| `public_checkout31.py` | Historical initial public-checkout builder; keep its release context |

## Stage documentation and publication

```powershell
# Rebuild only the controlled generated region and stage explorer from public data.
py -3.13 scripts/build_stage_evidence.py render
py -3.13 scripts/build_stage_evidence.py render --check
# After committing intended changes, preview and stage into a clean public clone.
py -3.13 scripts/stage_public.py stage --destination work/public-interim-20261015 --dry-run
py -3.13 scripts/stage_public.py stage --destination work/public-interim-20261015
```

Exporting a new supplement requires the existing local trial roots, a new destination under `public-evidence/`, and a valid frozen ledger. It never starts a builder. `stage_public.py audit` creates the additive disclosure of initial inner-manifest/normalized-public-byte differences. Public packaging uses actual public hashes; original snapshots are not rewritten.

Public staging copies committed files only, refuses a dirty destination, and preserves the original paper and dated bundles. It uses the maintained HTML template and explicit generated Markdown markers rather than replacing authored explanations with a private script's old page. Installation, evidence export, public staging, and Git publishing remain separate operations.

Reading labels live in `build_stage_evidence.py`; individual short names and explanations live in [STEP-GUIDE.json](../docs/research/STEP-GUIDE.json). Rendering requires exactly one description per existing capture and checks its full-image hash. Edit these maintained descriptions and render again; do not rename source IDs, revise the dated supplement, or hand-edit the generated page. Attempt references follow frozen trial order and step references follow capture order. Descriptions summarize existing records; new observations require their own properly collected evidence.
