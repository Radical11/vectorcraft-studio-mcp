# Supported environment

Experimental release: 3.1.0-alpha.1. Supported initial scope: local Codex on Windows, Python 3.13, VectorCraft CLI plus desktop 0.9. The engine is installed separately; no executables are redistributed. Native document/resource/prompt/command passthrough is checked against the installed engine, not emulated by the companion.

Linux-hosted CI covers self-contained fixtures, portable installer transactions and release/site validation. Local Windows evidence separately covers stdio MCP, live rendering, native reopening, desktop ownership, recovery and fresh Codex routing. Neither constitutes support for Linux/macOS deployment or ordinary web ChatGPT.

Image generation and independent reviewer subagents are host capabilities. When unavailable, record the limitation instead of inventing visual evidence. No model is bundled or called through a separate API. Optional validation tools and Poppler are development-only; the gateway/installer use the standard library.

Point the installer to your actual paths. The knowledge vault is configurable; new Studio work uses workflow_status.knowledge_vault and brain31.py. Legacy v1/v2 helpers retain their original defaults/contracts, so pass --vault explicitly if invoking them directly.
