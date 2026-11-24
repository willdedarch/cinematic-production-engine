"""Real FFmpeg controls for the production handoff, return, import and approval paths."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import test_series_release as fixtures
from shared_state import StateError, fingerprint, index
from shot_workflow import compare_handoff, handoff


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'Requires installed FFmpeg and FFprobe')
class MediaQC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temporary.cleanup)
        cls.workspace = Path(temporary.name)
        cls.snapshot = fixtures.example.scenario(cls.workspace/'state')
        cls.shot = next(row for row in cls.snapshot['tables']['Shot List'] if row['duration_s']==8)
        cls.good = cls.workspace/'good.mp4'
        cls.silent = cls.workspace/'silent.mp4'
        cls.short = cls.workspace/'short.mp4'
        cls.square = cls.workspace/'square.mp4'
        cls.audio = cls.workspace/'audio.m4a'
        cls.corrupt = cls.workspace/'corrupt.mp4'
        cls.warning = cls.workspace/'duration-from-container.mkv'

        def ffmpeg(*args):
            subprocess.run(['ffmpeg','-nostdin','-v','error',*map(str,args)],check=True,capture_output=True,timeout=30)

        ffmpeg('-f','lavfi','-i','color=c=blue:s=1280x720:r=24:d=8',
               '-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=8',
               '-vf','setsar=1','-c:v','libx264','-preset','ultrafast','-threads','1','-c:a','aac',
               '-movflags','+faststart',cls.good)
        ffmpeg('-i',cls.good,'-map','0:v','-c','copy',cls.silent)
        ffmpeg('-i',cls.good,'-t','4','-c','copy',cls.short)
        ffmpeg('-i',cls.silent,'-vf','crop=720:720,setsar=1','-c:v','libx264','-preset','ultrafast','-threads','1',cls.square)
        ffmpeg('-i',cls.good,'-vn','-c','copy',cls.audio)
        ffmpeg('-i',cls.good,'-c','copy',cls.warning)
        original=cls.good.read_bytes()
        cls.corrupt.write_bytes(original[:len(original)//2])

    def packet(self, audio=True, native=None, requirements=None):
        settings={'mode':'omni_reference',**(native or {})}
        if audio is not None:
            settings['generate_audio']=audio
        spec={'model_id':'seedance_2_5','shot_id':self.shot['id'],'parameters':settings}
        if requirements is not None:
            spec['return_requirements']=requirements
        return handoff(self.snapshot,spec)

    def cli(self, snapshot, command, spec, fail=False):
        directory=self.workspace/self.id().split('.')[-1]
        directory.mkdir(exist_ok=True)
        state,request=directory/'snapshot.json',directory/'request.json'
        state.write_text(json.dumps(snapshot),encoding='utf8')
        request.write_text(json.dumps(spec),encoding='utf8')
        response = subprocess.run([sys.executable,'-B',str(fixtures.ROOT/'scripts/cpe.py'),command,
            '--workspace',str(directory/'runs'),'--snapshot',str(state),'--input',str(request)],
            capture_output=True,encoding='utf8',timeout=60)
        if fail:
            self.assertNotEqual(response.returncode,0,response.stdout)
            return response.stderr
        self.assertEqual(response.returncode,0,response.stderr)
        return json.loads(Path(json.loads(response.stdout)['result']).read_text(encoding='utf8'))

    def review(self, source, packet):
        return compare_handoff(self.snapshot,packet,source,True)

    def import_spec(self, source, packet):
        return {'shot':packet['shot'],'handoff':packet,'path':str(source),'asset_id':'QC-RETURN','kind':'FINAL_ASSET',
                'origin':'Generated local control','rights':'Original audio and video signal','rights_confirmed':True,
                'decision_id':'QC-RETURN-LINK','reason':'Verify the exact returned media',
                'authorization':fixtures.example.auth('QC-IMPORT')}

    def test_real_positive_contract_and_no_automatic_approval(self):
        packet=self.packet(native={'resolution':'720p'},requirements={'width':1280,'height':720,'fps':'24/1',
                      'streams':{'video':1,'audio':1,'subtitle':0},'format':'mp4','video_codec':'H.264','audio_codec':'aac'})
        review=self.cli(self.snapshot,'shot-compare',{'handoff':packet,'path':str(self.good),'rights_confirmed':True})
        self.assertEqual(review['technical_review'],'SPEC_CHECKED')
        self.assertTrue(all(r['status']=='PASS' for r in review['check_details'].values() if r['required']))
        self.assertFalse(review['approved'])
        imported=self.cli(self.snapshot,'shot-import',self.import_spec(self.good,packet))
        self.assertEqual(imported['kind'],'WRITE_PLAN_NOT_SAVED')
        self.assertFalse(imported['return_comparison']['approved'])
        registry=index(imported['candidate'])['Artifact Registry']['QC-RETURN']
        self.assertEqual(registry['status'],'REVIEW_REQUIRED')
        approval={**fixtures.example.auth('QC-APPROVE'),'at':datetime.now(timezone.utc).isoformat(),
                  'changes':[{'table':'Artifact Registry','id':registry['id'],'expected_revision':registry['revision'],
                              'values':{'status':'APPROVED'}}]}
        error=self.cli(imported['candidate'],'prepare',approval,fail=True)
        self.assertIn('Current reviews required',error)

    def test_silent_video_fails_comparator_import_and_approval(self):
        packet=self.packet(native={'resolution':'720p'})
        review=self.cli(self.snapshot,'shot-compare',{'handoff':packet,'path':str(self.silent),'rights_confirmed':True})
        self.assertEqual(review['technical_review'],'MISMATCH')
        self.assertEqual(review['check_details']['audio_stream']['status'],'FAIL')
        self.assertFalse(review['observed']['audio_stream'])
        self.assertIn('specification: audio_stream',self.cli(self.snapshot,'shot-import',self.import_spec(self.silent,packet),fail=True))
        attempted=fixtures.example.auth('QC-BYPASS')
        attempted['at']=datetime.now(timezone.utc).isoformat()
        attempted['changes']=[{'table':'Artifact Registry','id':'QC-RETURN','expected_revision':None,
                             'values':{'status':'APPROVED'}}]
        self.assertIn('Save a draft before approving an asset',self.cli(self.snapshot,'prepare',attempted,fail=True))

    def test_legacy_seal_reapplies_explicit_audio_requirement(self):
        packet=copy.deepcopy(self.packet())
        previous=packet['production_brief']['expected_media']
        packet['production_brief']['expected_media']={k:previous[k] for k in ('duration_s','aspect_ratio')}
        packet['handoff_sha256']=fingerprint({k:v for k,v in packet.items() if k!='handoff_sha256'})
        result=self.review(self.silent,packet)
        self.assertEqual(result['technical_review'],'MISMATCH')
        self.assertEqual(result['check_details']['audio_stream']['status'],'FAIL')

    def test_disabled_and_unspecified_audio_are_distinct(self):
        packet=self.packet(audio=False)
        self.assertEqual(self.review(self.silent,packet)['check_details']['audio_stream']['status'],'PASS')
        self.assertEqual(self.review(self.good,packet)['check_details']['audio_stream']['status'],'FAIL')
        self.assertEqual(self.review(self.silent,self.packet(audio=None))['check_details']['audio_stream']['status'],'NOT_APPLICABLE')
        with self.assertRaisesRegex(StateError,'conflicts with the explicit native audio setting'):
            self.packet(requirements={'audio_stream':False})

    def test_real_media_type_integrity_duration_and_delivery_mismatches(self):
        packet=self.packet()
        self.assertEqual(self.review(self.audio,packet)['check_details']['media_type']['status'],'FAIL')
        image=next((fixtures.ROOT/'examples/series-worked/frames').glob('*.png'))
        still=self.review(image,packet)
        self.assertEqual(still['observed']['media_type'],'image')
        self.assertEqual(still['check_details']['media_type']['status'],'FAIL')
        corrupt=self.review(self.corrupt,packet)
        self.assertEqual(corrupt['observed']['media_type'],'video')
        self.assertEqual(corrupt['check_details']['integrity']['status'],'FAIL')
        self.assertEqual(self.review(self.short,packet)['check_details']['duration_s']['status'],'FAIL')
        self.assertEqual(self.review(self.square,self.packet(audio=None))['check_details']['aspect_ratio']['status'],'FAIL')
        wrong={'resolution':'960x540','width':960,'height':540,'fps':60,'streams':{'video':2},'format':'webm',
               'video_codec':'hevc','audio_codec':'opus'}
        report=self.review(self.good,self.packet(requirements=wrong))
        self.assertEqual(set(wrong),{k for k,v in report['check_details'].items() if v['status']=='FAIL'})

    def test_missing_tool_and_weak_metadata_never_count_as_complete(self):
        packet=self.packet()
        which=shutil.which
        with patch('return_media.shutil.which',side_effect=lambda name: None if name=='ffmpeg' else which(name)):
            result=self.review(self.good,packet)
        self.assertEqual(result['technical_review'],'INCOMPLETE')
        self.assertEqual(result['check_details']['integrity']['status'],'UNKNOWN')
        mkv=self.review(self.warning,packet)
        self.assertEqual(mkv['technical_review'],'INCOMPLETE')
        self.assertEqual(mkv['check_details']['duration_s']['status'],'WARNING')
