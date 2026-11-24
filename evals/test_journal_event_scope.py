"""Journal confirmation must belong to the operation actually read back."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from history_integrity import verify_journal, ensure_no_pending_overlap
from shared_state import StateError, Conflict
from public_journal_fixtures import fixture_pair


def saved(name):
    keys={'final-confirmed-state':'link-repair-plan','native-test-confirmed':'native-test-plan',
          'native-archive-confirmed':'native-archive-plan'}
    plan,state=fixture_pair(keys.get(name,name))
    return state if name in keys else plan


class NativeJournalScope(unittest.TestCase):
    def setUp(self):
        self.plan = saved('link-repair-plan')
        self.state = saved('final-confirmed-state')

    def own(self, kind):
        return next(r for r in self.state['tables']['Revision History'] if
                    r['op_id']==self.plan['op_id'] and r['event']==kind)

    def verify(self):
        verify_journal(self.plan,self.state,require_prepared=True,require_confirmed=True)

    def test_three_archived_native_journals_compatible(self):
        for plan,snapshot in [('native-test-plan','native-test-confirmed'),
                              ('native-archive-plan','native-archive-confirmed'),
                              ('link-repair-plan','final-confirmed-state')]:
            with self.subTest(plan=plan):
                verify_journal(saved(plan),saved(snapshot),require_prepared=True,require_confirmed=True)

    def test_different_project_or_test_scope_cannot_confirm(self):
        self.own('CONFIRMED').update(project_id='TEST-CPE31',episode_id='TEST-CPE31-EP1',is_test=True)
        with self.assertRaisesRegex(StateError,'Journal scope'):
            self.verify()

    def test_changed_operation_or_executor_cannot_confirm(self):
        row = self.own('CONFIRMED')
        original = copy.copy(row)
        for key in ['last_op_id','updated_by']:
            row[key] = 'unrelated'
            with self.subTest(key=key),self.assertRaisesRegex(StateError,'operation or executor'):
                self.verify()
            row.update(original)

    def test_confirmation_after_plan_but_before_preparation_must_fail(self):
        self.own('PREPARED')['updated_at'] = self.state['read_at']
        with self.assertRaisesRegex(StateError,'follow every preparation'):
            self.verify()

    def test_event_newer_than_the_readback_is_unverified(self):
        self.own('CONFIRMED')['updated_at'] = '2099-01-01T00:00:00+00:00'
        with self.assertRaisesRegex(StateError,'postdates its readback'):
            self.verify()

    def test_unrelated_confirmation_cannot_release_overlapping_work(self):
        other = {**self.plan,'op_id':'NEXT-OPERATION'}
        rows = [self.own('PREPARED'),self.own('CONFIRMED')]
        ensure_no_pending_overlap(other,rows,self.state['read_at'])
        self.own('CONFIRMED')['episode_id'] = 'OTHER-EPISODE'
        with self.assertRaisesRegex(Conflict,'Unresolved operation'):
            ensure_no_pending_overlap(other,rows,self.state['read_at'])
