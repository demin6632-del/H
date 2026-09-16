from pathlib import Path

MARK="ANDROID-TOUCH-FIX-V4"
CSS="""
<style id="android-touch-fix-v4">
/* Надёжная зона касания Android WebView: декоративные слои не перехватывают ввод. */
button, select, input, .class-card { -webkit-tap-highlight-color: transparent; touch-action: manipulation; pointer-events: auto !important; }
#classes, #classes .panel, #classes .class-grid, #classes .class-card { position: relative; z-index: 100 !important; }
#classes .class-card { cursor: pointer; }
</style>
"""
JS="""
<script id="android-touch-fix-v4">
(function(){
  if(window.__androidTouchFixV4) return;
  window.__androidTouchFixV4=true;
  let lastTouch=0,lastTarget=null;
  function activate(target){
    const btn=target && target.closest ? target.closest('button,select,input') : null;
    if(!btn || btn.disabled) return;
    const now=Date.now();
    if(btn===lastTarget && now-lastTouch<650) return;
    lastTarget=btn; lastTouch=now;
    if(typeof btn.click==='function') btn.click();
  }
  document.addEventListener('touchend',function(e){
    const t=e.changedTouches && e.changedTouches[0];
    if(!t) return;
    const target=document.elementFromPoint(t.clientX,t.clientY);
    if(target && target.closest && target.closest('button')) { e.preventDefault(); activate(target); }
  },{passive:false,capture:true});
  document.addEventListener('pointerup',function(e){
    if(e.pointerType==='touch') activate(e.target);
  },{capture:true});
})();
</script>
"""

for name in ['NEW_DARK_RPG/index.html','android/app/src/main/assets/index.html']:
    p=Path(name)
    s=p.read_text(encoding='utf-8')
    if MARK in s: continue
    s=s.replace('</head>', CSS+'\n</head>',1)
    s=s.replace('</body>', JS+'\n</body>',1)
    s=s.replace('<body>', '<body data-'+MARK.lower()+'="1">',1)
    p.write_text(s,encoding='utf-8')
print(MARK)
