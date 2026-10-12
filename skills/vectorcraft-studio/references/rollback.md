# Roll back an installation

Use scripts/install.py from the maintained checkout, with Python 3.13. Do not manually replace the user's entire Codex configuration.

```powershell
py -3.13 scripts/install.py --rollback --snapshot SNAPSHOT_ID --dry-run
py -3.13 scripts/install.py --rollback --snapshot SNAPSHOT_ID
```

The private snapshot stores the prior VectorCraft MCP section and both owned skill directories. Rollback checks subsequently modified owned files/settings before writing and preserves unrelated current configuration. Omit --snapshot to select the latest installation made by this checkout. If a conflict is reported, preserve and resolve the changed owned content explicitly; there is no force overwrite. Historical imported backups and run records remain unchanged. Existing engine binaries and other Crafting Apps are not reinstalled or modified.

After rollback, reconnect the MCP or use a fresh Codex session. Existing loaded connections retain their catalog and startup environment. For installation/discovery flags see the project README.
