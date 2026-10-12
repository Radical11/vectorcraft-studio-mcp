import base64
import concurrent.futures
import json
from pathlib import Path
PROJECT=Path(__file__).resolve().parents[2]
import sys
import time

sys.path.insert(0, str(PROJECT / 'src'))
from vectorcraft_gateway import NativeMcp, payload

WORK = Path(__file__).resolve().parent
ROOT = Path(str(PROJECT / 'work/tests/vectorcraft-gateway-tests/primary'))
ROOT.mkdir(parents=True, exist_ok=True)
GATEWAY = str(PROJECT / 'src/vectorcraft_gateway.py')


def client(root):
    root.mkdir(parents=True, exist_ok=True)
    result = NativeMcp([sys.executable, str(PROJECT / 'src/launch_mcp.py'), "vectorcraft"], root)
    try:
        tools = result.request("tools/list", {})["tools"]
        result.checked_call("workflow_start", {"mode":"quick", "scope":"Legacy engine regression fixture"})
        assert len(tools) >= 39
    except Exception:
        result.close()
        raise
    return result


def command(c, name, params=None):
    return payload(c.checked_call("command_run", {"id": name, "params": params or {}}))


def save_image(result, path):
    for block in result.get("content", []):
        if block.get("type") == "image":
            path.write_bytes(base64.b64decode(block["data"]))
            return
    raise AssertionError("Expected inline image content")


def primary():
    c = client(ROOT)
    try:
        assert payload(c.checked_call("connection_status", {}))["mode"] == "headless"
        command(c, "file.new", {"width": 640, "height": 360})
        command(c, "layer.new", {"name": "Brand artwork"})
        bg = payload(c.checked_call("draw_shape", {"shape": "rectangle", "x": 0, "y": 0, "width": 640, "height": 360, "fill": "#10263d", "stroke": "none"}))["id"]
        command(c, "paint.editGradient", {"ids": [bg], "stroke": False, "kind": "linear", "angle": 0, "stops": [{"offset": 0, "color": "#10263d"}, {"offset": 1, "color": "#24577f"}]})
        mark = payload(c.checked_call("draw_shape", {"shape": "ellipse", "x": 52, "y": 65, "width": 100, "height": 100, "fill": "#49d5ba", "stroke": "none"}))["id"]
        text = payload(c.checked_call("add_text", {"x": 52, "y": 228, "text": "MADE THROUGH CHAT", "font": "Arial", "size": 31, "color": "#ffffff"}))["id"]
        c.checked_call("add_text", {"x": 54, "y": 270, "text": "Editable vectors. No manual drawing.", "font": "Arial", "size": 17, "color": "#b7d6e8"})
        command(c, "select.set", {"ids": [mark]})
        c.checked_call("apply_effect", {"effect": "stylize.dropShadow", "ids": [mark]})
        before = payload(c.checked_call("doc_inspect", {}))
        save_image(c.checked_call("render_preview", {"max_side": 640}), ROOT / "before.png")
        native_path = ROOT / "chat-artwork.vectorcraft"
        c.checked_call("save_file", {"path": str(native_path)})
        # An interface-only tool must trigger lazy desktop startup.
        ui = c.checked_call("ui_inspect", {})
        status = payload(c.checked_call("connection_status", {}))
        assert status["mode"] == "desktop", status
        after = payload(c.checked_call("doc_inspect", {}))
        assert before["objects"] == after["objects"]
        assert before["artboards"] == after["artboards"]
        assert before["selection"] == after["selection"]
        (ROOT / "ui-inspect.json").write_text(json.dumps(payload(ui), indent=2), encoding="utf-8")
        c.checked_call("open_panel", {"panel": "Layers"})
        c.checked_call("open_panel", {"panel": "Gradient"})
        command(c, "view.fitArtboard", {})
        # Follow-up edit in desktop mode; save and export the updated document.
        command(c, "select.set", {"ids": [text]})
        command(c, "text.setText", {"ids": [text], "text": "MADE WITH VECTORCRAFT"})
        # The native Type tool receives actual interface text input.
        c.checked_call("select_tool", {"tool": "type"})
        c.checked_call("pointer_gesture", {"events": [{"kind": "down", "x": 70, "y": 220}, {"kind": "up", "x": 70, "y": 220}]})
        c.checked_call("press_key", {"key": "A", "mods": {"cmd": True}})
        c.checked_call("type_text", {"text": "MADE WITH VECTORCRAFT"})
        c.checked_call("press_key", {"key": "Escape"})
        c.checked_call("select_tool", {"tool": "selection"})
        c.checked_call("save_file", {"path": str(native_path)})
        for extension in ["svg", "pdf", "png"]:
            destination = ROOT / f"chat-artwork.{extension}"
            c.checked_call("export", {"path": str(destination)})
            assert destination.is_file() and destination.stat().st_size > 0
        c.checked_call("open_file", {"path": str(native_path)})
        reopened = payload(c.checked_call("doc_inspect", {}))
        assert reopened["objects"] == after["objects"]
        save_image(c.checked_call("render_preview", {"max_side": 640}), ROOT / "after.png")
        save_image(c.checked_call("ui_screenshot", {}), ROOT / "desktop.png")
        print(json.dumps({"primary": "passed", "status": status, "objects": reopened["objects"]}), flush=True)
        return status
    finally:
        # Allow recovery and graceful managed-window shutdown.
        c.process.stdin.close()
        c.process.wait(timeout=45)


if __name__ == "__main__":
    status = primary()
    (WORK / "vectorcraft-gateway-primary-result.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
