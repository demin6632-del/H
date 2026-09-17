from pathlib import Path
import re

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
MARK='ANDROID-TOUCH-FIX-V44-NATIVE-CLASS'

# Удаляем накопленные обработчики V39/V42/V43. Выбор класса теперь выполняется
# единственным нативным мостом MainActivity V51, а обычные кнопки — штатным click
# с безопасным резервом pointerup/touchend.
V39_RE=re.compile(r'/\* TOUCH-BUTTON-FIX-V39.*?\(\)\);\s*',re.S)
V42_RE=re.compile(r'/\* ANDROID-TOUCH-FIX-V42.*?\(\)\);\s*',re.S)
CLASS_RE=re.compile(r'/\* ANDROID-CLASS-SELECT-FIX-V43.*?\(\)\);\s*',re.S)
PATCH=r'''/* ANDROID-TOUCH-FIX-V42 — единый резервный обработчик касаний. */
(function(){
  if(window.__androidTouchFixV42)return;
  window.__androidTouchFixV42=true;
  const st=document.createElement('style');
  st.textContent='button{touch-action:manipulation!important;-webkit-tap-highlight-color:rgba(220,30,30,.16)!important;pointer-events:auto!important}.class-card:before,.class-icon{pointer-events:none!important}';
  document.head.appendChild(st);
  let pending=null;
  document.addEventListener('click',function(){if(pending){clearTimeout(pending);pending=null;}},true);
  function arm(e){
    const b=e.target&&e.target.closest?e.target.closest('button'):null;
    if(!b||b.disabled)return;
    if(pending)clearTimeout(pending);
    pending=setTimeout(function(){
      pending=null;
      if(!document.documentElement.contains(b)||b.disabled)return;
      b.click();
    },260);
  }
  document.addEventListener('pointerup',arm,{passive:true});
  document.addEventListener('touchend',arm,{passive:true});
})();
'''
for p in FILES:
    s=p.read_text(encoding='utf-8')
    s=V39_RE.sub('',s)
    s=V42_RE.sub('',s)
    s=CLASS_RE.sub('',s)
    s=s.replace('<!-- ANDROID-TOUCH-FIX-V4-FINAL: synthetic click now reaches the original button handler. -->','')
    anchor='</script>'
    pos=s.rfind(anchor)
    if pos<0: raise SystemExit(f'{p}: script closing tag missing')
    s=s[:pos]+'\n'+PATCH+'\n'+s[pos:]
    s += f'\n<!-- {MARK}: native class bridge is primary; ordinary buttons keep duplicate-safe touch fallback. -->\n'
    p.write_text(s,encoding='utf-8')
print(MARK)
