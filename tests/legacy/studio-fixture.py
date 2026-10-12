import base64
import json
from pathlib import Path
PROJECT=Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(PROJECT / 'src'))
from vectorcraft_gateway import NativeMcp, payload

ROOT = PROJECT / 'work/tests/studio-fixture'
ROOT.mkdir(parents=True, exist_ok=True)
c = NativeMcp([sys.executable, str(PROJECT / 'src/launch_mcp.py'), 'vectorcraft'], ROOT)
ids = {}
try:
    tools = c.request('tools/list', {})
    def cmd(name, params=None):
        return payload(c.checked_call('command_run', {'id':name, 'params':params or {}}))
    cmd('file.new', {'width':900, 'height':1200})
    cmd('layer.new', {'name':'Night of Ideas poster'})
    def shape(key, args):
        ids[key] = payload(c.checked_call('draw_shape', args))['id']
    def text(key, x, y, content, size, color, font='Arial'):
        ids[key] = payload(c.checked_call('add_text', {'x':x,'y':y,'text':content,'size':size,'color':color,'font':font}))['id']
    shape('background', {'shape':'rectangle','x':0,'y':0,'width':900,'height':1200,'fill':'#f4f0e8','stroke':'none'})
    text('label', 76, 100, 'CAMPUS / AFTER HOURS', 19, '#193747')
    text('title1', 72, 245, 'NIGHT', 100, '#193747')
    text('title2', 110, 330, 'OF IDEAS', 76, '#193747')
    text('subtitle', 86, 378, 'Student talks. Fresh perspectives.', 17, '#aaa697')
    shape('orb', {'shape':'ellipse','x':582,'y':155,'width':235,'height':235,'fill':'#eeb12c','stroke':'#193747','strokeWidth':9})
    c.checked_call('apply_effect', {'effect':'stylize.dropShadow','ids':[ids['orb']]})
    shape('triangle', {'shape':'polygon','cx':284,'cy':560,'radius':125,'sides':3,'fill':'#219e9b','stroke':'none'})
    shape('square', {'shape':'rectangle','x':640,'y':535,'width':110,'height':110,'fill':'#e04491','stroke':'none','radius':20})
    text('date', 105, 765, '18 OCT 2026 / 6 PM', 24, '#193747')
    text('place', 63, 819, 'STUDIO HALL', 22, '#193747')
    shape('ticket', {'shape':'rectangle','x':200,'y':940,'width':500,'height':80,'fill':'#e04491','stroke':'none','radius':24})
    text('cta', 300, 992, 'FREE ENTRY', 26, '#193747')
    text('footer', 96, 1112, 'An evening of creativity, conversation, and possibility.', 16, '#aaa697')
    native = ROOT / 'original.vectorcraft'
    c.checked_call('save_file', {'path':str(native)})
    for name, side in [('original-full.png',1200),('original-use.png',600)]:
        image = c.checked_call('render_preview', {'max_side':side})
        block = next(x for x in image['content'] if x['type']=='image')
        (ROOT / name).write_bytes(base64.b64decode(block['data']))
    inspect = payload(c.checked_call('inspect_document', {}))
    (ROOT / 'original-inspection.json').write_text(json.dumps(inspect,indent=2),encoding='utf-8')
    (ROOT / 'ids.json').write_text(json.dumps(ids,indent=2),encoding='utf-8')
    (ROOT / 'commands.json').write_text(json.dumps(payload(c.checked_call('command_list', {})),indent=2),encoding='utf-8')
    (ROOT / 'brief.md').write_text('Create an editorial campus poster for NIGHT OF IDEAS, an evening of student talks and fresh perspectives. Required content: CAMPUS / AFTER HOURS; NIGHT OF IDEAS; Student talks. Fresh perspectives.; 18 OCT 2026 / 6 PM; STUDIO HALL; FREE ENTRY; An evening of creativity, conversation, and possibility. Audience: college students. Size: 900x1200, primarily shared at 450x600 on phones. Desired direction: confident, playful editorial geometry with purposeful typography. Preserve all content, no new facts. Supplied artwork is the starting point; improve communication and craft while preserving its recognizable identity. Deliver editable original, SVG and PNG.',encoding='utf-8')
    print(json.dumps({'native':str(native),'objects':inspect.get('objects')}))
finally:
    c.process.stdin.close()
    c.process.wait(timeout=45)
