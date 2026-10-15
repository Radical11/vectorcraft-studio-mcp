# Verification map

Use Python 3.13. The standard self-contained entry point is:

```powershell
py -3.13 scripts/test_suite.py --unit-only
```

| Checks | What they establish |
| --- | --- |
| Workflow/designer/focused/process fixtures | Policy ordering, revision binding, acceptance, correction, and profile isolation |
| Experiment/edit/reporting fixtures | Budgets and accounting behavior, including incomplete evidence |
| Installer and legacy fixtures | Scoped installation/rollback and historical contracts |
| Process-analysis and interim-export tests | Reporting safeguards and sanitized export behavior; run explicitly in CI |
| Native/live tests | Local engine, gateway passthrough, desktop ownership, and isolated recovery; require Windows binaries |
| Publication/presentation checks | Links, hashes, stage mappings, snapshot preservation, and missingness labels |

Synthetic fixtures never count as actual image-tool observations, human responses, or aesthetic evidence. A documentation-only change requires relevant publication checks; native integration is rerun when engine behavior, recovery, or ownership changes.
