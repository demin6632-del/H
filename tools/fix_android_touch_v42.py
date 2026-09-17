from pathlib import Path
import re
import subprocess

FILES=[Path('NEW_DARK_RPG/index.html'), Path('android/app/src/main/assets/index.html')]
OLD_MARKERS=['TOUCH-BUTTON-FIX-V39','ANDROID-TOUCH-FIX-V42','ANDROID-TOUCH-FIX-V54','ANDROID-CLASS-SELECT-FIX-V43']
STABLE=r'''/* ANDROID-TOUCH-STABLE-V55 — единый безопасный fallback касаний Android/WebView. */
(function(){
  if(window.__androidTouchStableV55)return;
  window.__androidTouchStableV55=true;
  const pending=new WeakMap(),lastClick=new WeakMap();
  const DELAY=140,DEDUPE=450;
  const css=document.createElement('style');
  css.textContent='button{touch-action:manipulation!important;-webkit-tap-highlight-color:rgba(220,30,30,.16)!important;pointer-events:auto!important}.class-card:before,.class-icon{pointer-events:none!important}';
  document.head.appendChild(css);
  const buttonFromTarget=t=>t&&t.closest?t.closest('button'):null;
  const cancel=b=>{const t=pending.get(b);if(t){clearTimeout(t);pending.delete(b)}};
  document.addEventListener('click',e=>{const b=buttonFromTarget(e.target);if(!b)return;cancel(b);const now=Date.now(),prev=lastClick.get(b)||0;if(now-prev<DEDUPE){e.stopImmediatePropagation();e.stopPropagation();return}lastClick.set(b,now)},true);
  function arm(e){const b=buttonFromTarget(e.target);if(!b||b.disabled)return;cancel(b);pending.set(b,setTimeout(()=>{pending.delete(b);if(document.documentElement.contains(b)&&!b.disabled){const now=Date.now(),prev=lastClick.get(b)||0;if(now-prev>=DEDUPE){lastClick.set(b,now);b.click()}}},DELAY))}
  function cancelFromTarget(e){const b=buttonFromTarget(e.target);if(b)cancel(b)}
  document.addEventListener('pointerup',arm,{passive:true});
  document.addEventListener('touchend',arm,{passive:true});
  document.addEventListener('pointercancel',cancelFromTarget,{passive:true});
  document.addEventListener('touchcancel',cancelFromTarget,{passive:true});
})();

/* GAME-STABILITY-V55 — защита от двойных действий. */
(function(){
  if(window.__gameStabilityV55)return;window.__gameStabilityV55=true;
  const wrapOnce=(name,ms)=>{const fn=window[name];if(typeof fn!=='function'||fn.__onceV55)return;let busy=false;const wrapped=function(){if(busy)return;busy=true;try{return fn.apply(this,arguments)}finally{setTimeout(()=>busy=false,ms)}};wrapped.__onceV55=true;window[name]=wrapped};
  ['start','continueGame','explore','attack','defend','skill','buyItem','buyKey','hireAlly','upgradeSkill','selectAbyssDepth','openAbyssKeyCache'].forEach(n=>wrapOnce(n,420));
})();
'''

for p in FILES:
    s=p.read_text(encoding='utf-8')
    for marker in OLD_MARKERS:
        s=re.sub(r'/\*\s*'+re.escape(marker)+r'.*?\}\)\(\);\s*','',s,flags=re.S)
    s=re.sub(r'\n<!--\s*(?:ANDROID-TOUCH-FIX|ANDROID-CLASS-SELECT-FIX)-[^>]+-->','',s)
    s=s.replace('<button id="continueHit" class="continue-hit hidden" onclick="continueGame()">Продолжить</button>', '<button id="continueHit" class="continue-hit" onclick="continueGame()">Продолжить</button>')
    if 'ANDROID-TOUCH-STABLE-V55' not in s:
        pos=s.rfind('</script>')
        if pos<0: raise SystemExit(f'{p}: script closing tag missing')
        s=s[:pos]+'\n'+STABLE+s[pos:]
    p.write_text(s,encoding='utf-8')

for p in FILES:
    s=p.read_text(encoding='utf-8')
    if s.count('ANDROID-TOUCH-STABLE-V55')!=1:
        raise SystemExit(f'{p}: stable touch handler count is invalid')
    for marker in OLD_MARKERS:
        if marker in s:
            raise SystemExit(f'{p}: obsolete touch marker remains: {marker}')
    if 'id="continueHit" class="continue-hit"' not in s:
        raise SystemExit(f'{p}: Continue button missing')
    js='\n'.join(m.group(1) for m in re.finditer(r'<script[^>]*>(.*?)</script>',s,re.S))
    Path('/tmp/game.js').write_text(js,encoding='utf-8')
    subprocess.run(['node','--check','/tmp/game.js'],check=True)
print('ANDROID TOUCH/STABILITY V55 OK')
