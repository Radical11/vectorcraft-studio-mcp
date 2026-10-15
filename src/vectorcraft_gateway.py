"""Project-scoped MCP gateway: headless editing with lazy desktop handoff."""
from __future__ import annotations

import copy
import ctypes
import json
import os
from pathlib import Path
import queue
import socket
import subprocess
import sys
import threading
import time
import uuid
from workflow import Workflow, INSTRUCTIONS, tool_definitions
from discovery import executables

VERSION = "3.2.0-alpha.1"
UI_TOOLS = {"ui_inspect", "ui_screenshot", "inspect_ui", "type_text", "open_panel"}
INIT = {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "vectorcraft-codex-gateway", "version": VERSION}}


def text_result(value, error=False):
    return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False)}], "isError": error}


def payload(result):
    for block in result.get("content", []):
        if block.get("type") == "text":
            try:
                return json.loads(block["text"])
            except ValueError:
                pass
    return None


class NativeMcp:
    def __init__(self, command, root, notify=None, init=None):
        self.notify = notify or (lambda message: None)
        self.process = subprocess.Popen(command, cwd=root, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", bufsize=1, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self.pending = {}
        self.lock = threading.Lock()
        self.write_lock = threading.Lock()
        self.next_id = 0
        self.active_id = None
        self.errors = []
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.error_reader = threading.Thread(target=self._stderr, daemon=True)
        self.reader.start(); self.error_reader.start()
        try:
            self.initialize_result = self.request("initialize", init or INIT, timeout=15)
            self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        except Exception:
            self.close()
            raise

    def _stderr(self):
        for line in self.process.stderr:
            self.errors.append(line.rstrip())
            self.errors = self.errors[-20:]
            print("VectorCraft: " + line.rstrip(), file=sys.stderr, flush=True)

    def _read(self):
        try:
            for line in self.process.stdout:
                try:
                    response = json.loads(line)
                except ValueError:
                    continue
                response_id = response.get("id")
                with self.lock:
                    receiver = self.pending.get(response_id)
                if receiver:
                    receiver.put(response)
                elif "method" in response and "id" not in response:
                    self.notify(response)
        finally:
            with self.lock:
                receivers = list(self.pending.values())
            for receiver in receivers:
                receiver.put({"error": {"code": -32000, "message": "Native VectorCraft MCP connection closed; operation outcome may be uncertain."}})

    def send(self, message):
        with self.write_lock:
            self.process.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
            self.process.stdin.flush()

    def request(self, method, params=None, timeout=290):
        with self.lock:
            self.next_id += 1
            request_id = self.next_id
            receiver = queue.Queue()
            self.pending[request_id] = receiver
        self.active_id = request_id
        try:
            message = {"jsonrpc": "2.0", "id": request_id, "method": method}
            if params is not None:
                message["params"] = params
            self.send(message)
            response = receiver.get(timeout=timeout)
            if "error" in response:
                raise RuntimeError(json.dumps(response["error"]))
            return response["result"]
        except queue.Empty:
            raise TimeoutError("VectorCraft did not respond. The operation may have completed; inspect its state before retrying.")
        finally:
            with self.lock:
                self.pending.pop(request_id, None)
            self.active_id = None

    def call(self, tool, args, timeout=290):
        return self.request("tools/call", {"name": tool, "arguments": args}, timeout=timeout)

    def checked_call(self, tool, args, timeout=290):
        result = self.call(tool, args, timeout)
        if result.get("isError"):
            raise RuntimeError(json.dumps(payload(result) or result))
        return result

    def close(self):
        try:
            self.process.stdin.close()
            self.process.wait(timeout=3)
        except Exception:
            self.process.kill()
            self.process.wait(timeout=3)
        finally:
            for reader in (self.reader,self.error_reader):reader.join(timeout=1)
            for stream in (self.process.stdout,self.process.stderr):
                if stream and not stream.closed:stream.close()


class Gateway:
    def __init__(self, root=None, notify=None):
        self.root = Path(root or os.getcwd()).resolve()
        self.notify = notify or (lambda message: None)
        self.cli,self.desktop_exe = executables()
        self.backend = None
        self.mode = "headless"
        self.desktop = None
        self.port = None
        self.init_params = INIT
        self.session = uuid.uuid4().hex
        self.recovery_dir = self.root / "work" / "vectorcraft" / self.session
        self.last_checkpoint = None
        self.checkpoint_number = 0
        self.last_error = None
        self.transfer_notes = []
        self.tool_catalog = None
        self.changed = False
        self.current_client_id = None
        self.workflow = Workflow(self.root)
        self.preserved_documents = []
        from study_session import Studies
        self.studies=Studies(self)

    def start_headless(self):
        self.backend = NativeMcp([str(self.cli), "mcp", "--headless", "--automation-read-root", str(self.root), "--automation-write-root", str(self.root)], self.root, self.notify, self.init_params)
        self.mode = "headless"

    def initialize(self, params):
        self.init_params = params
        self.start_headless()
        result = copy.deepcopy(self.backend.initialize_result)
        result["serverInfo"].update(name="vectorcraft-studio",title="VectorCraft Studio — unofficial companion",version=VERSION)
        result["instructions"] = INSTRUCTIONS + '\nNative VectorCraft guidance:\n' + result.get('instructions','')
        return result

    def status(self):
        return {"mode": self.mode, "project_root": str(self.root), "desktop_pid": self.desktop.pid if self.desktop and self.desktop.poll() is None else None, "port": self.port, "recovery_checkpoint": str(self.last_checkpoint) if self.last_checkpoint else None, "last_error": self.last_error, "transfer_notes": self.transfer_notes, "workflow_run": str(self.workflow.run) if self.workflow.run else None, "gateway_version": VERSION, "preserved_documents": self.preserved_documents}

    def tools(self):
        result = self.backend.request("tools/list", {})
        result = copy.deepcopy(result)
        for tool in result["tools"]:
            if tool["name"] in UI_TOOLS:
                tool["description"] += " The Codex gateway opens the managed desktop automatically when this tool is used."
        result["tools"].extend([
            {"name": "enable_desktop", "title": "Enable VectorCraft desktop tools", "description": "Open a managed VectorCraft window for this project and transfer the active artwork. Use for dialogs, panels, and interface-only commands. Artwork is preserved; undo history starts anew. No manual operation is required.", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}, "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}},
            {"name": "connection_status", "title": "VectorCraft connection status", "description": "Report background/desktop mode, project folder, owned window, recovery checkpoint and errors without changing artwork.", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}, "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False}}
        ])
        result["tools"].extend(tool_definitions())
        self.tool_catalog = {tool["name"]: tool for tool in result["tools"]}
        return result

    def checkpoint(self, backend=None):
        backend = backend or self.backend
        self._check_recovery_location()
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
        candidate = self.recovery_dir / f"checkpoint-{self.checkpoint_number % 2}.vectorcraft"
        backend.checked_call("export", {"format": "vectorcraft", "path": str(candidate)}, timeout=30)
        if not candidate.is_file() or candidate.stat().st_size == 0:
            raise RuntimeError("Recovery export returned without a nonempty native document")
        native = json.loads(candidate.read_text(encoding="utf-8"))
        if native.get("format") != "vectorcraft":
            raise RuntimeError("Recovery export is not a valid native VectorCraft document")
        self.last_checkpoint = candidate
        self.checkpoint_number += 1
        self._write_status()
        return candidate

    def _write_status(self):
        self._check_recovery_location()
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
        path = self.recovery_dir / "session.json"
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.status(), indent=2), encoding="utf-8")
        os.replace(temporary, path)

    def _check_recovery_location(self):
        if not self.recovery_dir.resolve().is_relative_to(self.root):
            raise RuntimeError("Recovery folder resolves outside the current project")

    @staticmethod
    def _free_port():
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            return listener.getsockname()[1]

    def enable_desktop(self):
        if self.mode == "desktop" and self.desktop and self.desktop.poll() is None:
            return self.status()
        if self.mode == "desktop":
            raise RuntimeError("The managed desktop stopped. Start a new session and open the recovery checkpoint; no edit was replayed.")
        before = payload(self.backend.checked_call("doc_inspect", {}))
        snapshot = self.checkpoint()
        bridge = None
        owned = None
        try:
            for attempt in range(3):
                port = self._free_port()
                log = open(self.recovery_dir / f"desktop-{attempt}.log", "ab")
                try:
                    owned = subprocess.Popen([str(self.desktop_exe), "--control", str(port), "--automation-read-root", str(self.root), "--automation-write-root", str(self.root), str(snapshot)], cwd=self.root, stdout=log, stderr=log)
                finally:
                    log.close()
                deadline = time.monotonic() + 18
                ready = False
                while time.monotonic() < deadline and owned.poll() is None:
                    try:
                        with socket.create_connection(("127.0.0.1", port), timeout=0.3) as connection:
                            connection.settimeout(2)
                            connection.sendall(b'{"id":1,"method":"document.inspect","params":{}}\n')
                            response = json.loads(connection.makefile("r", encoding="utf-8").readline())
                            if response.get("ok"):
                                ready = True
                                break
                    except (OSError, ValueError):
                        time.sleep(0.1)
                if ready:
                    break
                if owned.poll() is None:
                    owned.terminate()
                    owned.wait(timeout=5)
                owned = None
            if not ready:
                raise RuntimeError("VectorCraft desktop did not start its control channel. The background document is still available.")
            bridge = NativeMcp([str(self.cli), "mcp", "--connect", f"127.0.0.1:{port}"], self.root, self.notify, self.init_params)
            after = payload(bridge.checked_call("doc_inspect", {}))
            if before.get("objects") != after.get("objects") or before.get("artboards") != after.get("artboards"):
                raise RuntimeError("Desktop handoff verification failed; the background document was retained")
            selection = before.get("selection", [])
            if selection:
                bridge.checked_call("command_run", {"id": "select.set", "params": {"ids": selection}})
            old_backend = self.backend
            self.backend = bridge
            self.desktop = owned
            self.port = port
            self.mode = "desktop"
            self.transfer_notes = ["Artwork transferred to the managed desktop. Undo history starts at the handoff checkpoint."]
            self.last_error = None
            # Once committed, metadata/old-child cleanup cannot roll back a live handoff.
            try:
                self._write_status()
            except Exception as error:
                self.last_error = "Desktop connected, but recovery metadata update failed: " + str(error)
            try:
                old_backend.close()
            except Exception as error:
                print("Unable to close previous background connection: " + str(error), file=sys.stderr, flush=True)
            return self.status()
        except Exception as error:
            if bridge:
                bridge.close()
            if owned and owned.poll() is None:
                # Only the newly loaded checkpoint is in this failed, unexposed window.
                owned.terminate()
                owned.wait(timeout=5)
            self.last_error = str(error)
            self._write_status()
            raise

    @staticmethod
    def requires_ui(name, args):
        if name in UI_TOOLS or (name == "screenshot" and args.get("window")):
            return True
        if name in {"command_run", "run_command", "invoke_menu"}:
            command = args.get("id", args.get("command", ""))
            return command.startswith(("view.", "window.", "ui.", "app."))
        if name == "command_batch":
            return any(Gateway.requires_ui("command_run", step) for step in args.get("steps", []) if isinstance(step, dict))
        return False

    def call(self, name, args):
        if self.studies.active() and name not in ('workflow_status',):
            return self.studies.route(name,args)
        if name == 'workflow_begin' and args.get('plan',{}).get('context')=='study':
            return text_result(self.studies.begin(**args))
        if name == "workflow_status":
            if self.studies.child:self.studies.child.workflow.verify()
            return text_result(self.workflow.status(**args))
        if name == "workflow_start":
            result=self.workflow.start(self.backend, **args)
            import design_process
            if design_process.enabled(self.workflow):self.studies.restore()
            return text_result(result)
        if name == "workflow_record":
            return text_result(self.workflow.record(self.backend, **args))
        if name == "workflow_begin":
            return text_result(self.workflow.begin(**args))
        if name == "workflow_checkpoint":
            return text_result(self.workflow.checkpoint(self.backend, **args))
        if name in {"enable_desktop", "connection_status"}:
            if args:
                return text_result({"error": "This tool takes no arguments"}, True)
            return text_result(self.enable_desktop() if name == "enable_desktop" else self.status())
        # Classify the real command, including every batch member, before any side effect.
        operation = self.operation(name, args)
        if operation == "setup":
            self.workflow.setup_allowed()
            inspection = payload(self.backend.checked_call("doc_inspect", {}))
            if inspection and inspection.get("objects", 0) > 1:
                self.checkpoint()  # Preserve existing artwork before document replacement.
                import shutil
                original = self.recovery_dir / ("original-" + uuid.uuid4().hex + ".vectorcraft")
                shutil.copy2(self.last_checkpoint, original)
                self.preserved_documents.append(str(original))
        elif operation == "edit":
            self.workflow.guard_edit()
        switched = False
        if self.requires_ui(name, args) and self.mode == "headless":
            self.enable_desktop()
            switched = True
        if self.mode == "desktop" and self.desktop.poll() is not None:
            return text_result({"error": "Managed VectorCraft window has closed. Editing was not replayed. Start a new connection and reopen the checkpoint.", **self.status()}, True)
        if operation in {"edit", "setup"}:
            self.changed = True
        try:
            result = self.backend.call(name, args)
        except Exception as error:
            if operation == "edit":
                self.workflow.edited(name, args, {}, error=str(error))
            raise
        if operation in {"edit", "setup"}:
            try:
                self.checkpoint()
            except Exception as error:
                self.last_error = "Recovery checkpoint failed: " + str(error)
                result.setdefault("content", []).append({"type": "text", "text": "The tool operation was not replayed. " + self.last_error + ". Save the current artwork explicitly."})
            if operation == "edit" or (operation == "setup" and self.workflow.state and self.workflow.state['mode'] == 'quick'):
                self.workflow.edited(name, args, result, self.last_checkpoint)
            elif operation == "setup" and self.workflow.state and self.last_checkpoint:
                self.workflow.state['recovery'] = self.workflow.artifact(self.last_checkpoint, 'recovery')
                self.workflow.state['events'].append({'event': 'document_setup', 'tool': name})
                self.workflow.persist()
        if switched:
            result.setdefault("content", []).append({"type": "text", "text": self.transfer_notes[0]})
        if not result.get('isError') and self.workflow.state:
            if name in {'render_preview','screenshot','ui_screenshot'}:self.workflow.note_render(name,result,args.get('path'))
            if name == 'export':self.workflow.note_export(args.get('path'))
            elif name in {'command_run','run_command'} and args.get('id',args.get('command')) in {'file.export','document.export'}:
                self.workflow.note_export(args.get('params',{}).get('path'))
            elif name == 'command_batch':
                for step in args.get('steps',[]):
                    if step.get('id') in {'file.export','document.export'}:self.workflow.note_export(step.get('params',{}).get('path'))
        return result

    @staticmethod
    def operation(name, args):
        """Conservative authoring classification; no blanket read-only trust for command tools."""
        read_tools = {"command_list", "list_commands", "doc_inspect", "inspect_document", "render_preview", "screenshot", "ui_inspect", "inspect_ui", "ui_screenshot", "export", "save_file"}
        if name in read_tools:
            return "read"
        if name in {"open_file", "new_document"}:
            return "setup"
        if name in {"command_run", "run_command", "invoke_menu"}:
            command = args.get("id", args.get("command", ""))
            params = args.get("params", {})
            if command in {"file.new", "file.open", "document.open"}:
                return "setup"
            reads = {"document.inspect", "document.node", "document.find", "document.formats", "text.fonts", "text.fontList", "text.getRange", "imageTrace.presets", "effect.list", "swatch.library.list", "clipboard.exportSvg", "clipboard.exportText", "document.export", "document.save", "file.save", "file.export"}
            if command in reads or command.startswith(("select.", "view.")):
                return "read"
            if command == "text.areaOptions" and not (set(params) - {"ids"}):
                return "read"
            return "edit"
        if name == "command_batch":
            operations = [Gateway.operation("command_run", step) for step in args.get("steps", [])]
            if "setup" in operations and "edit" in operations:
                raise ValueError("Do not mix document setup with artwork edits in one batch")
            return "edit" if "edit" in operations else "setup" if "setup" in operations else "read"
        # Every convenience edit and focus-dependent UI input is gated, including unknown tools.
        return "edit"

    def shutdown(self):
        self.studies.shutdown()
        if not self.backend:
            return
        saved = False
        try:
            if self.changed or self.mode == "desktop":
                checkpoint = self.checkpoint()
                if self.mode == "desktop" and self.desktop.poll() is None:
                    self.backend.checked_call("save_file", {"path": str(checkpoint)}, timeout=15)
                saved = True
        except Exception as error:
            self.last_error = "Shutdown recovery failed; desktop retained if still running: " + str(error)
            print(self.last_error, file=sys.stderr, flush=True)
        finally:
            self.backend.close()
        if self.desktop and self.desktop.poll() is None and saved:
            self._close_owned_window()
        if self.last_checkpoint:
            try:
                self._write_status()
            except Exception as error:
                print("Unable to update recovery metadata: " + str(error), file=sys.stderr, flush=True)

    def _close_owned_window(self):
        if os.name != "nt":
            return
        user32 = ctypes.windll.user32
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
        user32.IsWindowVisible.argtypes = [ctypes.c_void_p]
        user32.PostMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
        user32.EnumWindows.argtypes = [callback_type, ctypes.c_void_p]
        pid = self.desktop.pid
        def visit(window, unused):
            owner = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(window, ctypes.byref(owner))
            if owner.value == pid and user32.IsWindowVisible(window):
                user32.PostMessageW(window, 0x0010, 0, 0)
            return True
        user32.EnumWindows(callback_type(visit), 0)
        try:
            self.desktop.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("VectorCraft window retained because its normal close did not complete; recovery checkpoint is saved.", file=sys.stderr, flush=True)


def main():
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    output_lock = threading.Lock()
    def emit(message):
        with output_lock:
            sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    gateway = Gateway(notify=emit)
    inbox = queue.Queue()
    def read_requests():
        for line in sys.stdin:
            try:
                message = json.loads(line)
            except ValueError:
                emit({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Invalid JSON"}})
                continue
            if not isinstance(message, dict):
                emit({"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Request must be an object"}})
                continue
            if message.get("method") == "ping":
                emit({"jsonrpc": "2.0", "id": message.get("id"), "result": {}})
            elif message.get("method") == "notifications/cancelled":
                current=gateway.studies.child.backend if gateway.studies.child else gateway.backend
                if message.get("params", {}).get("requestId") == gateway.current_client_id and current and current.active_id is not None:
                    current.send({"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": current.active_id, "reason": message.get("params", {}).get("reason", "Cancelled by client")}})
            else:
                inbox.put(message)
        inbox.put(None)
    threading.Thread(target=read_requests, daemon=True).start()
    try:
        while True:
            message = inbox.get()
            if message is None:
                break
            method = message.get("method")
            if "id" not in message:
                continue
            gateway.current_client_id = message["id"]
            try:
                if method == "initialize":
                    if gateway.backend:
                        raise RuntimeError("Connection is already initialized")
                    result = gateway.initialize(message.get("params", {}))
                elif not gateway.backend:
                    raise RuntimeError("Initialize the connection first")
                elif method == "tools/list":
                    result = gateway.tools()
                elif method == "tools/call":
                    params = message.get("params", {})
                    try:
                        result = gateway.call(params["name"], params.get("arguments", {}))
                    except Exception as error:
                        gateway.last_error = str(error)
                        result = text_result({"error": str(error), "operation_replayed": False, **gateway.status()}, True)
                else:
                    current=gateway.studies.child.backend if gateway.studies.child else gateway.backend
                    result = current.request(method, message.get("params"))
                emit({"jsonrpc": "2.0", "id": message["id"], "result": result})
            except Exception as error:
                emit({"jsonrpc": "2.0", "id": message["id"], "error": {"code": -32000, "message": str(error)}})
            finally:
                gateway.current_client_id = None
    finally:
        gateway.shutdown()


if __name__ == "__main__":
    main()
