#!/usr/bin/env python3
"""Generate the v4.6 offline media pack: procedural fantasy art + original synthesized audio."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import math, wave, struct, hashlib

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "NEW_DARK_RPG" / "assets" / "generated"
ANDROID = ROOT / "android" / "app" / "src" / "main" / "assets" / "generated"
WEB.mkdir(parents=True, exist_ok=True)
ANDROID.mkdir(parents=True, exist_ok=True)

PALETTES = [
    (18,5,7),(28,7,9),(12,9,18),(22,6,16),(8,10,16),(34,8,5),
    (16,12,7),(7,13,18),(26,5,13),(10,7,7),(31,10,8),(9,12,11)
]
SCENES = [
    "abyss_gate","blood_rift","ash_citadel","bone_catacomb","shadow_forest","void_bridge",
    "fallen_temple","red_chasm","obsidian_hall","forgotten_throne","night_marsh","iron_ruins",
    "cursed_library","black_keep","wraith_gallery","deep_lair","hell_stairs","starless_vault",
    "crimson_arena","ancient_gate","abyss_core","archon_chamber","endless_depth","rift_lord"
]

def art(name, idx):
    # 2K source art: higher native detail instead of simply stretching the old 1600px assets.
    W = H = 2048
    rng = np.random.default_rng(0xC0A54 + idx * 7919)
    low = rng.integers(0, 256, (160,160), dtype=np.uint8)
    noise = Image.fromarray(low, "L").resize((W,H), Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(2.2))
    a = np.asarray(noise, dtype=np.int16)
    fine = rng.integers(-22, 23, (H,W), dtype=np.int16)
    a = np.clip(a + fine, 0, 255).astype(np.uint8)

    p = PALETTES[idx % len(PALETTES)]
    arr = np.empty((H,W,3), dtype=np.uint8)
    for ch in range(3):
        arr[:,:,ch] = np.clip(a * (0.28 + (ch+1)*0.135) + p[ch]*0.58, 0, 255)
    img = Image.fromarray(arr, "RGB")
    d = ImageDraw.Draw(img, "RGBA")

    # Layered atmospheric depth.
    horizon = 860 + int(110*math.sin(idx*.71))
    for band in range(8):
        y0 = horizon + band*145
        alpha = max(12, 58-band*6)
        d.rectangle((0,y0,W,min(H,y0+145)), fill=(2,3,8,alpha))

    cx = 1024 + int(250*math.sin(idx))
    cy = 510 + int(110*math.cos(idx*0.7))
    for k in range(15):
        r = 75 + k*92
        d.ellipse((cx-r,cy-r,cx+r,cy+r), outline=(245,38,25,max(12,40-k)), width=6)

    # Ruined architecture with stone segmentation and perspective.
    for x in range(-140, W+220, 170):
        h = 280 + int(680*abs(math.sin(idx*.63 + x*.0105)))
        top = H-h
        d.polygon([(x,H),(x+118,H),(x+88,top),(x+30,top-82)], fill=(2,2,6,215))
        d.line((x+10,top+80,x+106,top+64), fill=(95,74,74,55), width=5)
        for yy in range(top+130,H,115):
            d.line((x+12,yy,x+108,yy-16), fill=(88,72,70,45), width=4)
        if (x//170 + idx) % 3 == 0:
            d.rectangle((x+40,top-105,x+72,top-42), fill=(235,34,22,125))
            d.rectangle((x+36,top-112,x+76,top-104), fill=(255,95,45,70))

    # Foreground floor / path gives the scenes stronger spatial depth.
    vanx = 1024 + int(90*math.sin(idx*.8))
    for k in range(12):
        yy = horizon + k*k*8 + 22*k
        if yy >= H: break
        spread = 120 + k*115
        d.line((vanx-spread,yy,vanx+spread,yy), fill=(110,80,76,max(18,58-k*3)), width=4)
    for k in range(-8,9):
        bx = vanx + k*120
        d.line((vanx,horizon,bx,H), fill=(72,58,64,38), width=5)

    # Rift / magical energy with secondary filaments.
    pts=[]
    for y in range(0,H,16):
        xx = 1024 + int(190*math.sin(y*.015+idx))
        pts.append((xx,y))
    d.line(pts, fill=(245,35,22,170), width=22)
    d.line([(x+32,y) for x,y in pts], fill=(255,100,35,82), width=9)
    for off in (-52,-30,48,74):
        d.line([(x+off,y) for x,y in pts[::2]], fill=(180,28,45,35), width=5)

    # Fine runes, embers and dust.
    for q in range(180):
        x=int(rng.integers(35,W-35)); y=int(rng.integers(35,H-35))
        r=int(rng.integers(2,18))
        alpha=int(rng.integers(16,82))
        d.ellipse((x-r,y-r,x+r,y+r), fill=(250,48,25,alpha))
    for q in range(34):
        x=int(rng.integers(100,W-100)); y=int(rng.integers(100,H-100))
        radius=int(rng.integers(25,72))
        d.regular_polygon((x,y,radius), 6, fill=(170,20,30,34), outline=(250,80,40,105), width=3)

    # Small silhouettes add readable focal points without changing gameplay.
    for q in range(2 + idx % 3):
        sx = int(280 + rng.integers(0, W-560))
        sy = int(horizon - rng.integers(20, 190))
        sh = int(rng.integers(120, 260))
        d.ellipse((sx-35,sy-sh,sx+35,sy-sh+70), fill=(1,2,5,220))
        d.polygon([(sx-48,sy-sh+55),(sx+48,sy-sh+55),(sx+78,sy+sh),(sx-78,sy+sh)], fill=(1,2,5,215))

    # Subtle vignette keeps the higher resolution from looking flat on mobile.
    vignette = Image.new("L", (W,H), 0)
    vd = ImageDraw.Draw(vignette)
    for r in range(1024, 80, -64):
        alpha = int(3 + (1024-r)/1024*22)
        vd.ellipse((1024-r,1024-r,1024+r,1024+r), outline=alpha, width=64)
    vignette = vignette.filter(ImageFilter.GaussianBlur(42))
    shade = Image.new("RGBA", (W,H), (0,0,0,0))
    shade.putalpha(vignette)
    img = Image.alpha_composite(img.convert("RGBA"), shade).convert("RGB")

    img.save(WEB / f"{name}.png", "PNG", optimize=True)
    (ANDROID / f"{name}.png").write_bytes((WEB / f"{name}.png").read_bytes())

def tone(seconds, kind, idx):
    rate=44100
    frames=int(rate*seconds)
    path=WEB / f"{kind}_{idx:02}.wav"
    phase=0.0
    freqs={"abyss":(55,82.41,110),"battle":(73.42,110,146.83),"boss":(41.2,61.74,82.41),
           "dungeon":(49,65.41,98),"victory":(196,246.94,293.66),"death":(65.41,49,36.71)}
    f1,f2,f3=freqs[kind]
    with wave.open(str(path),"wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(rate)
        block=[]
        for n in range(frames):
            t=n/rate
            beat=0.5+0.5*math.sin(2*math.pi*(0.075+idx*.006)*t)
            env=min(1.0,t/0.8,max(0.0,(seconds-t)/1.2))
            s=(0.30*math.sin(2*math.pi*f1*t)+
               0.16*math.sin(2*math.pi*f2*t+0.7*math.sin(t))+
               0.10*math.sin(2*math.pi*f3*t+0.2*idx)+
               0.07*math.sin(2*math.pi*(f1*2.01)*t)*beat)
            if kind=="battle": s += 0.06*math.sin(2*math.pi*(180+idx*7)*t*t/seconds)
            if kind=="boss": s += 0.08*math.sin(2*math.pi*31*t)*(0.5+0.5*math.sin(2*math.pi*.11*t))
            if kind=="victory": s += 0.12*math.sin(2*math.pi*(f1*(1+t/seconds))*t)
            if kind=="death": s *= max(0.05,1-t/seconds)
            v=max(-1,min(1,s*env))
            sample=int(v*26000)
            block.append(struct.pack("<hh",sample,int(sample*(0.94+0.04*math.sin(t*0.31)))))
            if len(block)>=4096:
                w.writeframes(b"".join(block)); block=[]
        if block: w.writeframes(b"".join(block))
    (ANDROID / path.name).write_bytes(path.read_bytes())

# 24 distinct in-game illustrations, not placeholder padding.
for i,name in enumerate(SCENES):
    art(name, i)

tracks=[("abyss",0,30),("abyss",1,30),("battle",0,30),("battle",1,30),
        ("boss",0,30),("dungeon",0,30),("victory",0,18),("death",0,18)]
for kind,idx,dur in tracks:
    tone(dur,kind,idx)

files=list(WEB.glob("*"))
total=sum(f.stat().st_size for f in files)
sha=hashlib.sha256()
for f in sorted(files): sha.update(f.read_bytes())
(WEB/"MEDIA_PACK_V46.txt").write_text(
    "Chronicles of the Abyss v4.6.0 media pack\n"
    f"files={len(files)-1}\nbytes={total}\nsha256={sha.hexdigest()}\n"
    "Original procedural fantasy illustrations and synthesized offline audio.\n",
    encoding="utf-8")
(ANDROID/"MEDIA_PACK_V46.txt").write_bytes((WEB/"MEDIA_PACK_V46.txt").read_bytes())
print(f"MEDIA PACK: {len(files)-1} files, {total/1024/1024:.1f} MiB")
if total < 90*1024*1024:
    raise SystemExit("Media pack is below 90 MiB; refusing to build a fake/small release.")
