from pathlib import Path

FILES = [
    Path('NEW_DARK_RPG/index.html'),
    Path('android/app/src/main/assets/index.html'),
]

CSS = r'''
/* === FIX v3.6: мобильная ширина экрана героя === */
.hero-ref,
.hero-ref *{min-width:0}
.hero-ref{width:100%;max-width:100%;overflow:hidden}
.hero-ref .hero-stage{
  width:100%;
  max-width:100%;
  grid-template-columns:minmax(0,1fr) minmax(86px,.78fr) minmax(0,1fr);
  overflow:hidden;
}
.hero-ref .hero-equip-side{min-width:0;overflow:hidden}
.hero-ref .hero-equip-card{
  min-width:0;
  width:100%;
  max-width:100%;
  overflow:hidden;
}
.hero-ref .hero-equip-card b,
.hero-ref .hero-equip-card small{
  min-width:0;
  max-width:100%;
  overflow:hidden;
  text-overflow:ellipsis;
}
.hero-ref .hero-equip-card button{
  width:100%;
  max-width:100%;
  min-width:0;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
}
.hero-ref .hero-figure{min-width:0;width:100%;overflow:visible}
.hero-ref .hero-art-svg{min-width:0;max-width:100%}
.hero-ref .hero-progress,
.hero-ref .hero-progress .info-card,
.hero-ref .hero-stats-box,
.hero-ref .hero-stats-box>div{min-width:0;max-width:100%}
.hero-ref .hero-stat{min-width:0;max-width:100%}
.hero-ref .hero-stat .val{min-width:0;max-width:100%;overflow:hidden;text-overflow:ellipsis}
@media(max-width:700px){
  .hero-ref .hero-stage{
    grid-template-columns:minmax(0,1fr) minmax(74px,.72fr) minmax(0,1fr);
    gap:4px;
    overflow:hidden;
  }
  .hero-ref .hero-equip-card{padding:6px 5px}
  .hero-ref .hero-equip-card button{padding-left:4px;padding-right:4px}
}
@media(max-width:390px){
  .hero-ref .hero-stage{grid-template-columns:minmax(0,1fr) minmax(62px,.62fr) minmax(0,1fr);gap:3px}
}
'''

for path in FILES:
    s = path.read_text(encoding='utf-8')
    marker = '/* === FIX v3.6: мобильная ширина экрана героя === */'
    if marker not in s:
        s = s.replace('</style>', CSS + '\n</style>', 1)
        path.write_text(s, encoding='utf-8')
        print('patched', path)
    else:
        print('already patched', path)
