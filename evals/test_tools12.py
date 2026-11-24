"""Regression cases for the observed 1.1 media, camera, laboratory and export defects."""
import contextlib
import copy
import io
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import cpe
from harness_runtime import experiment
from media_tools import inspect,candidate_events
from previs import validate_geometry,camera_path,verify_blender_files
from prompt_compiler import compile_prompt,CompileError

def read(relative):
    return json.loads((ROOT/relative).read_text(encoding='utf-8'))

class Regression12(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace=Path(self.temp.name)
        self.room=read('templates/previs-room.json')
        self.spec=read('templates/optical-experiment.json')

    def cli(self,command,spec,extra=(),exit_code=0):
        input_file=self.workspace/'input.json'
        input_file.write_text(json.dumps(spec),encoding='utf-8')
        stdout=io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code=cpe.main([command,'--workspace',str(self.workspace),'--input',str(input_file),*extra])
        self.assertEqual(code,exit_code)
        receipt=json.loads(stdout.getvalue())
        result=json.loads(Path(receipt['result']).read_text(encoding='utf-8'))
        events=[json.loads(line) for line in Path(receipt['events']).read_text(encoding='utf-8').splitlines()]
        return result,events

    def test_gif_parameters_are_format_specific(self):
        spec=read('examples/prompt-specs/gpt_image_2_6.json')
        for params in ({'frame_count':9},{'output_format':'png','frame_duration_ms':100},
                       {'output_format':'gif','size':'289x289'},{'size':'-10x2'}):
            with self.subTest(params=params),self.assertRaises(CompileError):
                compile_prompt({**spec,'parameters':params})
        good={'output_format':'gif','size':'288x304','frame_count':9,'frame_duration_ms':100}
        self.assertEqual(compile_prompt({**spec,'parameters':good})['native_parameters'],good)

    def test_video_action_survives_normalization(self):
        spec=read('examples/prompt-specs/seedance_2_5.json')
        spec['intent']['action']=' \t '
        with self.assertRaisesRegex(CompileError,'action'):
            compile_prompt(spec)

    def test_path_checks_endpoints_and_frame_order(self):
        cam=self.room['cameras'][0]
        for path in ([{'frame':9,'position_m':[7,1,1]}],
                     [{'frame':7,'position_m':[1,2,1]},{'frame':4,'position_m':[1,2,1]}],
                     [{'frame':1,'position_m':[1,2,1]}],
                     [{'frame':True,'position_m':[1,2,1]}]):
            cam['path']=path
            with self.subTest(path=path),self.assertRaises(ValueError):
                validate_geometry(self.room)
        cam['path']=[{'frame':9,'position_m':[4,2,1]}]
        self.assertTrue(validate_geometry(self.room))
        self.assertEqual([k['frame'] for k in camera_path(cam,self.room['room_m'],False)],[1,9])

    def test_single_replication_and_comparison(self):
        self.assertEqual(experiment(self.spec)['design'],'ONE_VARIABLE_COMPARISON')
        variant=copy.deepcopy(self.spec['variants'][0])
        self.spec['variants']=[variant]
        self.assertFalse(experiment(self.spec)['single_variable_controlled'])
        self.spec['variants'].append({**variant,'id':'REPEAT'})
        self.assertEqual(experiment(self.spec)['design'],'REPLICATION')
        self.assertFalse(experiment(self.spec)['single_variable_controlled'])

    def test_all_labs_normal_entry_points(self):
        sample=ROOT/'examples/integrated-case/storyboard-contact.png'
        labs=read('harness/laboratories.json')
        self.assertEqual(len(labs),16)
        for lab in labs:
            family=lab['tool_family']
            settings={'optics':{'focal_mm':35},'previs_2d':self.room,'overlay':{'guides':['thirds']},
                      'image_analysis':{'source':str(sample)},'context':{'reference':'approved local script excerpt'}}[family]
            spec={**self.spec,'lab':lab['name'],'variants':[{'id':'V1','settings':settings}]}
            del spec['tool']
            with self.subTest(lab=lab['name']):
                result,events=self.cli('experiment',spec,['--source',str(sample)])
                self.assertEqual(result['tool'],family)
                missing_image_tools=any(importlib.util.find_spec(pkg) is None for pkg in ('PIL','numpy'))
                if missing_image_tools and family in ('previs_2d','overlay','image_analysis'):
                    self.assertEqual(result['kind'],'LAB_RESOURCE_REQUIRED')
                    continue
                self.assertEqual(result['execution_mode'],'GUIDED' if family=='context' else 'EXECUTED')
                if family=='context':
                    self.assertTrue(result['worksheet']['procedure'])
                    self.assertIsNone(result['observed_result'])
                    self.assertEqual(events[-1]['status'],'PLANNED')
                else:
                    self.assertEqual(len(result['observed_result']),1)

    def test_missing_image_is_pending(self):
        spec={**self.spec,'lab':'Color','tool':'image_analysis','variants':[{'id':'V1','settings':{}}]}
        result,events=self.cli('experiment',spec)
        self.assertEqual(result['kind'],'LAB_RESOURCE_REQUIRED')
        self.assertEqual(events[-1]['status'],'PLANNED')

    def test_blender_failed_receipt_has_failed_events(self):
        result,events=self.cli('blender',self.room,['--blender',str(self.workspace/'missing.exe')],2)
        self.assertEqual(result['status'],'UNAVAILABLE')
        self.assertEqual([e['status'] for e in events[-3:]],['FAILED','FAILED','FAILED'])

    def test_blender_requires_each_file_referenced_by_the_receipt(self):
        # The recorded render can be moved together with its geometry and receipt.
        source=ROOT/'examples/blender-trajectory'
        result=read('examples/blender-trajectory/blender-result.json')
        ids=[c['id'] for c in result['cameras']]
        for name in ['technical-previs.blend']+[cam+'.png' for cam in ids]:
            shutil.copyfile(source/name,self.workspace/name)
        result['blend']=str(self.workspace/'technical-previs.blend')
        result['renders']=[str(self.workspace/(cam+'.png')) for cam in ids]
        verify_blender_files(result,self.workspace,ids)
        (self.workspace/(ids[0]+'.png')).write_bytes(b'')
        with self.assertRaisesRegex(ValueError,'PNG'):
            verify_blender_files(result,self.workspace,ids)

    def test_clip_oversized_intervals_and_incomplete_intervals(self):
        logs={'black_freeze':'black_start:-0.2 black_end:0.75 black_duration:0.95\nlavfi.freezedetect.freeze_start: 0.2',
              'silence':'silence_start: -0.1\nsilence_end: 0.8 | silence_duration: 0.9',
              'cuts':'pts_time:0.19\npts_time:0.4\npts_time:0.8'}
        events=candidate_events(logs,.4)
        self.assertEqual(events['cut_seconds'],[.19])
        self.assertEqual(events['black_intervals'],[{'start':0,'end':.4,'duration':.4}])
        self.assertEqual(events['silence_intervals'][0]['end'],.4)
        self.assertTrue(events['freeze_intervals'][0]['ends_at_window'])

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe') and importlib.util.find_spec('PIL') and importlib.util.find_spec('numpy'),'requires local FFmpeg, FFprobe, Pillow and NumPy')
    def test_real_video_finds_cuts_only_in_requested_window(self):
        fixture=ROOT/'examples/integrated-case/qc-fixture.mp4'
        for seconds,expected in ((.4,[]),(2.5,[1.,2.])):
            with self.subTest(seconds=seconds):
                result=inspect(fixture,self.workspace/str(seconds),max_seconds=seconds,sample_fps=2)
                events=result['candidate_events']
                self.assertEqual(events['cut_seconds'],expected)
                self.assertAlmostEqual(sum(events['candidate_shot_durations_seconds']),seconds)
                for key in ['black_intervals','freeze_intervals','silence_intervals']:
                    for interval in events[key]:
                        self.assertTrue(0<=interval['start']<interval['end']<=seconds)

if __name__=='__main__':
    unittest.main()
