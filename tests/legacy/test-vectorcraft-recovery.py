import concurrent.futures
import importlib.util
import json
from pathlib import Path
PROJECT=Path(__file__).resolve().parents[2]
import sys
import threading
import time

sys.path.insert(0, str(PROJECT / 'src'))
from vectorcraft_gateway import Gateway, INIT, NativeMcp, payload

WORK = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("test_gateway", WORK / "test-vectorcraft-gateway.py")
test = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test)
results = []


def simultaneous_sessions():
    barrier = threading.Barrier(2)
    roots = [Path(str(PROJECT / 'work/tests/vectorcraft-gateway-tests')) / "isolated-c", Path(str(PROJECT / 'work/tests/vectorcraft-gateway-tests/isolated-d'))]
    def session(index):
        c = test.client(roots[index])
        try:
            c.checked_call("draw_shape", {"shape": "rectangle", "x": 0, "y": 0, "width": 12 + index, "height": 20})
            c.checked_call("ui_inspect", {})
            status = payload(c.checked_call("connection_status", {}))
            inspect = payload(c.checked_call("doc_inspect", {}))
            assert inspect["objects"] == 2
            # Cross-project writes must be refused by both the desktop and gateway.
            refused = c.call("export", {"path": str(roots[1-index] / "must-not-exist.svg")})
            assert refused.get("isError") and "outside" in json.dumps(refused).lower()
            barrier.wait(timeout=30)
            return {"project_root": status["project_root"], "pid": status["desktop_pid"], "port": status["port"]}
        finally:
            c.process.stdin.close()
            c.process.wait(timeout=45)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        sessions = list(pool.map(session, [0, 1]))
    assert sessions[0]["pid"] != sessions[1]["pid"]
    assert sessions[0]["port"] != sessions[1]["port"]
    results.append({"test": "simultaneous isolated C/D project sessions", "passed": True, "sessions": sessions})


def failed_startup_retains_document():
    root = Path(str(PROJECT / 'work/tests/vectorcraft-gateway-tests')) / "startup-failure"
    root.mkdir(parents=True, exist_ok=True)
    g = Gateway(root)
    g.initialize(INIT)
    g.call("workflow_start", {"mode":"quick", "scope":"Recovery regression fixture"})
    g.tools()
    actual_exe = g.desktop_exe
    try:
        assert not g.call("draw_shape", {"shape": "star", "cx": 40, "cy": 40, "radius1": 30, "radius2": 12}).get("isError")
        before = payload(g.call("doc_inspect", {}))
        g.desktop_exe = root / "nonexistent-vectorcraft.exe"
        try:
            g.enable_desktop()
            raise AssertionError("Expected startup failure")
        except FileNotFoundError:
            pass
        after = payload(g.call("doc_inspect", {}))
        assert g.mode == "headless" and before["layers"] == after["layers"]
        g.desktop_exe = actual_exe
        g.enable_desktop()
        assert payload(g.call("doc_inspect", {}))["objects"] == before["objects"]
        results.append({"test": "failed desktop startup preserves background artwork and allows explicit retry", "passed": True})
    finally:
        g.shutdown()


def shutdown_failure_preserves_window():
    root = Path(str(PROJECT / 'work/tests/vectorcraft-gateway-tests')) / "shutdown-failure"
    root.mkdir(parents=True, exist_ok=True)
    g = Gateway(root)
    g.initialize(INIT)
    g.call("workflow_start", {"mode":"quick", "scope":"Recovery regression fixture"})
    g.tools()
    recovery_dir = g.recovery_dir
    try:
        g.call("draw_shape", {"shape": "ellipse", "x": 0, "y": 0, "width": 25, "height": 25})
        g.enable_desktop()
        g.recovery_dir = root.parent / "outside-project"
        g.shutdown()
        assert g.desktop.poll() is None, "Failed recovery must not close the window"
        g.recovery_dir = recovery_dir
        g.backend = NativeMcp([str(g.cli), "mcp", "--connect", f"127.0.0.1:{g.port}"], root)
        g.last_error = None
        results.append({"test": "failed shutdown save retains owned desktop instead of discarding artwork", "passed": True})
    finally:
        g.recovery_dir = recovery_dir
        g.shutdown()
        assert g.desktop.poll() is not None


def unexpected_desktop_exit():
    root = Path(str(PROJECT / 'work/tests/vectorcraft-gateway-tests')) / "desktop-exit"
    c = test.client(root)
    try:
        c.checked_call("draw_shape", {"shape": "rectangle", "x": 0, "y": 0, "width": 28, "height": 12})
        c.checked_call("enable_desktop", {})
        c.checked_call("add_text", {"text": "RECOVERY", "x": 30, "y": 50})
        status = payload(c.checked_call("connection_status", {}))
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.OpenProcess.restype = ctypes.c_void_p
        kernel32.OpenProcess.argtypes = [ctypes.c_uint, ctypes.c_bool, ctypes.c_uint]
        kernel32.TerminateProcess.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        handle = kernel32.OpenProcess(1, False, status["desktop_pid"])
        assert handle
        try:
            assert kernel32.TerminateProcess(handle, 1)
        finally:
            kernel32.CloseHandle(handle)
        time.sleep(0.3)
        rejected = c.call("draw_shape", {"shape": "ellipse", "x": 0, "y": 0, "width": 10, "height": 10})
        assert rejected.get("isError") and "not replayed" in json.dumps(rejected).lower()
        native = json.loads(Path(status["recovery_checkpoint"]).read_text())
        assert native["format"] == "vectorcraft"
        recovered = test.client(root)
        try:
            recovered.checked_call("open_file", {"path": status["recovery_checkpoint"]})
            document = payload(recovered.checked_call("doc_inspect", {}))
            assert document["objects"] == 3
        finally:
            recovered.process.stdin.close()
            recovered.process.wait(timeout=45)
        results.append({"test": "unexpected desktop exit does not replay edits and completed work reopens from recovery", "passed": True})
    finally:
        c.process.stdin.close()
        c.process.wait(timeout=45)


if __name__ == "__main__":
    simultaneous_sessions()
    failed_startup_retains_document()
    shutdown_failure_preserves_window()
    unexpected_desktop_exit()
    (WORK / "vectorcraft-recovery-test-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    for result in results:
        print(json.dumps(result), flush=True)
