"""Regression cases reproduced by the 1.1 review, including historical 1.1 receipts."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
import test_harness_review as fixture
from shared_state import Conflict, StateError, prepare, check_guards, verify_readback, fingerprint
from journal import journal_rows
from journal_codec import CELL_BUDGET, cell_units


class CoreCorrections(unittest.TestCase):
    def setUp(self):
        h = fixture.IndependentHarnessReview()
        h.setUp()
        self.h, self.s = h, h.s

    def other_script(self):
        r = copy.deepcopy(self.h.asset)
        r.update(id="SECOND-SCREENPLAY", text_or_ref="Synthetic alternate version, a different ending.")
        self.s["tables"]["Screenplays"].append(r)
        return r

    def edit(self, *, text="new screenplay", op=None, table=None, key=None):
        row = self.h.asset
        c = {"table":table or "Screenplays","id":key or row["id"],"expected_revision":1,
             "values":{"text_or_ref":text} if not table else {"choice":text}}
        i = self.h.intent([c])
        if op:
            i["op_id"] = op
        return prepare(self.s, i)

    def event(self, plan, kind):
        return journal_rows(plan,kind,"TEST-CPE31","TEST-CPE31-EP1",True,"2026-11-24T10:02:00Z","test-only")

    def fresh(self, s):
        s = copy.deepcopy(s)
        s["read_at"] = "2026-11-24T10:03:00Z"
        return s

    def test_other_script_fails_for_same_gate_and_episode(self):
        self.h.asset = self.other_script()
        with self.assertRaisesRegex(StateError, "another delivery"):
            prepare(self.s,self.h.intent(self.h.gate_changes()),self.h.review())

    def test_plain_state_prepare_cannot_skip_review(self):
        with self.assertRaisesRegex(StateError,"Current reviews"):
            prepare(self.s,self.h.intent(self.h.gate_changes()))

    def test_multi_delivery_review_must_cover_exact_set_and_persist_manifest(self):
        a = self.h.asset
        review_a = self.h.review()
        self.h.asset = b = self.other_script()
        review_b = self.h.review()
        self.h.w["deliverable_ref"] = json.dumps([a["id"], b["id"]])
        i = self.h.intent(self.h.gate_changes())
        with self.assertRaisesRegex(StateError,"Missing review"):
            prepare(self.s,i,[review_a])
        p = prepare(self.s,i,[review_b,review_a])
        changed = next(c["after"] for c in p["changes"] if c["table"] == "Workflow")
        pins = json.loads(changed["deliverable_ref"])["targets"]
        self.assertEqual([x["id"] for x in pins],[a["id"],b["id"]])
        self.assertEqual(pins[1]["sha256"],review_b["target"]["sha256"])
        self.assertEqual(pins[1]["record_sha256"],fingerprint(b))

    def test_review_of_other_bytes_fails_with_correct_row_and_revision(self):
        review=self.h.review()
        review["target"]["sha256"]="b"*64
        with self.assertRaisesRegex(StateError,"material hash"):
            prepare(self.s,self.h.intent(self.h.gate_changes()),review)

    def test_direct_asset_with_wrong_preapproved_gate_delivery_fails(self):
        r = self.h.registry_state()
        refs = self.h.registry_evaluations(r)
        self.h.workflow("G10")["deliverable_ref"]="ANOTHER-REGISTERED-ID"
        i = self.h.intent([{"table":"Artifact Registry","id":r["id"],"expected_revision":1,
                            "values":{"status":"APPROVED",**refs}}])
        with self.assertRaisesRegex(StateError,"different delivery"):
            prepare(self.s,i,self.h.registry_review(r,"G10"))

    def test_qc_planned_even_with_review_and_human_message_is_pending(self):
        row = self.h.registry_state()
        for c in self.s["tables"]["Checklists"]:
            if c["gate_id"] == "G14":
                c.update(observed_or_planned="planned",evidence="Will inspect tomorrow")
        with self.assertRaisesRegex(StateError,"Observation required"):
            prepare(self.s,self.h.intent(self.h.gate_changes()),self.h.registry_review(row))

    def test_qc_observation_must_be_for_material_and_version_under_review(self):
        row = self.h.registry_state()
        c = next(c for c in self.s["tables"]["Checklists"] if c["gate_id"]=="G14")
        value = json.loads(c["evidence"])
        value["targets"][0]["revision"] += 1
        c["evidence"] = json.dumps(value)
        with self.assertRaisesRegex(StateError,"another version"):
            prepare(self.s,self.h.intent(self.h.gate_changes()),self.h.registry_review(row))

    def test_changed_or_removed_historical_rows_prevent_confirmation(self):
        p = self.edit()
        s = self.fresh(p["candidate"])
        logs = s["tables"]["Revision History"]
        logs.extend(self.event(p,"PREPARED")+self.event(p,"CONFIRMED"))
        self.assertEqual(verify_readback(p,s,True)["status"],"CONFIRMED")
        original = logs[0]
        logs[0] = {**original,"result":"changed old event"}
        with self.assertRaisesRegex(Conflict,"Known journal row"):
            verify_readback(p,s,True)
        logs.pop(0)
        with self.assertRaisesRegex(Conflict,"Known journal row"):
            verify_readback(p,s,True)

    def test_overlap_blocks_pending_and_allows_valid_unrelated_append(self):
        p = self.edit()
        other = self.edit(op="OTHER-EDITOR")
        other_row = self.edit(op="OTHER-ROW",table="Decisions",key="TEST-D-ROUNDTRIP")
        pre = self.fresh(self.s)
        logs = pre["tables"]["Revision History"]
        logs.extend(self.event(p,"PREPARED")+self.event(other_row,"PREPARED"))
        self.assertTrue(check_guards(p,pre,require_prepared=True))
        logs.extend(self.event(other,"PREPARED"))
        with self.assertRaisesRegex(Conflict,"same material"):
            check_guards(p,pre,require_prepared=True)

    def test_prewrite_expects_complete_own_prepared_event(self):
        p = self.edit()
        with self.assertRaisesRegex(StateError,"Missing journal PREPARED"):
            check_guards(p,self.fresh(self.s),require_prepared=True)

    def test_reconcile_requires_authorized_observed_versions_and_releases_with_new_operation(self):
        from reconciliation import observed_versions, reconcile, RESOLUTION
        p = self.edit()
        s = self.fresh(self.s)
        rows = s["tables"]["Revision History"]
        rows.extend(self.event(p,"PREPARED"))
        other = self.edit(op="NEW-DECISION")
        with self.assertRaisesRegex(Conflict,"Unresolved operation"):
            check_guards(other,s)
        view = observed_versions(p,s)
        auth = dict(authorized=True, actor="fixture-director", at=s["read_at"],decision=RESOLUTION,
                    reason="Keep the untouched version",user_message_ref="SYNTHETIC-RECONCILIATION")
        with self.assertRaisesRegex(StateError,"observed versions"):
            reconcile(p,s,auth)
        proposal = reconcile(p,s,{**auth,"observed_targets_sha256":view["observed_targets_sha256"]})
        self.assertEqual(proposal["observed"][0]["state"],"BEFORE")
        rows.append(proposal["row"])
        self.assertTrue(check_guards(other,s))
        with self.assertRaisesRegex(StateError,"unresolved incident"):
            check_guards(p,s)
        rows[-1]["changes_json"] = rows[-1]["changes_json"].replace("KEPT_OBSERVED_STATE","OTHER")
        with self.assertRaisesRegex(Conflict,"Unresolved operation"):
            check_guards(other,s)

    def test_long_single_revision_unicode_roundtrip_and_missing_chunk(self):
        old = "ação🎬" * 4200
        self.h.asset["text_or_ref"] = old
        p = self.edit(text=old+"!")
        s = self.fresh(p["candidate"])
        prepared, confirmed = self.event(p,"PREPARED"), self.event(p,"CONFIRMED")
        self.assertGreater(len(prepared),1)
        self.assertTrue(all(cell_units(r["changes_json"]) <= CELL_BUDGET for r in prepared))
        s["tables"]["Revision History"].extend(prepared[::-1]+confirmed[::-1])
        self.assertEqual(verify_readback(p,s,True)["status"],"CONFIRMED")
        s["tables"]["Revision History"].pop()
        with self.assertRaisesRegex(StateError,"journal part"):
            verify_readback(p,s,True)

    def test_native_business_cell_oversize_rejected_during_preparation(self):
        with self.assertRaisesRegex(StateError,"Business cell exceeds"):
            self.edit(text="🎬"*25001)

    def test_real_historical_11_plan_keeps_original_baseline(self):
        from public_journal_fixtures import fixture_pair
        plan,native=fixture_pair()
        self.assertEqual(verify_readback(plan,native,True)["status"],"CONFIRMED")
        native["tables"]["Revision History"] = [x for x in native["tables"]["Revision History"] if x["op_id"]==plan["op_id"]]
        with self.assertRaisesRegex(Conflict,"Known journal row"):
            verify_readback(plan,native,True)

if __name__ == "__main__":
    unittest.main()
