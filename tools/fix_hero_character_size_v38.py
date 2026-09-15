from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STYLE = r'''
<style id="hero-character-scale-v38-final">
/* === v3.8 FINAL: увеличиваем видимого героя поверх всех предыдущих CSS === */
.hero-v34 .hero-figure .hero-character-image{
  display:block!important;
  width:auto!important;
  height:100%!important;
  max-width:none!important;
  max-height:none!important;
  object-fit:contain!important;
  object-position:center bottom!important;
  transform:scale(2)!important;
  transform-origin:center bottom!important;
  flex:0 0 auto!important;
}
.hero-v34 .hero-figure{overflow:visible!important}
.hero-v34 .hero-stage{overflow:hidden!important}
@media(max-width:390px){
  .hero-v34 .hero-figure .hero-character-image{transform:scale(1.8)!important}
}
</style>
'''

for rel in ('NEW_DARK_RPG/index.html', 'android/app/src/main/assets/index.html'):
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    marker = 'hero-character-scale-v38-final'
    if marker in text:
        start = text.index('<style id="hero-character-scale-v38-final">')
        end = text.index('</style>', start) + len('</style>')
        text = text[:start] + STYLE.strip() + text[end:]
    else:
        pos = text.rfind('</body>')
        if pos < 0:
            pos = len(text)
        text = text[:pos] + STYLE + '\n' + text[pos:]
    path.write_text(text, encoding='utf-8')
    print(f'Final hero scale applied to {rel}')
