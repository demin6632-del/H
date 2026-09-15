from pathlib import Path

FILES = [
    Path('NEW_DARK_RPG/index.html'),
    Path('android/app/src/main/assets/index.html'),
]

STYLE = r'''
<style id="hero-character-scale-v38">
/* === v3.8: увеличиваем именно видимый масштаб героя, не меняя механику === */
.hero-v34 .hero-figure{
  height:420px!important;
  min-height:420px!important;
  overflow:visible!important;
  display:flex!important;
  align-items:flex-end!important;
  justify-content:center!important;
}
.hero-v34 .hero-figure .hero-character-image{
  display:block!important;
  width:auto!important;
  height:100%!important;
  max-width:none!important;
  max-height:none!important;
  object-fit:contain!important;
  object-position:center bottom!important;
  transform:scale(1.75)!important;
  transform-origin:center bottom!important;
  flex:0 0 auto!important;
}
.hero-v34 .hero-stage{overflow:hidden!important}
@media(max-width:390px){
  .hero-v34 .hero-figure{
    height:360px!important;
    min-height:360px!important;
  }
  .hero-v34 .hero-figure .hero-character-image{
    transform:scale(1.6)!important;
  }
}
</style>
'''

for path in FILES:
    s = path.read_text(encoding='utf-8')
    marker = 'hero-character-scale-v38'
    if marker not in s:
        s = s.replace('</head>', STYLE + '\n</head>', 1)
        if marker not in s:
            s = s.replace('</body>', STYLE + '\n</body>', 1)
        path.write_text(s, encoding='utf-8')
        print('patched', path)
    else:
        print('already patched', path)
