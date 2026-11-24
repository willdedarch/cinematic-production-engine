"""Draw the three focal beats as a camera-locked technical blocking study."""
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT, FPS = 1280, 720, 24
TITLES = (
    'O passadiço sai do alto. Iara perde apoio.',
    'O suporte cruza o quadro. Abel termina no piso.',
    'Daro desloca Iara. O piso cede no ponto deixado.',
)


def font(size):
    for name in ('DejaVuSans.ttf', 'arial.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


TITLE_FONT = font(34)
LABEL_FONT = font(20)
BODY_FONT = font(27)
NAME_OFFSETS = {'IARA': (-66, -30), 'ABEL': (22, -45), 'DARO': (24, -24)}


def motion(time, start, end):
    progress = max(0, min(1, (time - start) / (end - start)))
    return progress * progress * (3 - 2 * progress)


def figure(draw, x, y, color, name, fallen=0, *, tape=False, injury=False):
    x, y = round(x), round(y)
    shoulders = (round(x + 48 * fallen), round(y - 71 + 62 * fallen))
    hips = (round(x + 20 * fallen), round(y - 34 + 28 * fallen))
    head_center = (round(x + 62 * fallen), round(y - 91 + 75 * fallen))
    draw.line((hips, shoulders), fill=color, width=24)
    draw.line((hips, (x - 12, y), (x + 22, y)), fill=color, width=12)
    hx, hy = head_center
    draw.ellipse((hx - 13, hy - 13, hx + 13, hy + 13), fill=color)
    if tape:
        draw.rectangle((shoulders[0] + 13, shoulders[1] + 16, shoulders[0] + 25, shoulders[1] + 28),
                       fill='#fdf8e3')
    if injury:
        draw.rectangle((shoulders[0] + 10, shoulders[1] + 6, shoulders[0] + 16, shoulders[1] + 21),
                       fill='#a0233c')
    dx, dy = NAME_OFFSETS[name]
    draw.text((hx + dx, hy + dy), name, font=LABEL_FONT, fill='#f3eddd')


def frame(time):
    image = Image.new('RGB', (WIDTH, HEIGHT), '#15212a')
    draw = ImageDraw.Draw(image)
    draw.rectangle((32, 110, 1248, 587), fill='#32404a')
    draw.polygon(((135, 159), (1050, 159), (1120, 389), (233, 414)), fill='#62717c')
    draw.polygon(((915, 159), (1050, 159), (1120, 389), (942, 414)), fill='#a3bbc6')
    draw.polygon(((32, 563), (233, 414), (1120, 389), (1248, 540), (1248, 587), (32, 587)), fill='#4d5c68')
    for x in (270, 540, 908):
        draw.line((x - 112, 587, x, 410), fill='#64737c', width=2)

    collapse = motion(time, 1.7, 3.5)
    if collapse < 1:
        y = round(242 + 284 * collapse)
        draw.polygon(((555, y), (1010, y - 11), (1005, y + 19), (550, y + 29)), fill='#d4a76d')
        draw.text((557, y - 31), 'PASSADIÇO', font=LABEL_FONT, fill='#fff0d6')
    if 1.7 <= time < 1.9:
        draw.polygon(((915, 159), (1050, 159), (1120, 389), (942, 414)), fill='#fde9bc')
    into_dust = motion(time, 2.1, 3.9)
    for i in range(12):
        x = round(943 - into_dust * (28 + i * 24))
        y = round(324 + (i % 4) * 26 + into_dust * (i % 3) * 11)
        draw.ellipse((x, y, x + 5 + i % 3, y + 5 + i % 3), fill='#c7bbc0')

    floor_drop = motion(time, 10.35, 11.55)
    if floor_drop > 0:
        floor_lip = round(518 + 43 * floor_drop)
        draw.polygon(((456, 515), (591, 512), (643, floor_lip), (417, floor_lip + 14)), fill='#18222d')
        draw.line((456, 515, 591, 512), fill='#d4a76d', width=3)

    tilt = round(15 * collapse)
    draw.polygon(((599, 431 + tilt), (707, 431), (707, 519), (599, 532)), fill='#192934')
    draw.line((610, 422 + tilt, 623, 401, 644, 398), fill='#e3d4b4', width=5)
    support = motion(time, 4.45, 6.2)
    support_x, support_y = round(880 - support * 107), round(266 + support * 167)
    if time >= 4.3:
        draw.line((support_x, support_y, support_x - 49, support_y + 53), fill='#dfaa72', width=11)

    abel_down = motion(time, 5.75, 6.8)
    figure(draw, 645 + 22 * abel_down, 448 + 21 * abel_down, '#a5c28e', 'ABEL', abel_down)
    enter = motion(time, 8, 9.45)
    pull = motion(time, 9.45, 10.75)
    iara_down = motion(time, 1.9, 3.4) * (1 - 0.28 * pull)
    iara_x, daro_x = 522 + 151 * pull, 883 - 178 * enter + 32 * pull
    figure(draw, iara_x, 518 + 19 * iara_down, '#d68d5f', 'IARA', iara_down * 0.51, tape=True)
    figure(draw, daro_x, 533, '#8ca7ca', 'DARO', enter * 0.2, injury=True)
    if 9.45 <= time <= 10.75:
        draw.line((round(daro_x), 470, round(iara_x + 45), 478), fill='#8ca7ca', width=12)

    beat = min(int(time // 4), 2)
    draw.text((32, 23), 'A última frequência', font=TITLE_FONT, fill='#f3eddd')
    draw.text((34, 68), 'SA08 · PREVIS ESQUEMÁTICO · SEM ATUAÇÃO REALIZADA', font=LABEL_FONT, fill='#a3bbc6')
    draw.text((34, 607), TITLES[beat], font=BODY_FONT, fill='#f3eddd')
    draw.text((1090, 613), f'{time:05.2f} / 12 s', font=LABEL_FONT, fill='#d4a76d')
    draw.rectangle((34, 671, 1246, 681), fill='#394750')
    draw.rectangle((34, 671, 34 + round(1212 * time / 12), 681), fill='#d4a76d')
    for position in (438, 842):
        draw.line((position, 666, position, 687), fill='#ede3c8', width=2)
    return image
