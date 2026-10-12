import copy
import importlib.util
import json
from pathlib import Path
PROJECT=Path(__file__).resolve().parents[2]
import tempfile
import unittest
import subprocess
import sys

SPEC = importlib.util.spec_from_file_location('studio', str(PROJECT / 'skills/vectorcraft-studio/scripts/studio_run.py'))
studio = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(studio)
ROOT = Path(str(PROJECT / 'work/tests/studio-ledger-tests'))
ROOT.mkdir(parents=True, exist_ok=True)
FIXTURE = Path(str(PROJECT / 'tests/fixtures/studio-existing'))


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.root = Path(self.temp.name)
        (self.root / 'brief.md').write_text('An editorial student event poster', encoding='utf-8')
        for a, b in [('original.vectorcraft','artwork.vectorcraft'), ('original-full.png','full.png'), ('original-use.png','use.png'), ('original-inspection.json','inspect.json')]:
            (self.root / b).write_bytes((FIXTURE / a).read_bytes())
        self.run, _ = studio.init(self.root, 'test', self.root / 'brief.md')

    def tearDown(self):
        self.temp.cleanup()

    def snap(self, version):
        return studio.snapshot(self.run, version, self.root/'artwork.vectorcraft', [self.root/'full.png',self.root/'use.png'], self.root/'inspect.json')

    def review(self, version, score=3, winner='no_baseline', findings=None):
        _, state = studio.load(self.run)
        versions = [version] + ([state['best_version']] if state['best_version'] else [])
        images = [str((self.run / a['path']).resolve()) for v in versions for a in state['versions'][v]['artifacts'] if a['role']=='image']
        return {'image_inspection':{'performed':True,'paths':images,'observations':['A large heading sits above event details']},
                'scores':{k:{'score':score,'reason':'Evidence-based fixture judgment'} for k in studio.CRITERIA},
                'findings':findings or [], 'comparison':{'winner':winner,'reason':'Independent fixture comparison'},'summary':'Fixture review'}

    def initial(self):
        self.snap('original')
        return studio.record_review(self.run,'original',self.review('original'),'initial',True)

    def test_polished_stops_without_revision(self):
        self.snap('original')
        s=studio.record_review(self.run,'original',self.review('original',4),'initial',True)
        self.assertEqual((s['status'],s['revision_rounds']),('review_passed',0))

    def test_clear_improvement_replaces_best(self):
        self.initial(); self.snap('r1')
        s=studio.record_review(self.run,'r1',self.review('r1',4,'candidate'),'revision',True)
        self.assertEqual((s['status'],s['best_version']),('review_passed','r1'))

    def test_two_ties_stop_and_preserve_best(self):
        self.initial()
        for v in ['r1','r2']:
            self.snap(v); s=studio.record_review(self.run,v,self.review(v,3,'equal'),'revision',True)
        self.assertEqual((s['status'],s['best_version']),('stalled','original'))

    def test_three_improving_rounds_exhaust_budget(self):
        self.initial()
        for v in ['r1','r2','r3']:
            self.snap(v); s=studio.record_review(self.run,v,self.review(v,3,'candidate'),'revision',True)
        self.assertEqual((s['status'],s['revision_rounds'],s['best_version']),('budget_exhausted',3,'r3'))
        self.snap('r4')
        with self.assertRaises(ValueError):
            studio.record_review(self.run,'r4',self.review('r4',4,'candidate'),'revision',True)

    def test_regression_does_not_replace_best(self):
        self.initial(); self.snap('r1')
        s=studio.record_review(self.run,'r1',self.review('r1',2,'incumbent'),'revision',True)
        self.assertEqual(s['best_version'],'original')

    def test_major_issue_prevents_pass_and_promotion(self):
        self.initial(); self.snap('r1')
        f={'criterion':'craft','severity':'major','location':'Title','evidence':'Clipped letters','impact':'Message becomes unreadable','fix':'Move within artboard'}
        s=studio.record_review(self.run,'r1',self.review('r1',4,'candidate',[f]),'revision',True)
        self.assertEqual(s['best_version'],'original'); self.assertEqual(s['status'],'active')

    def test_resume_checks_native_integrity(self):
        self.initial()
        resumed=studio.load(self.run)[1]
        self.assertEqual(resumed['best_version'],'original')
        path=self.run/'versions'/'original'/'artwork.vectorcraft'
        path.write_text('broken',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'integrity'):
            studio.load(self.run)

    def test_existing_snapshot_cannot_be_replaced(self):
        self.snap('original')
        before=studio.digest(self.run/'versions'/'original'/'artwork.vectorcraft')
        with self.assertRaises(ValueError): self.snap('original')
        self.assertEqual(before,studio.digest(self.run/'versions'/'original'/'artwork.vectorcraft'))

    def test_unviewed_images_do_not_pass(self):
        self.snap('original'); r=self.review('original',4)
        r['image_inspection']['performed']=False
        with self.assertRaises(ValueError): studio.record_review(self.run,'original',r,'initial',True)
        with self.assertRaises(ValueError): studio.record_review(self.run,'original',self.review('original',4),'initial',False)

    def test_missing_compared_image_does_not_pass(self):
        self.initial(); self.snap('r1'); r=self.review('r1',4,'candidate')
        r['image_inspection']['paths']=r['image_inspection']['paths'][:2]
        with self.assertRaises(ValueError): studio.record_review(self.run,'r1',r,'revision',True)

    def test_na_criterion_allowed_but_all_na_rejected(self):
        self.snap('original'); r=self.review('original',4)
        r['scores']['typography']={'score':None,'reason':'Symbol has no text'}
        self.assertTrue(studio.validate_review(r,r['image_inspection']['paths']))
        for score in r['scores'].values(): score['score']=None
        with self.assertRaises(ValueError): studio.validate_review(r,r['image_inspection']['paths'])

    def test_review_cannot_hide_a_missing_criterion(self):
        self.snap('original'); r=self.review('original',4)
        del r['scores']['craft']
        with self.assertRaises(ValueError): studio.record_review(self.run,'original',r,'initial',True)

    def test_unavailable_stops_honestly_and_retains_candidate(self):
        self.snap('original')
        result=subprocess.run([sys.executable,'-X','utf8',str(SPEC.origin),'unavailable','--run',str(self.run),'--reason','Reviewer cannot inspect images'],capture_output=True,text=True,encoding='utf-8',check=True)
        state=json.loads(result.stdout)
        self.assertEqual(state['status'],'review_unavailable')
        self.assertIsNone(state['best_version'])
        self.assertTrue((self.run/'versions'/'original'/'artwork.vectorcraft').exists())
        with self.assertRaises(ValueError):studio.record_review(self.run,'original',self.review('original',4),'initial',True)

    def test_neutral_packet_works_and_modified_copy_rejected(self):
        self.initial(); self.snap('r1')
        packet=studio.review_packet(self.run,'r1')
        self.assertEqual(set(packet['evidence']),{'A','B'})
        for files in packet['evidence'].values():
            inspection=json.loads(Path(next(p for p in files if p.endswith('.json'))).read_text())
            self.assertNotIn('path',inspection); self.assertNotIn('history',inspection)
        self.assertTrue(all('original' not in p and 'r1' not in p for files in packet['evidence'].values() for p in files))
        r=self.review('r1',4,'candidate')
        r['image_inspection']['paths']=[p for files in packet['evidence'].values() for p in files if p.endswith('.png')]
        self.assertTrue(studio.validate_review(r,self.review('r1')['image_inspection']['paths']))
        changed=Path(r['image_inspection']['paths'][0]); changed.write_bytes(b'not the artwork')
        with self.assertRaises(ValueError):studio.validate_review(r,self.review('r1')['image_inspection']['paths'])

    def test_explicit_extension_resumes_without_discarding_best(self):
        self.initial()
        for v in ['r1','r2']:
            self.snap(v);studio.record_review(self.run,v,self.review(v,3,'equal'),'revision',True)
        result=subprocess.run([sys.executable,'-X','utf8',str(SPEC.origin),'extend','--run',str(self.run),'--rounds','2'],capture_output=True,text=True,encoding='utf-8',check=True)
        state=json.loads(result.stdout)
        self.assertEqual((state['status'],state['best_version'],state['max_rounds']),('active','original',4))
        self.assertEqual(len(state['reviews']),3)


if __name__=='__main__':
    unittest.main(verbosity=2)
