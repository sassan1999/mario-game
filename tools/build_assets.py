"""Generate all original non-player art for COMET ZIP from Pillow primitives."""
from pathlib import Path
import math, wave, struct, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from palette import *
from shapes import canvas, rrect, ellipse, save

ROOT = Path('/home/user/work/game/assets/images')
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
random.seed(42)

def sc(c): return tuple(c)+(255,)
def make(sz, color=(0,0,0,0)): return Image.new('RGBA', sz, color)
def outline(im, col=(7,18,42), px=2):
    a=im.getchannel('A').filter(ImageFilter.MaxFilter(px*2+1))
    ring=Image.new('RGBA',im.size,sc(col)); ring.putalpha(a)
    ring.alpha_composite(im); return ring

def text_center(im, text, y, size, fill, stroke=(0,0,0), sw=2):
    d=ImageDraw.Draw(im); f=ImageFont.truetype(FONT,size)
    box=d.textbbox((0,0),text,font=f,stroke_width=sw); x=(im.width-(box[2]-box[0]))//2
    d.text((x,y),text,font=f,fill=sc(fill),stroke_width=sw,stroke_fill=sc(stroke))

def draw_coin(i):
    im=make((48,48)); d=ImageDraw.Draw(im); cx=24; sy=2+int(math.sin(i/6*math.pi)*3); w=[25,20,12,20,25,20][i]
    d.ellipse((cx-w//2,sy,cx+w//2,46),fill=sc(COIN['gold_low']),outline=sc(COIN['outline']),width=3)
    d.ellipse((cx-w//2+3,sy+2,cx+w//2-3,43),fill=sc(COIN['gold']))
    d.line((cx,sy+6,cx,40),fill=sc(COIN['gold_hi']),width=3)
    d.polygon([(cx,12),(cx+4,19),(cx+11,19),(cx+5,24),(cx+7,32),(cx,27),(cx-7,32),(cx-5,24),(cx-11,19),(cx-4,19)],fill=sc(COIN['star']))
    return outline(im,COIN['outline'],1)

def draw_mushroom(i):
    im=make((52,52)); d=ImageDraw.Draw(im); bob=int(math.sin(i/4*math.pi)*2)
    d.ellipse((4,4+bob,48,35+bob),fill=sc(MUSHROOM['cap_low']),outline=sc(MUSHROOM['outline']),width=3)
    d.ellipse((7,3+bob,45,30+bob),fill=sc(MUSHROOM['cap']))
    d.ellipse((13,6+bob,23,17+bob),fill=sc(MUSHROOM['spot'])); d.ellipse((31,8+bob,40,18+bob),fill=sc(MUSHROOM['spot']))
    d.rounded_rectangle((15,26+bob,39,47),radius=7,fill=sc(MUSHROOM['stem']),outline=sc(MUSHROOM['outline']),width=3)
    d.ellipse((19,30+bob,25,37+bob),fill=sc(MUSHROOM['power']))
    return im

def draw_enemy(kind, i):
    p=ENEMIES[kind]; im=make((64,64)); d=ImageDraw.Draw(im); bob=int(math.sin(i/4*math.pi)*2)
    if kind=='grubbo':
        d.ellipse((8,24+bob,56,57),fill=sc(p['dark']),outline=sc(p['outline']),width=3)
        d.ellipse((10,18+bob,54,51),fill=sc(p['body']))
        d.ellipse((16,25+bob,30,38+bob),fill=sc(p['hi'])); d.ellipse((34,25+bob,48,38+bob),fill=sc(p['hi']))
        for x in (20,40): d.ellipse((x,25+bob,x+7,34+bob),fill=sc(p['eye'])); d.ellipse((x+3,28+bob,x+6,33+bob),fill=sc(p['pupil']))
        d.line((22,45+bob,42,45+bob),fill=sc(p['outline']),width=3)
    elif kind=='zippbat':
        d.polygon([(32,31+bob),(3,13+bob),(11,43+bob),(26,37+bob)],fill=sc(p['wing']),outline=sc(p['outline']))
        d.polygon([(32,31+bob),(61,13+bob),(53,43+bob),(38,37+bob)],fill=sc(p['wing']),outline=sc(p['outline']))
        d.ellipse((18,17+bob,46,51+bob),fill=sc(p['body']),outline=sc(p['outline']),width=3)
        d.ellipse((24,25+bob,32,34+bob),fill=sc(p['eye'])); d.ellipse((36,25+bob,44,34+bob),fill=sc(p['eye']))
        d.ellipse((27,28+bob,31,34+bob),fill=sc(p['pupil'])); d.ellipse((39,28+bob,43,34+bob),fill=sc(p['pupil']))
    elif kind=='bouncer':
        d.ellipse((8,28+bob,56,58),fill=sc(p['dark']),outline=sc(p['outline']),width=3)
        d.ellipse((13,20+bob,51,52),fill=sc(p['body']))
        d.ellipse((21,26+bob,31,37+bob),fill=sc(p['eye'])); d.ellipse((35,26+bob,45,37+bob),fill=sc(p['eye']))
        d.ellipse((25,30+bob,30,36+bob),fill=sc(p['pupil'])); d.ellipse((39,30+bob,44,36+bob),fill=sc(p['pupil']))
        d.arc((22,33+bob,42,47+bob),0,180,fill=sc(p['outline']),width=3)
    elif kind=='spitter':
        d.ellipse((10,17+bob,54,55),fill=sc(p['dark']),outline=sc(p['outline']),width=3)
        d.ellipse((14,13+bob,50,49),fill=sc(p['body']))
        d.ellipse((20,20+bob,30,31+bob),fill=sc(p['eye'])); d.ellipse((36,20+bob,46,31+bob),fill=sc(p['eye']))
        d.ellipse((24,23+bob,29,30+bob),fill=sc(p['pupil'])); d.ellipse((40,23+bob,45,30+bob),fill=sc(p['pupil']))
        d.ellipse((25,37+bob,43,47+bob),fill=sc(p['spore']))
    else:
        d.polygon([(7,45+bob),(13,21+bob),(50,18+bob),(58,45+bob)],fill=sc(p['dark']),outline=sc(p['outline']))
        d.rounded_rectangle((11,14+bob,53,48+bob),radius=12,fill=sc(p['body']),outline=sc(p['outline']),width=3)
        d.polygon([(17,17+bob),(26,4+bob),(31,17+bob),(39,4+bob),(45,18+bob)],fill=sc(p['horn']),outline=sc(p['outline']))
        d.ellipse((34,25+bob,45,36+bob),fill=sc(p['eye'])); d.ellipse((39,28+bob,44,34+bob),fill=sc(p['pupil']))
    return im

def draw_bolt(kind='bolt',i=0):
    im=make((42,26)); d=ImageDraw.Draw(im)
    if kind=='bolt':
        d.polygon([(4,13),(19,4),(16,11),(35,7),(22,18),(25,12),(8,22)],fill=sc((121,247,255)),outline=sc((8,48,77)))
        d.ellipse((2,8,8,14),fill=sc((220,255,255)))
    else:
        d.ellipse((8,6,24,22),fill=sc((188,245,101)),outline=sc((36,82,35)),width=2)
        d.ellipse((27,9,37,19),fill=sc((132,214,74)),outline=sc((36,82,35)),width=2)
    return im

def draw_checkpoint(on=False,i=0):
    im=make((70,110)); d=ImageDraw.Draw(im); col=(92,255,184) if on else (139,160,190)
    d.rectangle((31,8,37,100),fill=sc((47,58,84)),outline=sc((8,18,42)),width=2)
    d.polygon([(36,11),(61,22),(36,34)],fill=sc(col),outline=sc((8,18,42)))
    d.ellipse((26,96,44,106),fill=sc((41,52,76)),outline=sc((8,18,42)))
    if on: d.ellipse((22,2,46,26),outline=sc((92,255,184)),width=3)
    return im

def draw_goal(i):
    im=make((90,130)); d=ImageDraw.Draw(im)
    d.rectangle((42,15,49,120),fill=sc((40,42,87)),outline=sc((8,18,42)),width=2)
    pts=[]
    for k in range(10):
        a=k/10*math.tau+i*.15; r=38 if k%2==0 else 16
        pts.append((45+math.cos(a)*r,36+math.sin(a)*r))
    d.polygon(pts,fill=sc((103,236,255)),outline=sc((8,18,42)))
    d.ellipse((22,13,68,59),outline=sc((214,255,255)),width=3)
    d.ellipse((34,25,56,47),fill=sc((34,20,83)))
    return im

def draw_tile(name):
    p=TILES[name]; im=make((32,32)); d=ImageDraw.Draw(im)
    d.rectangle((0,0,31,31),fill=sc(p['body']),outline=sc(p['outline']),width=2)
    if name=='grass':
        d.rectangle((1,1,30,9),fill=sc(p['top'])); d.line((2,8,30,8),fill=sc(p['top_hi']),width=2)
        for x,y in ((6,18),(20,15),(26,26),(13,28)): d.ellipse((x,y,x+3,y+3),fill=sc(p['pebble']))
    elif name in ('bonus','breakable','used'):
        d.rectangle((4,4,27,27),outline=sc(p['top_hi']),width=2); text_center(im,'?',3,18,p['top_hi'],p['outline'],1)
    elif name=='platform':
        d.rectangle((0,3,31,12),fill=sc(p['top'])); d.rectangle((4,13,27,28),fill=sc(p['body_dark']))
        d.line((5,14,26,14),fill=sc(p['top_hi']),width=2)
    elif name=='spikes':
        d.rectangle((0,23,31,31),fill=sc(p['body_dark']))
        for x in range(-4,36,10): d.polygon([(x,24),(x+6,4),(x+14,24)],fill=sc(p['body']),outline=sc(p['outline']))
    elif name=='goo':
        d.rectangle((0,10,31,31),fill=sc(p['body_dark']));
        for x in (2,13,24): d.ellipse((x,2+(x%3)*3,x+12,16+(x%3)*3),fill=sc(p['top']))
    else:
        for x,y in ((4,14),(17,7),(24,24),(9,26)): d.ellipse((x,y,x+4,y+4),fill=sc(p['pebble']))
        d.line((0,8,31,5),fill=sc(p['top_hi']),width=2)
    return im

def draw_control(label, active=False):
    im=make((190,128)); d=ImageDraw.Draw(im); base=UI['accent_dark'] if active else UI['panel']
    d.rounded_rectangle((5,5,185,123),radius=28,fill=sc(base),outline=sc(UI['accent']),width=4)
    f=ImageFont.truetype(FONT,42 if len(label)>2 else 64); bb=d.textbbox((0,0),label,font=f); x=(190-(bb[2]-bb[0]))//2
    d.text((x,34),label,font=f,fill=sc(UI['text']),stroke_width=2,stroke_fill=sc(UI['outline']))
    return im

def draw_background(theme,w=960,h=540):
    t=THEMES[theme]; im=make((w,h)); d=ImageDraw.Draw(im)
    for y in range(h):
        k=y/max(1,h-1); col=tuple(int(t['sky_top'][j]*(1-k)+t['sky_low'][j]*k) for j in range(3)); d.line((0,y,w,y),fill=sc(col))
    # clouds / stars
    if theme=='meadow':
        d.ellipse((w*.10,h*.12,w*.30,h*.27),fill=sc(t['cloud'])); d.ellipse((w*.22,h*.08,w*.45,h*.28),fill=sc(t['cloud'])); d.ellipse((w*.36,h*.15,w*.54,h*.28),fill=sc(t['cloud']))
        d.ellipse((w*.68,h*.13,w*.82,h*.24),fill=sc(t['cloud']))
    else:
        for _ in range(55):
            x=random.randrange(w); y=random.randrange(int(h*.65)); r=random.choice([1,1,2]); d.ellipse((x,y,x+r,y+r),fill=sc(t['cloud']))
    # far and near polygon hills / skyline
    far=[]; near=[]
    for x in range(-50,w+100,100): far.append((x,h*.62-random.randint(20,90)))
    far += [(w+20,h),(0,h)]
    d.polygon(far,fill=sc(t['far']))
    if theme=='city':
        for x in range(0,w,75):
            hh=random.randint(50,170); d.rectangle((x,h*.75-hh,x+55,h*.75),fill=sc(t['near']))
            for wy in range(int(h*.75-hh+10),int(h*.75-8),25): d.rectangle((x+12,wy,x+19,wy+5),fill=sc(t['near_hi']))
    else:
        for x in range(-50,w+100,130): near.append((x,h*.78-random.randint(40,130)))
        near += [(w+20,h),(0,h)]; d.polygon(near,fill=sc(t['near']))
    return im

def write_wav(path, freq, seconds=.12, volume=.22):
    rate=22050; n=int(rate*seconds); frames=[]
    for i in range(n):
        env=min(1,i/(rate*.01), (n-i)/(rate*.04)); val=int(32767*volume*env*math.sin(2*math.pi*freq*i/rate)); frames.append(struct.pack('<h',val))
    with wave.open(str(path),'wb') as w: w.setparams((1,2,rate,n,'NONE','not compressed')); w.writeframes(b''.join(frames))

def main():
    for folder in ('enemies','collectibles','environments','ui'):
        (ROOT/folder).mkdir(parents=True,exist_ok=True)
    for i in range(6): save(draw_coin(i),ROOT/'collectibles'/f'coin_spin_{i}.png')
    for i in range(4): save(draw_mushroom(i),ROOT/'collectibles'/f'mushroom_idle_{i}.png')
    for kind in ENEMIES:
        for i in range(4): save(draw_enemy(kind,i),ROOT/'enemies'/f'{kind}_walk_{i}.png')
    for i in range(2): save(draw_bolt('bolt',i),ROOT/'collectibles'/f'bolt_fly_{i}.png'); save(draw_bolt('spore',i),ROOT/'collectibles'/f'spore_fly_{i}.png')
    for i in range(2): save(draw_checkpoint(True,i),ROOT/'ui'/f'checkpoint_on_{i}.png')
    save(draw_checkpoint(False),ROOT/'ui/checkpoint_off.png');
    for i in range(4): save(draw_goal(i),ROOT/'ui'/f'goal_idle_{i}.png')
    for n in TILES: save(draw_tile(n),ROOT/'environments'/f'tile_{n}.png')
    NAMES={'←':'left','→':'right','JUMP':'jump','ATTACK':'attack','Ⅱ':'pause'}
    for label,slug in NAMES.items():
        for active in (False,True):
            save(draw_control(label,active),ROOT/'ui'/(f'control_{slug}_'+('on' if active else 'off')+'.png'))
        save(draw_control(label,False),ROOT/'ui'/f'control_{slug}.png')
    for theme in THEMES: save(draw_background(theme),ROOT/'environments'/f'background_{theme}.png')
    ad=Path('/home/user/work/game/assets/audio'); ad.mkdir(parents=True,exist_ok=True)
    tones={'jump':660,'coin':990,'stomp':190,'shoot':780,'hurt':120,'powerup':520,'block_break':260,'block_bonus':860,'checkpoint':740,'goal':1040,'game_over':110,'select':600,'land':230,'dash':430}
    for name,freq in tones.items(): write_wav(ad/f'{name}.wav',freq,.10 if name not in ('goal','powerup') else .28)
    print('generated original sprite, background and sound assets')
if __name__=='__main__': main()
