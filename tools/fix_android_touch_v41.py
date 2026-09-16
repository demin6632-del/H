from pathlib import Path

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
MARK='ANDROID-TOUCH-FIX-V4-FINAL'
PATCH=r'''/* ANDROID-TOUCH-FIX-V42 — единый резервный обработчик касаний Android WebView. */
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
      if(document.documentElement.contains(b)&&!b.disabled)b.click();
    },260);
  }
  document.addEventListener('pointerup',arm,{passive:true});
  document.addEventListener('touchend',arm,{passive:true});
})();
'''
for p in FILES:
    s=p.read_text(encoding='utf-8')
    start=s.find('/* TOUCH-BUTTON-FIX-V39')
    if start>=0:
        end=s.find('})();',start)
        if end<0: raise SystemExit(f'{p}: V39 closing marker not found')
        s=s[:start]+s[end+4:]
    while True:
        start=s.find('/* ANDROID-TOUCH-FIX-V42')
        if start<0: break
        end=s.find('})();',start)
        if end<0: raise SystemExit(f'{p}: V42 closing marker not found')
        s=s[:start]+s[end+4:]
    pos=s.rfind('</script>')
    if pos<0: raise SystemExit(f'{p}: script closing tag not found')
    s=s[:pos]+'\n'+PATCH+s[pos:]
    s=s.replace('<!-- ANDROID-TOUCH-FIX-V4-FINAL: synthetic click now reaches the original button handler. -->','')
    s += f'\n<!-- {MARK}: native click is primary; pointer/touch fallback is delayed and duplicate-safe. -->\n'
    p.write_text(s,encoding='utf-8')
print(MARK)