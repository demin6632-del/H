from pathlib import Path
import base64
import re

ROOT = Path(__file__).resolve().parents[1]
B64_FILE = ROOT / 'tools' / 'character_v37.webp.b64'
DATA = 'data:image/webp;base64,' + B64_FILE.read_text(encoding='ascii').strip()

CSS = '''
<style id="hero-character-v37">
.hero-figure{
  height:300px!important;
  min-height:300px!important;
  display:flex!important;
  align-items:flex-end!important;
  justify-content:center!important;
  overflow:hidden!important;
  position:relative!important;
  background:radial-gradient(circle at 50% 46%,rgba(120,0,0,.30),transparent 62%),linear-gradient(180deg,#090506,#020202)!important;
  filter:none!important;
}
.hero-character-image{
  display:block!important;
  width:auto!important;
  height:100%!important;
  max-width:100%!important;
  object-fit:contain!important;
  object-position:center bottom!important;
  filter:drop-shadow(0 0 12px rgba(190,0,0,.42))!important;
}
@media(max-width:360px){
  .hero-figure{height:260px!important;min-height:260px!important}
}
</style>
'''

for rel in ('NEW_DARK_RPG/index.html', 'android/app/src/main/assets/index.html'):
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    if 'hero-character-v37' in text:
        continue
    pattern = re.compile(r'<div class="hero-figure"[^>]*>.*?</div>', re.S)
    replacement = f'<div class="hero-figure"><img class="hero-character-image" src="{DATA}" alt="Персонаж Хроник Бездны"></div>'
    new_text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f'Не найден hero-figure в {rel}')
    marker = '</style>'
    if marker not in new_text:
        raise RuntimeError(f'Не найден конец CSS в {rel}')
    new_text = new_text.replace(marker, CSS + marker, 1)
    path.write_text(new_text, encoding='utf-8')
    print(f'Patched {rel}')
