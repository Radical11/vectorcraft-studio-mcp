"""Launch a portable Crafting App MCP server in the current Codex project."""
import json
import os
from pathlib import Path
import subprocess
import sys


def command_for(app_name, workspace=None):
    manifest_path = Path(os.environ.get("CRAFTING_APPS_MANIFEST", r"D:\Crafting Apps\download-manifest.json"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    app = next((entry for entry in manifest if entry["App"].lower() == app_name), None)
    if app is None:
        raise ValueError(f"Unknown Crafting App: {app_name}")
    cli = Path(app["Executable"]).with_name(f"{app_name}-cli.exe")
    if not cli.is_file():
        raise FileNotFoundError(f"Missing portable CLI: {cli}")
    root = str(Path(workspace or os.getcwd()).resolve())
    args = [str(cli), "mcp"]
    if app_name in {"photocraft", "vectorcraft", "effectcraft"}:
        if app_name == "vectorcraft":
            args.append("--headless")
        args.extend(["--automation-read-root", root, "--automation-write-root", root])
    elif app_name == "pdfcraft":
        args.extend(["--root", root, "--compact"])
    elif app_name == "lightcraft":
        args.append("--compact")
    return args


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise ValueError("Usage: launch_mcp.py APP_NAME")
        app_name = sys.argv[1].lower()
        print(f"Crafting Apps: {app_name}, project folder {os.getcwd()}", file=sys.stderr)
        if app_name == "vectorcraft":
            from vectorcraft_gateway import main
            main()
            sys.exit(0)
        child = subprocess.Popen(command_for(app_name))
        try:
            sys.exit(child.wait())
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=5)
    except Exception as error:
        print(f"Crafting Apps launch failed: {error}", file=sys.stderr)
        sys.exit(1)
