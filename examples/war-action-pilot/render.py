"""Render original schematic picture and sound for the two editing studies."""
import argparse
import math
import random
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT, FPS, SAMPLE_RATE = 864, 486, 12, 24000
FONTS = {size: ImageFont.load_default(size=size) for size in (14, 17, 20, 27)}
BOUNDS = (0, 5, 9, 14, 20, 25, 30)
WIDE = (0, 0, WIDTH, HEIGHT)
CROPS = (WIDE, (172, 87, 774, 426), (151, 142, 717, 460), WIDE, (235, 64, 864, 418), (297, 53, 864, 372))
FRAMES = {
    'Inês': ((130, 352), (248, 339), (267, 349), (330, 352), (432, 334), (599, 307), (681, 294)),
    'Mara': ((215, 310), (336, 302), (346, 339), (345, 343), (459, 336), (630, 306), (713, 296)),
    'João': ((352, 287), (463, 279), (476, 283), (476, 286), (568, 288), (703, 256), (787, 240)),
    'Eva': ((76, 324), (101, 321), (130, 329), (191, 330), (475, 310), (610, 279), (700, 264)),
}
COLORS = {'Inês': '#d3ad78', 'Mara': '#a88377', 'João': '#93a3a2', 'Eva': '#bca4bd'}
STEPS = (0.6, 1.1, 1.46, 2.08, 2.46, 3.13, 3.52, 4.19, 4.6, 12.1, 15.5, 16.1, 16.83,
         17.25, 17.95, 18.73, 19.25, 20.4, 21.35, 21.78, 22.66, 23.27, 24.11, 25.05, 25.9, 26.75)


def position(name, shot, fraction):
    start, end = FRAMES[name][shot:shot + 2]
    return tuple(round(a + (b - a) * fraction) for a, b in zip(start, end))


def silhouette(draw, name, x, y, lean, time):
    color = COLORS[name]
    head = (x + lean, y - 66)
    swing = 5 * math.sin(time * 8 + len(name))
    draw.ellipse((x - 18, y - 3, x + 18, y + 5), fill='#1e262c')
    draw.line(((x, y - 24), (x - 8 - swing, y)), fill='#151a1d', width=8)
    draw.line(((x, y - 23), (x + 9 + swing, y)), fill='#242c30', width=8)
    draw.line(((x, y - 22), (head[0], y - 52)), fill=color, width=15)
    draw.ellipse((head[0] - 7, head[1] - 6, head[0] + 7, head[1] + 8), fill='#e1c8a9')
    draw.line(((head[0] + 1, y - 47), (x + 15, y - 38)), fill=color, width=5)


def frame(source_time, output_time, shot, label):
    image = Image.new('RGB', (WIDTH, HEIGHT), '#242d34')
    draw = ImageDraw.Draw(image)
    draw.polygon([(0, 145),(864, 166),(864, 486),(0, 486)], fill='#3b4141')
    draw.polygon([(767, 213),(817, 220),(864, 486),(163, 486)], fill='#4e4b44')
    draw.polygon([(0, 152),(129, 126),(129, 299),(0, 335)], fill='#222a30')
    draw.polygon([(42, 180),(98, 166),(98, 307),(42, 323)], fill='#121b22')
    door = [(749, 143),(815, 140),(815, 242),(749, 252)]
    draw.polygon(door, fill='#171c22', outline='#a3987b', width=3)
    draw.polygon([(759, 150),(804, 148),(804, 241),(759, 246)], fill='#2c343a')
    flag = math.sin(source_time * 3) * 5
    draw.polygon([(747, 147),(782, 151+flag),(779, 171+flag),(747, 164)], fill='#c2584f')
    for index in range(10):
        x = 106+index*59
        draw.line((x, 382, x + 28, 378), fill='#4a4e47', width=2)
    fraction = (source_time-BOUNDS[shot])/(BOUNDS[shot+1]-BOUNDS[shot])
    people = {name: position(name, shot, fraction) for name in FRAMES}
    left = people['Eva'] if source_time >= 19 else people['Mara']
    right = people['João']
    a, b = (left[0]+10,left[1]-38), (right[0]+10,right[1]-38)
    draw.line((a,b),fill='#1d2124',width=14)
    draw.line((a,b),fill='#b0a28b',width=8)
    for name, (x,y) in sorted(people.items(), key=lambda pair: pair[1][1]):
        lean = 13 if name == 'Mara' and 5.5 <= source_time < 25 else 3
        silhouette(draw,name,x,y,lean,source_time)
    if 9.6 <= source_time < 25.5:
        x,y = people['Inês']
        u,v = people['Mara']
        draw.line(((x+8,y-45),(u-3,v-44)),fill=COLORS['Inês'],width=5)
    if source_time < 9.6:
        x,y = people['Inês']
        draw.rectangle((x+11,y-44,x+34,y-26),fill='#a77d57',outline='#dbb585',width=2)
    else:
        draw.rectangle((276,335,300,351),fill='#8b6449',outline='#d3a278',width=2)
        draw.line(((276,335),(268,329),(283,321)),fill='#d3a278',width=3)
    if 5.35 <= source_time < 17.2:
        dust = Image.new('RGBA', image.size)
        vapour = ImageDraw.Draw(dust)
        randomizer = random.Random(47)
        age = source_time-5.35
        for _ in range(120):
            x = randomizer.uniform(274,539) + age*randomizer.uniform(-4,13)
            y = randomizer.uniform(138,277) + min(age,9)*randomizer.uniform(0,12)
            radius = randomizer.uniform(1,15) * (1+age/18)
            vapour.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(213,193,156,max(0,round((99-age*8)*randomizer.random()))))
        image = Image.alpha_composite(image.convert('RGBA'),dust).convert('RGB')
    image = image.crop(CROPS[shot]).resize((WIDTH, HEIGHT), Image.Resampling.BICUBIC)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0,0,WIDTH,49), fill='#10161b')
    draw.rectangle((0,434,WIDTH,HEIGHT),fill='#10161b')
    draw.text((24,10),'O PANO VERMELHO',font=FONTS[27],fill='#f2e2c7')
    draw.text((WIDTH-22,16),f'VERSÃO {label}   {output_time:04.1f} s',font=FONTS[17],fill='#dbac80',anchor='ra')
    for index,(name,color) in enumerate(COLORS.items()):
        x = 25+index*93
        draw.ellipse((x,459,x+9,468),fill=color)
        draw.text((x+15,452),name,font=FONTS[17],fill='#dcd7c8')
    draw.text((WIDTH-23,452),'ANIMATIC ESQUEMÁTICO',font=FONTS[14],fill='#9ca7ac',anchor='ra')
    draw.line((24,477,24+(WIDTH-48)*output_time/30,477),fill='#b95449',width=2)
    return image


def audio():
    generator = np.random.default_rng(214)
    n = 30*SAMPLE_RATE
    raw = generator.normal(0,1,n)
    window = np.hanning(65)
    air = np.convolve(raw,window/window.sum(),mode='same') * .12
    bed = air.copy()
    def sound(when, seconds, amplitude, frequency):
        offset = round(when*SAMPLE_RATE)
        length = round(seconds*SAMPLE_RATE)
        local = np.arange(length)/SAMPLE_RATE
        envelope = np.minimum(local/.018,1)*np.exp(-local*6/seconds)
        wavelet = (np.sin(local*math.tau*frequency)*.72 + generator.normal(0,.3,length))*envelope
        bed[offset:offset+length] += amplitude*wavelet
    for beat in STEPS:
        sound(beat,.17,.14,92)
    sound(5.37,1.2,.76,54)
    sound(5.55,.7,.31,184)
    bed[round(5.92*SAMPLE_RATE):round(8.4*SAMPLE_RATE)] *= .35
    sound(9.61,.34,.45,106)
    sound(9.71,.45,.21,498)
    for beat in (10.5,11.6,13.15,17.46,19.92,21.9,24.6,27.4):
        sound(beat,.45,.13,118)
    sound(27.15,1.1,.19,57)
    return bed


def render(output, label, order, bed):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder)/'audio.wav'
        cuts = [bed[a*SAMPLE_RATE:b*SAMPLE_RATE].copy() for a,b in (BOUNDS[s:s+2] for s in order)]
        # A short ramp keeps the picture cuts from creating unrelated audio clicks.
        ramp = np.linspace(0,1,150)
        for clip in cuts:
            clip[:len(ramp)] *= ramp
            clip[-len(ramp):] *= ramp[::-1]
        with wave.open(str(path),'wb') as stream:
            stream.setparams((1,2,SAMPLE_RATE,0,'NONE','not compressed'))
            stream.writeframes((np.clip(np.concatenate(cuts),-1,1)*32767).astype('<i2').tobytes())
        arguments = ['ffmpeg','-hide_banner','-loglevel','error','-n','-f','rawvideo','-pixel_format','rgb24',
                     '-video_size',f'{WIDTH}x{HEIGHT}','-framerate',str(FPS),'-i','pipe:0','-i',str(path),
                     '-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-c:a','aac','-movflags','+faststart',str(output)]
        with subprocess.Popen(arguments,stdin=subprocess.PIPE) as process:
            tick = 0
            for shot in order:
                for index in range(BOUNDS[shot]*FPS,BOUNDS[shot+1]*FPS):
                    process.stdin.write(frame(index/FPS,tick/FPS,shot,label).tobytes())
                    tick += 1
            process.stdin.close()
            if process.wait():
                raise RuntimeError('FFmpeg could not encode the animatic')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    args = parser.parse_args()
    args.directory.mkdir(parents=True,exist_ok=True)
    bed = audio()
    render(args.directory/'O-pano-vermelho-A.mp4','A',range(6),bed)
    render(args.directory/'O-pano-vermelho-B.mp4','B',(1,0,2,3,4,5),bed)
    frame(1,1,0,'A').save(args.directory/'O-pano-vermelho-quadro.png')


if __name__ == '__main__':
    main()
