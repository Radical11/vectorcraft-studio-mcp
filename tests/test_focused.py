"""Synthetic policy checks. These fixtures are not image-tool or artwork evidence."""
import copy
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from workflow import Workflow, STAGES, read, atomic, tool_definitions
import focused
import test_designer as designer_tests


class FocusedTests(unittest.TestCase):
    def setUp(self):
        self.fixture = designer_tests.DesignerTests('test_missing_study')
        self.fixture.setUp()
        self.fixture.ready()
        self.fixture.study()
        self.w, self.root, self.backend = self.fixture.w, self.fixture.root, self.fixture.backend
        self.w.state['quality_profile'] = focused.PROFILE
        self.w.state['focused'] = {'contract': 1, 'tasks': {}, 'queue': [], 'mapping': {},
                                   'acceptances': {}, 'verified_revision': None}
        self.w.persist()

    def tearDown(self):
        self.fixture.tearDown()

    def plan(self, task='task', entities=None):
        return {'task_id': task, 'goal': 'Fixture: adjust one component',
                'entities': entities or ['title'], 'preserve': 'Fixture: preserve neighbors',
                'purpose': 'Fixture purpose', 'changes': 'Fixture changes',
                'expected_result': 'Fixture outcome',
                'checks': [{'id': 'recognition', 'description': 'Fixture visible recognition'},
                           {'id': 'spacing', 'description': 'Fixture visible spacing'}]}

    def begin(self, stage='composition', task='task', **changes):
        plan = self.plan(task)
        plan.update(changes)
        self.w.begin(stage, plan)

    def confirmation(self, complete=False, outcome='pass'):
        pending = self.w.state['pending']
        snap = self.w.state['versions'][pending['captured']]
        paths = [str(self.w.run / a['path']) for a in snap['images']]
        paths.append(str(self.w.run / self.w.latest('target')['attachments'][0]['path']))
        return {'phase': 'confirm', 'outcome': outcome, 'observations': 'Synthetic fixture only',
                'preservation_observation': 'Synthetic neighbor and whole-scene assertion only',
                'reason': 'Synthetic correction reason',
                'check_results': [{'id': c['id'], 'outcome': 'pass', 'observation': 'Fixture only'}
                                  for c in pending['plan']['checks']],
                'image_inspection': {'performed': True, 'paths': paths, 'observations': ['Fixture only']},
                'image_observation': self.fixture.obs, 'element_map': {'title': [4]},
                'stage_complete': complete,
                'stage_checks': {k: {'outcome': 'pass', 'observation': 'Fixture only'}
                                 for k in focused.STAGE_CHECKS[pending['stage']]}}

    def capture(self, name='capture'):
        self.w.checkpoint(self.backend, name, {'phase': 'capture'})

    def confirm(self, name='capture', complete=False, outcome='pass'):
        return self.w.checkpoint(self.backend, name, self.confirmation(complete, outcome))

    def complete(self):
        for stage in STAGES:
            self.begin(stage, task=stage)
            self.capture(stage)
            self.confirm(stage, complete=True)

    def test_opt_in_and_default_isolation(self):
        for profile in ('designer-v1', focused.PROFILE):
            w = Workflow(self.root)
            w.start(self.backend, brief_path=str(self.root / 'brief.md'), run_id=profile,
                    quality_profile=profile)
            self.assertEqual(w.state['quality_profile'], profile)
            self.assertEqual('focused' in w.state, profile == focused.PROFILE)
        defs = {t['name']: t for t in tool_definitions()}
        self.assertEqual(len(defs), 5)
        self.assertEqual(defs['workflow_start']['inputSchema']['properties']['quality_profile']['default'], 'designer-v1')

    def test_focused_quick_rejected(self):
        with self.assertRaisesRegex(ValueError, 'full mode'):
            Workflow(self.root).start(self.backend, mode='quick', scope='Fixture', quality_profile=focused.PROFILE)

    def test_missing_and_oversized_checks(self):
        for checks in (None, [], [{'id': str(i), 'description': 'Fixture'} for i in range(4)]):
            with self.assertRaisesRegex(ValueError, 'two or three'):
                self.begin(checks=checks)
        with self.assertRaisesRegex(ValueError, 'unique'):
            self.begin(checks=[{'id': 'same', 'description': 'Fixture'}] * 2)

    def test_unknown_and_oversized_scope(self):
        with self.assertRaisesRegex(ValueError, 'semantic entities'):
            self.begin(entities=['unknown'])
        with self.assertRaisesRegex(ValueError, 'semantic entities'):
            self.begin(entities=['title'] * 4)

    def test_intermediate_pass_does_not_complete_stage(self):
        self.begin(); self.capture(); self.confirm()
        self.assertTrue(self.w.state['versions']['capture']['confirmed'])
        self.assertEqual(self.w.state['completed_stages'], [])
        with self.assertRaisesRegex(ValueError, 'preceding'):
            self.begin('typography', 'next')
        self.begin(task='next-component')

    def test_explicit_stage_acceptance(self):
        self.begin(); self.capture(); self.confirm(complete=True)
        self.assertEqual(self.w.state['completed_stages'], ['composition'])
        self.begin('typography', 'type')

    def test_revise_records_then_correction_passes(self):
        self.begin(); self.capture(); self.confirm(outcome='revise')
        self.assertEqual(self.w.state['focused']['queue'][0]['id'], 'task-task')
        self.assertEqual(self.w.state['versions']['capture']['task_outcome'], 'revise')
        with self.assertRaises(ValueError):
            self.begin('typography', 'type')
        with self.assertRaisesRegex(ValueError, 'first correction'):
            self.begin()
        self.begin(finding_id='task-task'); self.capture('fixed'); self.confirm('fixed', complete=True)
        self.assertEqual(self.w.state['focused']['queue'], [])

    def test_blocked_is_not_a_terminal_run(self):
        self.begin(); self.capture(); self.confirm(outcome='blocked')
        self.assertEqual(self.w.state['status'], 'active')
        self.assertIn('correction', self.w.status(view='working')['next_action'])
        self.begin(finding_id='task-task')

    def test_failed_check_cannot_pass(self):
        self.begin(); self.capture(); data = self.confirmation(True)
        data['check_results'][0]['outcome'] = 'fail'
        with self.assertRaisesRegex(ValueError, 'failed check'):
            self.w.checkpoint(self.backend, 'capture', data)
        self.assertIsNotNone(self.w.state['pending'])

    def test_inapplicable_requires_reason(self):
        self.begin(); self.capture(); data = self.confirmation(True)
        data['stage_checks']['reading_order']['outcome'] = 'not_applicable'
        with self.assertRaisesRegex(ValueError, 'inapplicable reason'):
            self.w.checkpoint(self.backend, 'capture', data)
        data['stage_checks']['reading_order']['reason'] = 'Fixture wordless scene'
        self.w.checkpoint(self.backend, 'capture', data)

    def test_stage_check_failure_does_not_mutate(self):
        self.begin(); self.capture(); data = self.confirmation(True)
        data['stage_checks']['focal_separation']['outcome'] = 'fail'
        with self.assertRaisesRegex(ValueError, 'prevents completion'):
            self.w.checkpoint(self.backend, 'capture', data)
        self.assertEqual(self.w.state['focused']['tasks'], {})

    def test_images_and_mapping_required(self):
        self.begin(); self.capture(); data = self.confirmation()
        data['element_map']['title'] = [999999]
        with self.assertRaisesRegex(ValueError, 'actual document'):
            self.w.checkpoint(self.backend, 'capture', data)
        data = self.confirmation(); data['image_inspection']['performed'] = False
        with self.assertRaisesRegex(ValueError, 'inspection'):
            self.w.checkpoint(self.backend, 'capture', data)

    def test_stage_coverage_not_just_active_component(self):
        spec = copy.deepcopy(self.w.data('spec'))
        spec['elements'].append({'id': 'ground', 'kind': 'background', 'stage': 'composition', 'box': [0, 0, 900, 1200]})
        self.w.record(self.backend, 'spec', spec)
        self.begin(); self.capture()
        with self.assertRaisesRegex(ValueError, 'ground'):
            self.confirm(complete=True)
        self.confirm()

    def test_spec_amendment_invalidates_acceptance_and_packet(self):
        self.begin(); self.capture(); self.confirm(complete=True)
        self.w.record(self.backend, 'spec', self.w.data('spec'))
        self.assertEqual(self.w.state['completed_stages'], [])
        packet = self.w.status(view='working')
        self.assertFalse(packet['preview_current'])
        self.assertEqual(packet['references']['spec'], str(self.w.run / self.w.latest('spec')['artifact']['path']))

    def test_edit_invalidates_current_and_later_stages(self):
        self.complete()
        self.begin('imagery', 'repair')
        self.w.edited('draw_shape', {}, {'content': [], 'isError': False})
        self.assertEqual(self.w.state['completed_stages'], ['composition', 'typography'])
        self.assertFalse(self.w.status(view='working')['preview_current'])
        self.capture('repair')
        self.confirm('repair', complete=True)
        self.assertEqual(self.w.state['focused']['verified_revision'], self.w.state['revision'])

    def test_amended_spec_reconciles_removed_finding_entity(self):
        self.begin(); self.capture(); self.confirm(outcome='revise')
        spec = copy.deepcopy(self.w.data('spec'))
        spec['elements'][0]['id'] = 'new-title'
        spec['reading_sequence'] = ['new-title']
        self.w.record(self.backend, 'spec', spec)
        self.assertEqual(self.w.state['focused']['queue'][0]['entities'], [])
        self.begin(task='new-scope', entities=['new-title'], finding_id='task-task')

    def test_confirmation_invalidated_after_spec_change(self):
        self.begin(); self.capture()
        self.w.state['spec_revision'] += 1
        with self.assertRaisesRegex(ValueError, 'Stale'):
            self.confirm()

    def test_passed_task_cannot_be_reused(self):
        self.begin(); self.capture(); self.confirm()
        with self.assertRaisesRegex(ValueError, 'new task ID'):
            self.begin()

    def test_correction_cannot_change_unresolved_scope(self):
        spec = copy.deepcopy(self.w.data('spec'))
        spec['elements'].append({'id': 'ground', 'kind': 'background', 'stage': 'composition', 'box': [0, 0, 900, 1200]})
        self.w.record(self.backend, 'spec', spec)
        self.begin(); self.capture(); self.confirm(outcome='revise')
        with self.assertRaisesRegex(ValueError, 'stage and entities'):
            self.begin(entities=['ground'], finding_id='task-task')

    def test_preflight_blocks_unresolved_and_stale_acceptance(self):
        self.complete(); focused.preflight(self.w)
        self.w.state['focused']['queue'].append({'id': 'unresolved'})
        with self.assertRaisesRegex(ValueError, 'unresolved'):
            focused.preflight(self.w)
        self.w.state['focused']['queue'] = []
        self.w.state['focused']['verified_revision'] = None
        with self.assertRaises(ValueError): focused.preflight(self.w)

    def test_resume_preserves_profile_task_queue_and_pending(self):
        self.begin(); self.capture(); self.confirm(outcome='revise')
        w = Workflow(self.root)
        w.start(self.backend, resume=str(self.w.run))
        self.assertTrue(focused.enabled(w))
        self.assertEqual(w.state['focused']['queue'][0]['id'], 'task-task')
        w.begin('composition', {**self.plan(), 'finding_id': 'task-task'})
        restored = Workflow(self.root)
        restored.start(self.backend, resume=str(w.run))
        self.assertEqual(restored.state['pending']['plan']['task_id'], 'task')

    def test_compact_packet_does_not_expand_research(self):
        self.begin()
        packet = self.w.status(view='working')
        self.assertEqual(packet['active_task']['goal'], self.plan()['goal'])
        self.assertNotIn('schemas', packet)
        self.assertNotIn('synthesis', str(packet))
        self.assertEqual(packet['relevant_object_ids'], {'title': []})

    def test_uncertain_packet_does_not_offer_authoring(self):
        self.begin()
        self.w.edited('command_batch', {}, {'isError': True})
        self.assertIn('never replay', self.w.status(view='working')['next_action'])

    def test_review_findings_prioritized_without_creator_scores(self):
        data = {'reviews': [{'role': 'craft', 'review': {'findings': [
            {'severity': 'major', 'evidence': 'Fixture grip', 'fix': 'Fixture fix', 'location': 'Fixture hand'},
            {'severity': 'critical', 'evidence': 'Fixture omitted object', 'fix': 'Fixture restore', 'location': 'Fixture tool'},
            {'severity': 'minor', 'evidence': 'Fixture texture', 'fix': 'Fixture adjust', 'location': 'Fixture surface'}]}}]}
        focused.reviewed(self.w, data)
        self.assertEqual([q['severity'] for q in self.w.state['focused']['queue']], ['critical', 'major'])
        with self.assertRaisesRegex(ValueError, 'first correction'):
            self.begin()


    def test_reviewed_version_packet_does_not_offer_duplicate_review(self):
        self.complete()
        self.w.state['ready_versions'] = ['finishing']
        self.w.state['reviews'].append({'version': 'finishing', 'artifact': self.w.latest('research')['artifact']})
        self.w.state['reviews'].append({'version': 'original', 'artifact': self.w.latest('calibration')['artifact']})
        packet = self.w.status(view='working')
        self.assertIn('latest observed review', packet['next_action'])
        self.assertIn('latest_review', packet['references'])
        self.assertEqual(packet['references']['latest_review'], str(self.w.run / self.w.latest('research')['artifact']['path']))

    def test_mutation_response_is_compact_but_full_status_keeps_schemas(self):
        result = self.w.begin('composition', self.plan())
        self.assertNotIn('schemas', result)
        self.assertEqual(result['active_task']['task_id'], 'task')
        self.assertIn('schemas', self.w.status())
        self.w.state['quality_profile'] = 'designer-v1'
        self.assertIn('schemas', self.w.response())

if __name__ == '__main__':
    unittest.main()
