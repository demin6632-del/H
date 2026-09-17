from pathlib import Path
import re

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
MARK='ANDROID-TOUCH-FIX-V54'

# Удаляем накопленные обработчики старых touch-фиксов.
V39_RE=re.compile(r'/\* TOUCH-BUTTON-FIX-V39.*?\(\)\);\s*',re.S)
V42_RE=re.compile(r'/\* ANDROID-TOUCH-FIX-V42.*?\(\)\);\s*',re.S)
CLASS_RE=re.compile(r'/\* ANDROID-CLASS-SELECT-FIX-V43.*?\(\)\);\s*',re.S)
PATCH=r'''/* ANDROID-TOUCH-FIX-V54 — прямое безопасное касание кнопок Android WebView. */
(function(){
  if(window.__androidTouchFixV54)return;
  window.__androidTouchFixV54=true;
  const st=document.createElement('style');
  st.textContent='button{touch-action:manipulation!important;-webkit-tap-highlight-color:rgba(220,30,30,.16)!important;pointer-events:auto!important}.class-card:before,.class-icon{pointer-events:none!important}';
  document.head.appendChild(st);
  let lock=false;
  function activate(e){
    const b=e.target&&e.target.closest?e.target.closest('button'):null;
    if(!b||b.disabled||lock)return;
    lock=true;
    if(e.cancelable)e.preventDefault();
    if(e.stopImmediatePropagation)e.stopImmediatePropagation();
    if(e.stopPropagation)e.stopPropagation();
    b.click();
    setTimeout(function(){lock=false;},700);
  }
  document.addEventListener('touchstart',activate,{capture:true,passive:false});
  document.addEventListener('pointerdown',function(e){if(e.pointerType==='touch')activate(e);},{capture:true,passive:false});
})();
'''
for p in FILES:
    s=p.read_text(encoding='utf-8')
    s=V39_RE.sub('',s)
    s=V42_RE.sub('',s)
    s=CLASS_RE.sub('',s)
    s=s.replace('<!-- ANDROID-TOUCH-FIX-V4-FINAL: synthetic click now reaches the original button handler. -->','')
    # Кнопка «Продолжить» всегда доступна. Если сохранения нет, её обработчик
    # сам переводит игрока к выбору класса.
    s=s.replace('<button id="continueHit" class="continue-hit hidden" onclick="continueGame()">Продолжить</button>','<button id="continueHit" class="continue-hit" onclick="continueGame()">Продолжить</button>')
    anchor='</script>'
    pos=s.rfind(anchor)
    if pos<0: raise SystemExit(f'{p}: script closing tag missing')
    s=s[:pos]+'\n'+PATCH+'\n'+s[pos:]
    s += f'\n<!-- {MARK}: direct touch activation for Android buttons; Continue is always visible. -->\n'
    p.write_text(s,encoding='utf-8')
print(MARK+' applied')
