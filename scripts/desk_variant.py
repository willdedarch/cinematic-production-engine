"""Make a local alternate sound edit while preserving video, duration and original bytes."""
import hashlib, json, math, os, shutil, subprocess, tempfile
from pathlib import Path
from media_tools import probe
from shared_state import canonical, fingerprint, require

def audio_shift(source, target, offset_ms):
    source=Path(source).resolve()
    target=Path(target).resolve()
    require(source.is_file() and target!=source and not target.exists(), "Choose a new output file")
    require(target.suffix.lower()=='.mp4', "The local edit produces an MP4")
    meta=probe(source)
    require({'video','audio'} <= {s['codec_type'] for s in meta['streams']}, "Need video and audio")
    duration=float(meta['format']['duration'])
    require(type(offset_ms) is int and 0<abs(offset_ms)<duration*1000 and math.isfinite(duration), "Invalid audio shift")
    ff=shutil.which('ffmpeg')
    require(ff,"FFmpeg unavailable")
    target.parent.mkdir(parents=True,exist_ok=True)
    prefix=(f'atrim=start={-offset_ms/1000:g},asetpts=PTS-STARTPTS' if offset_ms<0 else f'adelay={offset_ms}:all=1')
    with tempfile.TemporaryDirectory(dir=target.parent) as tmp:
        new=Path(tmp)/'alternate.mp4'
        args=[ff,'-nostdin','-hide_banner','-v','error','-i',str(source),'-map','0:v:0','-map','0:a:0','-c:v','copy','-af',prefix+',apad','-c:a','aac','-t',str(duration),'-movflags','+faststart',str(new)]
        subprocess.run(args,check=True,capture_output=True)
        require(abs(float(probe(new)['format']['duration'])-duration)<0.10, "Unexpected alternate duration")
        if os.name=='nt':
            new.rename(target)  # Windows rename refuses to replace an existing file.
        else:
            os.link(new,target)
    with target.open('rb') as f: sha=hashlib.file_digest(f,'sha256').hexdigest()
    return {'kind':'LOCAL_EDIT_REQUIRES_REVIEW','path':str(target),'sha256':sha,'offset_ms':offset_ms,'duration_s':duration}

def materialize(workspace,key,source,provenance):
    root=Path(workspace).resolve()
    variants=root/'variantes'
    require(variants.resolve().is_relative_to(root) and not variants.is_symlink(),'Destino de edição inválido.')
    variants.mkdir(parents=True,exist_ok=True)
    destination=variants/key
    def checked(directory):
        require(directory.resolve().parent==variants.resolve() and not directory.is_symlink(),'Destino de edição inválido.')
        file=directory/'alternativa.mp4';info=directory/'origem.json'
        require(file.is_file() and info.is_file() and not file.is_symlink() and not info.is_symlink(),
                'A variação local está incompleta.')
        cached=json.loads(info.read_text(encoding='utf-8'))
        with file.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
        require(cached.get('provenance')==provenance and cached.get('sha256')==digest,'Comprovante da variação diverge.')
        return file
    # Preserve an incomplete derivative from an interrupted older client.
    if destination.is_dir() and not (destination/'origem.json').is_file():
        destination=variants/(key+'-recuperada-'+fingerprint(provenance)[:12])
    if destination.exists():return checked(destination)
    with tempfile.TemporaryDirectory(dir=variants) as tmp:
        staging=Path(tmp)/'completa';staging.mkdir()
        generated=audio_shift(source,staging/'alternativa.mp4',provenance['offset_ms'])
        (staging/'origem.json').write_text(canonical({'provenance':provenance,'sha256':generated['sha256']}),encoding='utf-8')
        try:staging.rename(destination)
        except OSError:
            if not destination.is_dir():raise
    return checked(destination)

