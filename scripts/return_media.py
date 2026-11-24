"""Technical contract and local measurement for the returned media of a sealed shot."""
import math
import re
import shutil
import subprocess
from fractions import Fraction

from shared_state import require


FIELDS = {'resolution','width','height','fps','audio_stream','streams','format','video_codec','audio_codec'}
STREAM_TYPES = {'video','audio','subtitle','data','attachment','unknown'}
RATIO = r'[1-9]\d*:[1-9]\d*'
RESOLUTION = r'[1-9]\d*x[1-9]\d*|[1-9]\d*p|[1-9]\d*k'


def positive_number(value):
    if type(value) is bool:
        return None
    try:
        number = float(Fraction(str(value)))
    except (ValueError, TypeError, OverflowError, ZeroDivisionError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def contract(duration, ratio, native, requested):
    """Keep delivery requirements separate from provider controls and validate conflicts."""
    require(isinstance(requested,dict) and set(requested)<=FIELDS,'Unknown return media requirements')
    result = {'media_type':'video','duration_s':duration, 'aspect_ratio':ratio if ratio!='auto' else None}
    wanted = dict(requested)
    for field in ('width','height'):
        require(field not in wanted or type(wanted[field]) is int and wanted[field]>0,field+' must be a positive pixel count')
    if 'fps' in wanted:
        wanted['fps'] = positive_number(wanted['fps'])
        require(wanted['fps'] is not None,'fps must be a positive rate or fraction')
    if 'audio_stream' in wanted:
        require(type(wanted['audio_stream']) is bool,'audio_stream must be true or false')
    if type(native.get('generate_audio')) is bool:
        require(wanted.get('audio_stream',native['generate_audio']) is native['generate_audio'],
                'Return audio requirement conflicts with the explicit native audio setting')
        result['audio_stream'] = native['generate_audio']
    if 'streams' in wanted:
        counts = wanted['streams']
        require(isinstance(counts,dict) and counts and set(counts)<=STREAM_TYPES and
                all(type(n) is int and n>=0 for n in counts.values()) and counts.get('video',1)>0,
                'Invalid expected stream counts for a video handoff')
        audio = wanted.get('audio_stream',result.get('audio_stream'))
        require(audio is None or 'audio' not in counts or audio is bool(counts['audio']),
                'Audio requirement conflicts with the audio stream count')
    for field in ('format','video_codec','audio_codec'):
        if field in wanted:
            require(isinstance(wanted[field],str) and re.fullmatch(r'[A-Za-z0-9._+-]+',wanted[field]),
                    'Use the exact media format or FFprobe codec name for '+field)
            token = wanted[field].casefold()
            wanted[field] = {'h.264':'h264','h.265':'hevc'}.get(token,token) if field.endswith('_codec') else token
    if 'audio_codec' in wanted:
        require(wanted.get('audio_stream',result.get('audio_stream')) is not False and
                wanted.get('streams',{}).get('audio',1)>0,'Audio codec conflicts with a return without audio')

    native_resolution = '480p' if native.get('draft') else native.get('resolution','').casefold()
    if 'resolution' in wanted:
        value = wanted['resolution']
        require(isinstance(value,str) and re.fullmatch(RESOLUTION,value.casefold()),'Use a resolution class or pixel dimensions such as 1280x720')
        value = value.casefold()
        if 'x' in value:
            width,height = map(int,value.split('x'))
            require(wanted.get('width',width)==width and wanted.get('height',height)==height,'Resolution conflicts with the exact dimensions')
            if native_resolution and native_resolution.endswith('p'):
                require(min(width,height)==int(native_resolution[:-1]),'Resolution conflicts with the native output setting')
        elif native_resolution:
            require(value==native_resolution,'Resolution conflicts with the native output setting')
        if value.endswith('k') and {'width','height'}<=wanted.keys():
            value = f"{wanted['width']}x{wanted['height']}"
        wanted['resolution'] = value
    elif native_resolution:
        if native_resolution.endswith('p') and {'width','height'}<=wanted.keys():
            require(min(wanted['width'],wanted['height'])==int(native_resolution[:-1]),
                    'Exact dimensions conflict with the native output setting')
        result['resolution'] = native_resolution
        if result['resolution'].endswith('k') and {'width','height'}<=wanted.keys():
            result['resolution'] = f"{wanted['width']}x{wanted['height']}"
    return {**result,**wanted}


def container_format(meta):
    """Distinguish common formats sharing a demuxer when the container exposes a brand."""
    names = (meta.get('format_name') or '').casefold().split(',')
    if len(names)==1:
        return names[0] or None,names
    brand = str(meta.get('tags',{}).get('major_brand','')).strip().casefold()
    if 'mov' in names and 'mp4' in names:
        if brand=='qt':
            return 'mov',names
        if re.fullmatch(r'iso[0-9m]|mp4[12]|avc1|dash|m4v|msnv',brand):
            return 'mp4',names
        if brand=='m4a':
            return 'm4a',names
        if brand.startswith(('3gp','3g2')):
            return brand[:3],names
    return None,names


def measurements(metadata):
    files = metadata.get('format') or {}
    tracks = {}
    rows = metadata.get('streams')
    known = isinstance(rows,list)
    videos,audios = [],[]
    for row in rows if known else []:
        kind = 'attachment' if row.get('disposition',{}).get('attached_pic') else row.get('codec_type','unknown')
        tracks[kind] = tracks.get(kind,0)+1
        if kind=='video':
            videos.append(row)
        elif kind=='audio':
            audios.append(row)
    video = next((row for row in videos if row.get('disposition',{}).get('default')),videos[0] if videos else {})
    container,aliases = container_format(files)
    still = any(name in {'image2','image2pipe','gif','apng','ico'} or name.endswith('_pipe') for name in aliases)
    media_type = 'image' if still and videos else 'video' if videos else 'audio' if audios else 'other'
    width,height = (video.get(name) if type(video.get(name)) is int and video[name]>0 else None for name in ('width','height'))
    dar,sar = str(video.get('display_aspect_ratio')),str(video.get('sample_aspect_ratio'))
    aspect = Fraction(dar.replace(':','/')) if re.fullmatch(RATIO,dar) else None
    if aspect is None and width and height and re.fullmatch(RATIO,sar):
        aspect = Fraction(width,height)*Fraction(sar.replace(':','/'))
    rotation = next((row['rotation'] for row in video.get('side_data_list',[]) if 'rotation' in row),0)
    if aspect and type(rotation) in (int,float) and abs(rotation)%180==90:
        aspect = 1/aspect
    duration = positive_number(video.get('duration'))
    total = positive_number(files.get('duration'))
    observed = {'media_type':media_type if known else None,'duration_s':duration or total,'container_duration_s':total,
                'duration_source':'video_stream' if duration else 'container' if total else None,
                'display_aspect_ratio':f'{aspect.numerator}:{aspect.denominator}' if aspect else None,
                'pixel_width':width,'pixel_height':height,'fps':positive_number(video.get('avg_frame_rate')),
                'nominal_fps':positive_number(video.get('r_frame_rate')),'audio_stream':bool(audios) if known else None,
                'streams':tracks if known else None,'format':container,'format_aliases':aliases,
                'video_codec':[row.get('codec_name') for row in videos], 'audio_codec':[row.get('codec_name') for row in audios]}
    indexes = [row.get('index') for row in videos+audios]
    return observed,indexes if all(type(i) is int and i>=0 for i in indexes) else [],total


def decode(path,indexes,duration):
    executable = shutil.which('ffmpeg')
    if not executable:
        return 'UNKNOWN','FFmpeg indisponível para testar a decodificação.'
    if not indexes or duration is None or duration>120:
        return 'UNKNOWN','Duração ausente ou superior a 120 s, limite para decodificação integral.'
    args = [executable,'-nostdin','-v','error','-xerror','-abort_on','empty_output_stream','-err_detect','explode',
            '-protocol_whitelist','file,pipe','-i',str(path)]
    for index in indexes:
        args.extend(['-map',f'0:{index}'])
    try:
        result = subprocess.run(args+['-f','null','-'],capture_output=True,timeout=45,shell=False)
    except (OSError,subprocess.TimeoutExpired):
        return 'UNKNOWN','O teste de decodificação não foi concluído no ambiente local.'
    if result.returncode:
        return 'FAIL','FFmpeg encontrou erro ao decodificar os streams selecionados.'
    return 'PASS','Decodificação integral dos streams de vídeo e áudio presentes.'


def evaluate(expected,observed,integrity):
    checks = {}

    def check(key,seen,matches=None,evidence='',status=None):
        wanted = 'decoded' if key=='integrity' else expected.get(key)
        required = wanted is not None
        if status is None:
            status = 'NOT_APPLICABLE' if not required else 'UNKNOWN' if seen is None else 'PASS' if matches else 'FAIL'
        checks[key] = {'status':status,'required':required,'expected':wanted,'observed':seen}
        if evidence:
            checks[key]['evidence'] = evidence

    media_type=observed['media_type']
    check('media_type',media_type,media_type==expected['media_type'])
    check('integrity',None if integrity[0]=='UNKNOWN' else integrity[0]=='PASS',evidence=integrity[1],status=integrity[0])
    duration,total = observed['duration_s'],observed['container_duration_s']
    rate = observed['fps'] or observed['nominal_fps']
    tolerance = max(0.05,1/rate) if rate else 0.05
    if duration is not None and observed['duration_source']=='container':
        check('duration_s',duration,evidence='Duração do contêiner. O stream principal não declara duração.',
              status='FAIL' if duration+tolerance < expected['duration_s'] else 'WARNING')
    else:
        check('duration_s',duration,duration is not None and abs(duration-expected['duration_s'])<=tolerance and
              (total is None or abs(total-expected['duration_s'])<=tolerance),
              'Conferência da duração do vídeo e do contêiner.' if duration is not None and total is not None else '')
    aspect = observed['display_aspect_ratio']
    wanted_aspect = expected.get('aspect_ratio')
    check('aspect_ratio',aspect,bool(aspect and wanted_aspect and Fraction(aspect.replace(':','/'))==
                                    Fraction(wanted_aspect.replace(':','/'))))
    width,height = observed['pixel_width'],observed['pixel_height']
    check('width',width,width==expected.get('width'))
    check('height',height,height==expected.get('height'))
    resolution = expected.get('resolution')
    dimensions = f'{width}x{height}' if width and height else None
    if dimensions and resolution and resolution.endswith('p'):
        check('resolution',f'{min(width,height)}p',min(width,height)==int(resolution[:-1]),'Menor dimensão da imagem codificada.')
    elif dimensions and resolution and resolution.endswith('k'):
        check('resolution',dimensions,evidence='Classe do provedor sem dimensões inequívocas. Declare largura e altura.',status='UNKNOWN')
    else:
        check('resolution',dimensions,dimensions==resolution)
    fps,nominal = observed['fps'],observed['nominal_fps']
    wanted_fps = expected.get('fps')
    check('fps',fps,bool(fps and wanted_fps and math.isclose(fps,wanted_fps,rel_tol=0.0001,abs_tol=0.005)),
          'Taxa média do stream. A constância dos intervalos pede inspeção separada.')
    if fps and nominal and not math.isclose(fps,nominal,rel_tol=0.0001,abs_tol=0.005):
        check('cadence',nominal,evidence='Taxa média e nominal diferem.',status='WARNING')
    audio = observed['audio_stream']
    check('audio_stream',audio,audio==expected.get('audio_stream'))
    streams = observed['streams']
    check('streams',streams,streams is not None and all(streams.get(kind,0)==count for kind,count in expected.get('streams',{}).items()))
    container,aliases = observed['format'],observed['format_aliases']
    want_format = expected.get('format')
    if want_format and container is None and any(aliases) and want_format not in aliases:
        check('format',aliases,evidence='O contêiner esperado não pertence ao demuxer observado.',status='FAIL')
    else:
        check('format',container,container==want_format,'Demuxer sem identificação de um formato único.' if container is None else '')
    for key in ('video_codec','audio_codec'):
        codecs = observed[key]
        check(key,codecs if streams is not None and None not in codecs else None,
              bool(codecs) and all(codec==expected.get(key) for codec in codecs))
    return checks
