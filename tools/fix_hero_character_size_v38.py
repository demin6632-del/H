from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STYLE = r'''
<style id="hero-character-scale-v40-final">
/* === v3.10 FINAL: увеличиваем именно фактически отображаемый PNG/WebP/SVG героя === */
.hero-v34 .hero-figure .hero-character-image,
.hero-v34 .hero-figure .hero-art-svg{
  display:block!important;
  width:auto!important;
  height:100%!important;
  max-width:none!important;
  max-height:none!important;
  object-fit:contain!important;
  object-position:center bottom!important;
  transform:scale(2.15)!important;
  transform-origin:center bottom!important;
  flex:0 0 auto!important;
}
.hero-v34 .hero-figure{overflow:visible!important}
.hero-v34 .hero-stage{overflow:visible!important}
@media(max-width:390px){
  .hero-v34 .hero-figure .hero-character-image,
  .hero-v34 .hero-figure .hero-art-svg{
    transform:scale(1.9)!important;
  }
}
</style>
'''

for rel in ('NEW_DARK_RPG/index.html', 'android/app/src/main/assets/index.html'):
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    markers = (
        'hero-character-scale-v38-final',
        'hero-character-scale-v39-final',
        'hero-character-scale-v40-final',
    )
    if any(marker in text for marker in markers):
        start = text.index('<style id="hero-character-scale-')
        end = text.index('</style>', start) + len('</style>')
        text = text[:start] + STYLE.strip() + text[end:]
    else:
        pos = text.rfind('</body>')
        if pos < 0:
            pos = len(text)
        text = text[:pos] + STYLE + '\n' + text[pos:]
    path.write_text(text, encoding='utf-8')
    print(f'Final hero scale applied to {rel}')
