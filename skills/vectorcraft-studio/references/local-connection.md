# Installed local connection fallback

Prefer the exposed `vectorcraft` MCP tools. If this environment does not expose them, the same configured gateway can be driven from a single Python process. This is not a replacement rendering engine.

```python
import sys
from pathlib import Path
import os, tomllib
home = Path(os.environ.get('CODEX_HOME', Path.home()/'.codex'))
section = tomllib.loads((home/'config.toml').read_text(encoding='utf-8-sig'))['mcp_servers']['vectorcraft']
launcher = Path(section['args'][0])
sys.path.insert(0, str(launcher.parent))
from vectorcraft_gateway import NativeMcp, payload

root = Path('ABSOLUTE_CURRENT_PROJECT_ROOT')
os.environ.update(section.get('env', {}))
c = NativeMcp([section['command'], *section['args']], root)
try:
    tools = c.request('tools/list', {})['tools']
    commands = payload(c.checked_call('command_list', {}))
    # Full designs: workflow_start full + v3 records before editing.
    # Scoped small edits: workflow_start quick with a concrete scope.
    # Use checked_call(tool_name, arguments). Inspect schemas and command results.
    # Save the native file and requested exports before ending this process.
finally:
    c.process.stdin.close()
    c.process.wait(timeout=45)
```

`NativeMcp` performs initialization and supports JSON-RPC requests. `payload` parses a JSON text block in a tool result. Image content is base64 PNG; write it to a project file and actually inspect it with `view_image`. Paths are rooted at this process's current project, including the gateway's desktop mode. Do not recreate this client for each unsaved edit: a new process starts an empty editing session. Reopen a saved native original when beginning another process.

Command discovery avoids guessing engine parameters. The native schema of `draw_shape` requires x/y/width/height for rectangles and ellipses. The stable skill documents other tested tool semantics. Use the same production executable and gateway; do not edit either to run the experiment.
