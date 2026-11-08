# Haybales — Pwny-CTF (script de solve)
from badgeio import badge
import framebuf # type: ignore

DISP_X = 128
DISP_Y = 64
FONT_WIDTH = 5
FONT_HEIGHT = 8
SPRITE_W = 48
SPRITE_H = 48
PADDING = 4
DEBUG = False

def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def draw_text_wrap(s, x=0, y=0):
    xdiff = DISP_X - x
    index = 0
    c = xdiff//(FONT_WIDTH + 1)
    while y < (DISP_Y - (FONT_HEIGHT)):
        badge.display.text(s[index:index+c], x, y)
        y += FONT_HEIGHT 
        index += c

def draw_text_center(s, x=DISP_X//2, y=0):
    width = len(s) * (FONT_WIDTH + 1)
    badge.display.text(s, x - width // 2, y)

def pbm_to_fbuf(fname):
    f = open(fname, 'rb')
    f.readline()
    dims = f.readline().decode('utf-8').split(' ')
    assert len(dims) == 2
    w, h = int(dims[0]), int(dims[1])
    data = bytearray(f.read())
    f.close()
    return framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)

def flip_framebuffer(fbuf):
    for y in range(SPRITE_H):
        buf = [0]*SPRITE_W
        for x in range(SPRITE_W):
            buf[x] = fbuf.pixel(x,y)
        i = 0
        for v in reversed(buf):
            fbuf.pixel(i,y,v)
            i+=1
