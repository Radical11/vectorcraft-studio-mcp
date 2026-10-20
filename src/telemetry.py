"""Connection-local cost receipts. No prompts, tool arguments or image pixels logged."""
import base64
import json
from pathlib import Path
import struct
import threading
import time


class Metrics:
    def __init__(self, root, session):
        self.root = Path(root).resolve()
        self.path = self.root / 'work/vectorcraft' / session / 'metrics.jsonl'
        self.lock = threading.Lock()
        self.error = None
        self.stream = None

    def record(self, layer, tool, args, result, started, error=None):
        try:
            images = [b for b in (result or {}).get('content', []) if b.get('type') == 'image'] if isinstance(result, dict) else []
            dimensions = []
            for image in images:
                head = base64.b64decode(image.get('data', '')[:44])
                if head.startswith(b'\x89PNG') and len(head) >= 24:
                    dimensions.append(list(struct.unpack('>II', head[16:24])))
            row = {'at': time.time(), 'layer': layer, 'tool': tool, 'duration_ms': (time.perf_counter()-started)*1000,
                   'request_json_bytes': len(json.dumps(args, ensure_ascii=False).encode()),
                   'response_text_bytes': sum(len(b.get('text', '').encode()) for b in (result or {}).get('content', []) if b.get('type') == 'text') if isinstance(result, dict) else 0,
                   'image_encoded_bytes': sum(len(b.get('data', '')) for b in images), 'image_dimensions': dimensions,
                   'failed': bool(error or isinstance(result, dict) and result.get('isError')),
                   'actual_model_tokens': None, 'token_source': 'unavailable; requires run-scoped host receipt'}
            arguments=(args or {}).get('arguments',{}) if layer=='native' else args or {}
            if tool=='export':
                row['export_format']=arguments.get('format')
                path=arguments.get('path')
                row['recovery_export']=bool(path and Path(path).resolve().parent==self.path.parent.resolve())
            if tool=='render_preview':row['requested_max_side']=arguments.get('max_side')
            if tool=='command_batch' and isinstance(result,dict):
                for block in result.get('content',[]):
                    if block.get('type')!='text':continue
                    try:batch=json.loads(block.get('text',''))
                    except (ValueError,TypeError):continue
                    if not isinstance(batch,dict):continue
                    row['completed_steps']=batch.get('completed')
                    row['failed_steps']=batch.get('failed')
                    row['failed']=row['failed'] or bool(batch.get('failed'))
                    break
            with self.lock:
                if not self.path.resolve().is_relative_to(self.root):
                    raise ValueError('Metrics escaped project root')
                self.path.parent.mkdir(parents=True, exist_ok=True)
                if self.stream is None:self.stream=self.path.open('a',encoding='utf-8',buffering=1)
                self.stream.write(json.dumps(row)+'\n')
        except Exception as exc:
            self.error = type(exc).__name__  # Diagnostics must never replay or fail a successful operation.

    def close(self):
        with self.lock:
            if self.stream is not None:
                try:self.stream.close()
                except OSError as exc:self.error=type(exc).__name__
                self.stream=None
