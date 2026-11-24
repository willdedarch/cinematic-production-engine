"""Independent checks of shot lineage, repair scope and episode initialization."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import test_series_release as fixtures
from episode_workflow import initialize_episode
from shared_state import StateError, canonical, index, prepare
from shot_workflow import dispatch, ref, impact


class ShotIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder=tempfile.TemporaryDirectory()
        cls.addClassCleanup(folder.cleanup)
        cls.directory=Path(folder.name)
        cls.example=fixtures.example.scenario(cls.directory)

    def setUp(self):
        self.snapshot=copy.deepcopy(self.example)
        self.ix=index(self.snapshot)
        self.row=self.ix["Shot List"]["SH05"]

    def run_shot(self, cmd, spec):
        return dispatch(cmd,self.snapshot,spec,self.directory)

    def repair(self):
        state=json.loads(self.row["start_end_state"])
        state["out"]["cantil"]="sobre o banco"
        return {"shot_id":"SH05","field":"cantil","impact":impact(self.snapshot,"SH05","cantil"),
                "pins":{"SH05":ref("Shot List",self.row)},"fields":{"SH05":["start_end_state"]},
                "authorization":fixtures.example.auth("REPAIR-INTEGRITY"),
                "changes":[{"table":"Shot List","id":"SH05","expected_revision":self.row["revision"],
                            "values":{"start_end_state":canonical(state)}}]}

    def test_scoped_repair_and_current_read_guard(self):
        spec=self.repair()
        plan=self.run_shot("shot-repair",spec)
        self.assertEqual([c["id"] for c in plan["changes"]],["SH05"])
        self.row["revision"]+=1
        with self.assertRaisesRegex(StateError,"Impact changed"):
            self.run_shot("shot-repair",spec)

    def test_repair_cannot_rewrite_another_continuity_field(self):
        spec=self.repair()
        patch=spec["changes"][0]["values"]
        state=json.loads(patch["start_end_state"])
        state["out"]["tampa"]="lançada pela janela"
        patch["start_end_state"]=canonical(state)
        with self.assertRaisesRegex(StateError,"another protected field"):
            self.run_shot("shot-repair",spec)

    def test_successor_inherits_unedited_fields_and_scope(self):
        spec=self.repair()
        ch=spec["changes"][0]
        ch.update(id="SH05-V2",expected_revision=None)
        ch["values"].update(supersedes_id="SH05",version="2",status="DRAFT",
                            **{k:self.row[k] for k in ("is_test","episode_id","project_id")})
        spec["fields"]={"SH05-V2":["start_end_state"]}
        plan=self.run_shot("shot-repair",spec)
        self.assertEqual(plan["changes"][0]["after"]["action"],self.row["action"])
        self.assertEqual(plan["changes"][0]["after"]["location_id"],self.row["location_id"])
        ch["values"]["episode_id"]="SERIE-AGUA-EP2"
        with self.assertRaisesRegex(StateError,"episode"):
            self.run_shot("shot-repair",spec)

    def test_stale_pin_or_unlinked_target_cannot_be_repaired(self):
        spec=self.repair()
        spec["pins"]["SH05"]["sha256"]="a"*64
        with self.assertRaisesRegex(StateError,"predecessor version"):
            self.run_shot("shot-repair",spec)
        spec=self.repair()
        spec["changes"][0]["id"]="SH01"
        with self.assertRaisesRegex(StateError,"current relationship"):
            self.run_shot("shot-repair",spec)

    def test_preference_requires_same_shot_and_previously_registered_media(self):
        spec={"from":ref("Shot List",self.row),"to":ref("Artifact Registry",self.ix["Artifact Registry"]["TAKE-06"]),
              "relation":"selected_take","decision_id":"WRONG-TAKE","reason":"Synthetic test",
              "authorization":fixtures.example.auth("WRONG-TAKE")}
        with self.assertRaisesRegex(StateError,"Register this exact take"):
            self.run_shot("shot-link",spec)
        spec["relation"]="take"
        spec["to"]=ref("Artifact Registry",next(r for r in self.ix["Artifact Registry"].values() if r["kind"]=="REFERENCE"))
        with self.assertRaisesRegex(StateError,"registered media"):
            self.run_shot("shot-link",spec)

    def test_typed_relationship_through_generic_prepare_requires_current_pin(self):
        row=next(r for r in self.ix["Decisions"].values() if r["topic"]=="CPE_SHOT_LINK_V1")
        data=json.loads(row["choice"]);end=data["from"]
        old=self.ix[end["table"]][end["id"]]
        old["revision"]+=1
        auth=fixtures.example.auth("FAKE-OLD")
        values={k:v for k,v in row.items() if k not in {"id","revision","updated_at","updated_by","last_op_id"}}
        values["user_message_ref"]=auth["user_message_ref"]
        intent={**auth,"at":"2026-11-24T19:10:00Z","changes":[{"table":"Decisions","id":"FAKE-OLD-LINK",
                "expected_revision":None,"values":values}]}
        with self.assertRaisesRegex(StateError,"stale version"):
            prepare(self.snapshot,intent)

    def test_attachment_order_follows_adapter_then_explicit_role_order(self):
        normal={"shot_id":"SH05","model_id":"seedance_2_5","parameters":{"mode":"omni_reference"}}
        first=self.run_shot("shot-handoff",normal)["attachment_order"][0]["id"]
        sample=self.ix["Artifact Registry"][first]
        for key,role in [("SECOND-IMAGE","image_references"),("START","start_image")]:
            source={**sample,"id":key}
            self.snapshot["tables"]["Artifact Registry"].append(source)
            spec={"from":ref("Artifact Registry",source),"to":ref("Shot List",self.row),
                  "role":role,"relation":"reference","decision_id":"LINK-"+key,"reason":"Teste de ordenação",
                  "authorization":fixtures.example.auth("LINK-"+key)}
            self.snapshot=self.run_shot("shot-link",spec)["candidate"]
        with self.assertRaisesRegex(StateError,"require explicit order"):
            self.run_shot("shot-handoff",normal)
        spec={**normal,"reference_order":{"image_references":["SECOND-IMAGE",first]}}
        before=self.run_shot("shot-handoff",spec)["attachment_order"]
        self.assertEqual([x["id"] for x in before],["START","SECOND-IMAGE",first])
        self.snapshot["tables"]["Decisions"].reverse()
        self.assertEqual(self.run_shot("shot-handoff",spec)["attachment_order"],before)

    def test_initialize_rejects_silent_switch_of_test_scope(self):
        spec={"project_id":self.row["project_id"],"include_test":True,"is_test":False,"new_episode":True,
              "episode_title":"EP3","target_seconds":45}
        with self.assertRaisesRegex(StateError,"scope differs"):
            initialize_episode(self.snapshot,spec,fixtures.example.auth("EP3"))

    def test_normal_cli_handoff_compiles_timeline_with_current_shot_and_attachments(self):
        normal = {'shot_id':'SH05','model_id':'seedance_2_5','parameters':{'mode':'omni_reference'}}
        legacy = self.run_shot('shot-handoff',normal)
        self.assertNotIn('cinematic_plan',legacy)
        reference = legacy['attachment_order'][0]['id']
        states = json.loads(self.row['start_end_state'])
        plan = {'cast':{'davi':'Davi','lia':'Lia'},'beats':[
            {'id':'hesitation','start_s':0,'end_s':4,'subjects':['davi'],'action':'Davi hesita antes da oferta.',
             'entry':states['in'],'references':[reference]},
            {'id':'handover','start_s':4,'end_s':self.row['duration_s'],'subjects':['davi','lia'],
             'action':'Lia recebe o cantil.','exit':states['out']},
        ]}
        spec = {**normal,'shot':legacy['shot'],'cinematic_plan':plan}
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            snapshot, request = base/'snapshot.json', base/'request.json'
            snapshot.write_text(json.dumps(self.snapshot),encoding='utf8')
            request.write_text(json.dumps(spec),encoding='utf8')
            run = subprocess.run([sys.executable,'-B',str(fixtures.ROOT/'scripts/cpe.py'),'shot-handoff',
                                  '--workspace',str(base/'run'),'--snapshot',str(snapshot),'--input',str(request)],
                                 capture_output=True,encoding='utf8')
            self.assertEqual(run.returncode,0,run.stderr)
            result = json.loads(Path(json.loads(run.stdout)['result']).read_text(encoding='utf8'))
        self.assertIn('0–4 s',result['delivery']['prompt'])
        self.assertIn('Lia recebe o cantil.',result['delivery']['prompt'])
        self.assertEqual(result['attachment_order'],legacy['attachment_order'])
        self.assertEqual(result['cinematic_plan']['duration_s'],self.row['duration_s'])
        self.assertEqual(result['execution'],'MANUAL')

        wrong_duration = {**spec,'cinematic_plan':{**plan,'duration_s':8}}
        with self.assertRaisesRegex(StateError,'duration differs from shot'):
            self.run_shot('shot-handoff',wrong_duration)
        conflict = copy.deepcopy(spec)
        field = next(iter(states['out']))
        conflict['cinematic_plan']['beats'][-1]['exit'][field] = 'outra posição'
        with self.assertRaisesRegex(StateError,'conflicts with shot out state'):
            self.run_shot('shot-handoff',conflict)
        stale = {**spec,'shot':{**spec['shot'],'revision':0}}
        with self.assertRaisesRegex(StateError,'Shot changed'):
            self.run_shot('shot-handoff',stale)
