from pathlib import Path

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]
MARK='TOUCH-BUTTON-FIX-V39'
PATCH=r'''
/* TOUCH-BUTTON-FIX-V39 — совместимость касаний Android WebView. */
(function(){
  if(window.__touchButtonFixV39)return;
  window.__touchButtonFixV39=true;
  const st=document.createElement('style');
  st.id='touch-button-fix-v39-style';
  st.textContent='button{touch-action:manipulation!important;-webkit-tap-highlight-color:rgba(220,30,30,.16)!important;pointer-events:auto!important}#menu:before,#menu:after,.title-wrap,.loading,.loading-text{pointer-events:none!important}.screen{pointer-events:auto!important}';
  document.head.appendChild(st);
  let pending=null, synthetic=false;
  document.addEventListener('click',function(e){
    const b=e.target&&e.target.closest?e.target.closest('button'):null;
    if(!b)return;
    if(pending){clearTimeout(pending);pending=null;}
    if(synthetic){synthetic=false;e.stopPropagation();}
  },true);
  document.addEventListener('touchend',function(e){
    const b=e.target&&e.target.closest?e.target.closest('button'):null;
    if(!b||b.disabled)return;
    if(pending)clearTimeout(pending);
    pending=setTimeout(function(){
      pending=null;
      if(!document.documentElement.contains(b)||b.disabled)return;
      synthetic=true;
      b.click();
      setTimeout(function(){synthetic=false},450);
    },180);
  },{passive:true});
})();
'''
for p in FILES:
    s=p.read_text(encoding='utf-8')
    if MARK in s:
        continue
    anchor='</script></div>'
    if anchor not in s:
        raise SystemExit(f'{p}: script anchor not found')
    s=s.replace(anchor,'\n'+PATCH+'\n'+anchor,1)
    p.write_text(s,encoding='utf-8')
print(MARK)
