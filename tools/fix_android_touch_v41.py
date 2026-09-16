from pathlib import Path
import re

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
MARK='ANDROID-TOUCH-FIX-V4-FINAL'
NEW='''
<style id="android-touch-fix-v4-final">
/* Точечный фикс: старый synthetic click-перехватчик удалён, касание передаётся кнопке. */
button, select, input { touch-action: manipulation !important; pointer-events: auto !important; -webkit-tap-highlight-color: transparent !important; }
#menu:before,#menu:after,.title-wrap,.loading,.loading-text { pointer-events:none !important; }
.screen { pointer-events:auto !important; }
</style>
<script id="android-touch-fix-v4-final">
(function(){
  if(window.__androidTouchFixV4Final)return;
  window.__androidTouchFixV4Final=true;
  let lastTarget=null,lastTime=0;
  function activate(target){
    const b=target&&target.closest?target.closest('button'):null;
    if(!b||b.disabled)return;
    const now=Date.now();
    if(b===lastTarget&&now-lastTime<700)return;
    lastTarget=b;lastTime=now;
    b.click();
  }
  document.addEventListener('touchend',function(e){
    const t=e.changedTouches&&e.changedTouches[0];
    if(!t)return;
    const target=document.elementFromPoint(t.clientX,t.clientY);
    if(target&&target.closest&&target.closest('button')){
      e.preventDefault();
      activate(target);
    }
  },{passive:false,capture:true});
  document.addEventListener('pointerup',function(e){
    if(e.pointerType==='touch')activate(e.target);
  },{capture:true});
})();
</script>
'''
for p in FILES:
    s=p.read_text(encoding='utf-8')
    # Удаляем старый V39 целиком только до известного конца основного script-блока.
    start=s.find('/* TOUCH-BUTTON-FIX-V39')
    if start>=0:
        end=s.find('</script></div>',start)
        if end<0:
            raise SystemExit(f'{p}: V39 end anchor not found')
        s=s[:start]+'/* TOUCH-BUTTON-FIX-V39 — старый обработчик удалён. */\n'+s[end:]
    # Удаляем предыдущую тестовую V4-версию, если она присутствует.
    s=re.sub(r'\n<style id="android-touch-fix-v4">[\s\S]*?</script>\n','\n',s,count=1)
    if 'TOUCH-BUTTON-FIX-V39' not in s:
        s += '\n<!-- TOUCH-BUTTON-FIX-V39 — старый обработчик удалён. -->\n'
    if MARK not in s:
        css,script=NEW.split('<script',1)
        s=s.replace('</head>',css+'\n</head>',1)
        s=s.replace('</body>','<script'+script+'\n</body>',1)
        s=s.replace('<body>', '<body data-android-touch-fix="v4-final">',1)
    p.write_text(s,encoding='utf-8')
print(MARK)
