# Installation and rollback


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

## Verification before installation

Run self-contained checks first. Full `scripts/test_suite.py` additionally exercises the installed Windows engine, native passthrough, desktop handoff, and isolated recovery. Hosted CI covers self-contained behavior, not actual image judgment or local engine integration.

Keep project access scoped to the current project. Copy authorized external inputs into that project rather than widening filesystem roots. Installation is separate from publishing research documentation.

[Process guide](PROCESS.md) · [Repository map](README.md)
