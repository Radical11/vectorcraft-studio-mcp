"""Synthetic stage/provenance safeguards, never actual artwork observations."""
from pathlib import Path
import copy
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_stage_evidence as stages
import stage_public as publication


class StagePublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.events = {'events': [
            {'event': 'begin', 'stage': 'imagery', 'at': '01'},
            {'event': 'focused_checkpoint', 'version': 'misleading-composition-name', 'at': '03', 'outcome': 'revise'}]}
        self.write('events.json', self.events)
        self.write('checkpoint.json', {'results': [
            {'id': 'a', 'brief': 'tyre', 'repeat': 1, 'condition': 'designer-v1', 'status': 'completed', 'retained_version': 'misleading-composition-name'},
            {'id': 'b', 'brief': 'tyre', 'repeat': 2, 'condition': 'designer-v1', 'status': 'pending', 'retained_version': None}]})
        (self.root / 'image.png').write_bytes(b'SYNTHETIC IMAGE BYTES')
        self.write('summary.json', {'best_version': 'misleading-composition-name', 'versions': {'misleading-composition-name': {'confirmed': True}}})
        capture = {'id': 'c', 'order': 1, 'version': 'misleading-composition-name', 'kind': 'production', 'stage': 'imagery',
                   'at': '02', 'confirmed': True, 'retained_best': True, 'selected_for_display': True,
                   'source_begin_event': 0, 'source_confirm_event': 1,
                   'images': {'full': {'path': 'image.png', 'sha256': stages.sha(self.root / 'image.png')}}}
        self.data = {'checkpoint': {'path': 'checkpoint.json', 'sha256': stages.sha(self.root / 'checkpoint.json')},
                     'trials': [dict(self.read('checkpoint.json')['results'][0], best_version='misleading-composition-name',
                                     source_summary={'path': 'summary.json', 'sha256': stages.sha(self.root / 'summary.json')},
                                     source_events={'path': 'events.json', 'sha256': stages.sha(self.root / 'events.json')}, captures=[capture]),
                                dict(self.read('checkpoint.json')['results'][1], captures=[])]}
        self.data['stages'] = {k: {'title': v[0], 'purpose': v[1]} for k, v in stages.STAGES.items()}
        for number, trial in enumerate(self.data['trials'], 1):
            trial['order'] = number
        self.guide = {'steps': [{'trial_id': 'a', 'capture_id': 'c',
                                 'full_sha256': stages.sha(self.root / 'image.png'),
                                 'title': 'Synthetic step', 'change': 'Synthetic change description.',
                                 'reading': 'Synthetic explanation; not an image observation.'}]}

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value), encoding='utf-8')

    def read(self, name):
        return stages.read(self.root / name)

    def test_event_not_filename_assigns_stage(self):
        self.assertEqual(stages.stage_binding(self.events, 'misleading-composition-name', {'at': '02'})[0], 'imagery')
        stages.validate(self.root, self.data)

    def test_reading_labels_preserve_source_ids_and_have_stable_steps(self):
        display = stages.presentation(self.data, self.guide)
        trial = display['trials'][0]
        self.assertEqual(trial['display_name'], 'Repair · Standard · Run 1')
        self.assertEqual(trial['short_id'], 'T01')
        self.assertEqual(trial['id'], 'a')
        self.assertEqual(trial['captures'][0]['version'], 'misleading-composition-name')
        self.assertEqual(trial['captures'][0]['step'], 'T01.01')
        self.assertNotIn('display_name', self.data['trials'][0])

    def test_every_step_description_is_required_exactly_once(self):
        for mode in ('missing', 'unknown', 'duplicate', 'empty'):
            guide = copy.deepcopy(self.guide)
            if mode == 'missing': guide['steps'] = []
            elif mode == 'unknown': guide['steps'][0]['capture_id'] = 'unknown'
            elif mode == 'duplicate': guide['steps'] *= 2
            else: guide['steps'][0]['change'] = ' '
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                stages.presentation(self.data, guide)

    def test_caption_image_binding_and_capture_order_cannot_drift(self):
        for mode in ('hash', 'order'):
            data = copy.deepcopy(self.data)
            capture = data['trials'][0]['captures'][0]
            if mode == 'hash': capture['images']['full']['sha256'] = 'changed'
            else: capture['order'] = 9
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                stages.presentation(data, self.guide)

    def test_progress_label_never_promotes_an_unconfirmed_or_failed_task(self):
        capture = self.data['trials'][0]['captures'][0]
        for confirmed, outcome, expected in ((False, 'pass', 'Not confirmed'),
                                              (True, 'revise', 'Needs correction'),
                                              (True, 'pass', 'Recorded step')):
            capture.update(confirmed=confirmed, task_outcome=outcome)
            result = stages.presentation(self.data, self.guide)
            self.assertEqual(result['trials'][0]['captures'][0]['progress_label'], expected)

    def test_comparison_accounting_includes_pending_and_partial_work(self):
        display = stages.presentation(self.data, self.guide)
        result = stages.comparison_story(display, {'cases': []})
        standard = result['accounting'][0]
        self.assertEqual(standard['total'], 2)
        self.assertEqual(standard['counts'], {'passed': 0, 'unresolved': 0, 'partial': 1, 'disrupted': 0, 'pending': 1})
        for status, run_status, expected in (('completed', 'review_passed', 'passed'),
                                              ('failed', 'active', 'unresolved')):
            display['trials'][0].update(status=status, run_status=run_status)
            self.assertEqual(stages.comparison_story(display, {'cases': []})['accounting'][0]['counts'][expected], 1)

    def comparison_fixture(self):
        display = stages.presentation(self.data, self.guide)
        first = display['trials'][0]['captures'][0]
        display['trials'][0]['captures'].append(dict(first, id='c2', version='second', order=2))
        config = {'cases': [{'id': 'synthetic', 'trial_id': 'a', 'steps': [
            {'version': first['version'], 'caption': 'Synthetic before'},
            {'version': 'second', 'caption': 'Synthetic after'}]}]}
        return display, config

    def test_comparisons_resolve_to_exact_capture_observations(self):
        display, config = self.comparison_fixture()
        result = stages.comparison_story(display, config)
        self.assertEqual(result['cases'][0]['captures'][1]['id'], 'c2')
        self.assertEqual(result['cases'][0]['captures'][1]['images'], display['trials'][0]['captures'][1]['images'])

    def test_comparisons_reject_unknown_unconfirmed_reversed_or_duplicate_steps(self):
        for mode in ('unknown', 'trial', 'unconfirmed', 'reverse', 'duplicate', 'duplicate-case'):
            display, config = self.comparison_fixture()
            case = config['cases'][0]
            if mode == 'unknown': case['steps'][1]['version'] = 'missing'
            elif mode == 'trial': case['trial_id'] = 'missing'
            elif mode == 'unconfirmed': display['trials'][0]['captures'][1]['confirmed'] = False
            elif mode == 'reverse': case['steps'].reverse()
            elif mode == 'duplicate': case['steps'] *= 2
            else: config['cases'] *= 2
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                stages.comparison_story(display, config)

    def test_unconfirmed_capture_binds_to_begin_timestamp(self):
        stage, begin, confirm, _ = stages.stage_binding(self.events, 'not-confirmed', {'at': '02'})
        self.assertEqual((stage, begin[0], confirm), ('imagery', 0, None))
        with self.assertRaises(ValueError):
            stages.stage_binding({'events': []}, 'unknown', {'at': '02'})

    def test_stage_mapping_cannot_disagree_with_source_events(self):
        self.data['trials'][0]['captures'][0]['stage'] = 'composition'
        with self.assertRaisesRegex(ValueError, 'Stage mapping'):
            stages.validate(self.root, self.data)

    def test_missing_duplicate_and_wrong_trial_mappings_rejected(self):
        for mode in ('missing', 'duplicate', 'wrong'):
            d = copy.deepcopy(self.data)
            if mode == 'missing': d['trials'].pop()
            elif mode == 'duplicate': d['trials'][1] = d['trials'][0]
            else: d['trials'][0]['repeat'] = 2
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                stages.validate(self.root, d)

    def test_changed_image_or_event_extract_rejected(self):
        for path in ('image.png', 'events.json'):
            old = (self.root / path).read_bytes()
            (self.root / path).write_bytes(b'changed')
            with self.subTest(path=path), self.assertRaises(ValueError):
                stages.validate(self.root, self.data)
            (self.root / path).write_bytes(old)

    def test_unconfirmed_or_wrong_version_cannot_be_retained_best(self):
        for key, value in (('confirmed', False), ('version', 'another-version')):
            d = copy.deepcopy(self.data)
            d['trials'][0]['captures'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                stages.validate(self.root, d)

    def test_pending_trial_cannot_gain_captures(self):
        self.data['trials'][1]['captures'] = [dict(self.data['trials'][0]['captures'][0], kind='study', retained_best=False)]
        with self.assertRaisesRegex(ValueError, 'Pending'):
            stages.validate(self.root, self.data)

    def test_missing_production_capture_cannot_silently_disappear(self):
        self.data['trials'][0]['captures'] = []
        with self.assertRaisesRegex(ValueError, 'Missing or duplicate production'):
            stages.validate(self.root, self.data)

    def test_missing_artifact_and_path_escape_fail(self):
        with self.assertRaises(ValueError):
            stages.safe_artifact(self.root, '../private')
        (self.root / 'image.png').unlink()
        with self.assertRaises(FileNotFoundError):
            stages.validate(self.root, self.data)

    def test_public_selection_excludes_private_and_old_authoring_helpers(self):
        for p in ('work/run.json', '.local/config.json', 'baseline/artwork.vectorcraft', 'outputs/results.json', 'benchmarks/repair_mapping31.py'):
            self.assertFalse(publication.selected(p), p)
        for p in ('docs/PROCESS.md', 'site/research.template.html', 'scripts/stage_public.py', 'benchmarks/README.md'):
            self.assertTrue(publication.selected(p), p)

    def test_json_redaction_does_not_rewrite_native_bytes(self):
        sample = ('C:' + '/Users/' + 'fixture-user/private\r\n').encode()
        self.assertNotIn(b'fixture-user', publication.public_bytes('docs/example.md', sample))
        self.assertEqual(publication.public_bytes('artwork.vectorcraft', sample), sample)

    def test_publication_audit_preserves_original_manifest(self):
        base = self.root / stages.CHECKPOINT
        base.mkdir(parents=True)
        content = b'{"synthetic":true}\r\n'
        (base / 'report.json').write_bytes(content)
        original = {'files': [{'path': 'report.json', 'public_sha256': stages.sha(base / 'report.json')}]}
        (base / 'artifact-manifest.json').write_text(json.dumps(original), encoding='utf-8')
        before = (base / 'artifact-manifest.json').read_bytes()
        audit = publication.snapshot_audit(self.root)
        self.assertEqual(len(audit['files']), 1)
        self.assertEqual((base / 'artifact-manifest.json').read_bytes(), before)

    def test_stale_generated_output_is_detected_without_overwrite(self):
        # Real presentation validation is exercised by --check in CI. Here prove
        # a missing marker aborts rather than replacing authored guide prose.
        supplement = self.root / stages.SUPPLEMENT
        supplement.mkdir(parents=True)
        d = copy.deepcopy(self.data)
        d.update(stages={k: {'title': v[0], 'purpose': v[1]} for k, v in stages.STAGES.items()})
        (supplement / 'index.json').write_text(json.dumps(d), encoding='utf-8')
        (self.root / 'site').mkdir()
        (self.root / 'site/research.template.html').write_text('<!-- STAGE_DATA -->', encoding='utf-8')
        (self.root / 'site/research.js').write_text('// synthetic', encoding='utf-8')
        (self.root / 'site/research.css').write_text('/* synthetic */', encoding='utf-8')
        guide = self.root / 'docs/research/PROGRESS.md'
        guide.parent.mkdir(parents=True)
        (self.root / stages.STEP_GUIDE).write_text(json.dumps(self.guide), encoding='utf-8')
        (self.root / stages.COMPARISONS).write_text(json.dumps({'cases': []}), encoding='utf-8')
        guide.write_text('Author-owned prose without generation markers.', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'markers'):
            stages.render(self.root, supplement, check=True)
        self.assertEqual(guide.read_text(encoding='utf-8'), 'Author-owned prose without generation markers.')

    def test_dirty_public_destination_cannot_be_overwritten(self):
        dest = self.root / 'work/public'
        (dest / '.git').mkdir(parents=True)
        def mock_git(root, *args):
            return ' M docs/PROCESS.md' if root == dest else ''
        with patch.object(publication, 'git', side_effect=mock_git), self.assertRaisesRegex(ValueError, 'Destination'):
            publication.stage(self.root, dest)

    def test_existing_dated_artifact_cannot_be_rewritten(self):
        dest = self.root / 'work/public'
        (dest / '.git').mkdir(parents=True)
        rel = 'docs/research/editions/old/paper.pdf'
        for base, content in ((self.root, b'new'), (dest, b'old')):
            p = base / rel
            p.parent.mkdir(parents=True)
            p.write_bytes(content)
        def mock_git(root, *args):
            return rel if args == ('ls-files',) else ''
        with patch.object(publication, 'git', side_effect=mock_git), self.assertRaisesRegex(ValueError, 'dated public snapshot'):
            publication.stage(self.root, dest)
        self.assertEqual((dest / rel).read_bytes(), b'old')


if __name__ == '__main__':
    unittest.main()
