from pathlib import Path
import re, subprocess

FILES=[Path('NEW_DARK_RPG/index.html'), Path('android/app/src/main/assets/index.html')]

def replace_once(s, old, new, label):
    if old not in s:
        raise SystemExit(f'{label}: target block not found')
    return s.replace(old, new, 1)

STABLE_TOUCH=r'''/* ANDROID-TOUCH-STABLE-V55 — единый безопасный fallback касаний Android/WebView. */
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
  document.addEventListener('pointerup',arm,{passive:true});document.addEventListener('touchend',arm,{passive:true});
  document.addEventListener('pointercancel',cancelFromTarget,{passive:true});document.addEventListener('touchcancel',cancelFromTarget,{passive:true});
})();

/* GAME-STABILITY-V55 — защита от двойных действий. */
(function(){
  if(window.__gameStabilityV55)return;window.__gameStabilityV55=true;
  const wrapOnce=(name,ms)=>{const fn=window[name];if(typeof fn!=='function'||fn.__onceV55)return;let busy=false;const wrapped=function(){if(busy)return;busy=true;try{return fn.apply(this,arguments)}finally{setTimeout(()=>busy=false,ms)}};wrapped.__onceV55=true;window[name]=wrapped};
  ['start','continueGame','explore','attack','defend','skill','buyItem','buyKey','hireAlly','upgradeSkill','selectAbyssDepth','openAbyssKeyCache'].forEach(n=>wrapOnce(n,420));
})();

/* GAME-ERROR-GUARD-V55 — записываем неожиданные runtime-ошибки в журнал. */
(function(){
  if(window.__gameErrorGuardV55)return;window.__gameErrorGuardV55=true;
  window.addEventListener('error',e=>{try{if(typeof logEvent==='function')logEvent('СИСТЕМА','Ошибка интерфейса: '+String(e&&e.message||'неизвестная ошибка').slice(0,180))}catch(_){}});
  window.addEventListener('unhandledrejection',e=>{try{if(typeof logEvent==='function')logEvent('СИСТЕМА','Ошибка операции: '+String(e&&e.reason||'неизвестная ошибка').slice(0,180))}catch(_){}});
})();
'''

NORMALIZE_OLD="""function normalizeHero(){if(!hero||typeof hero!=='object')return false;const s=classStats[hero.class];if(!s)return false;hero.items=Array.isArray(hero.items)?hero.items:[];hero.gold=Math.max(0,Number(hero.gold??localStorage.getItem('abyss_gold')??100));hero.allies=Array.isArray(hero.allies)?hero.allies:[];hero.crit=Math.max(0,Math.min(1,Number(hero.crit||0)));hero.skillLevel=Math.max(1,Math.min(5,Number(hero.skillLevel||1)));hero.skillPoints=Math.max(0,Number(hero.skillPoints||0));hero.weapon=hero.weapon||'Нет';hero.armor=hero.armor||'Нет';hero.level=Math.max(1,Number(hero.level||1));hero.xp=Math.max(0,Number(hero.xp||0));hero.maxHp=Math.max(Number(hero.maxHp||s.maxHp),1);hero.maxEnergy=Math.max(Number(hero.maxEnergy||s.maxEnergy),1);hero.hp=Math.min(Math.max(Number(hero.hp??hero.maxHp),0),hero.maxHp);hero.energy=Math.min(Math.max(Number(hero.energy??hero.maxEnergy),0),hero.maxEnergy);hero.attack=Math.max(1,Number(hero.attack||s.attack));hero.def=Math.max(0,Number(hero.def||s.def));return true}
function loadGame(){try{const raw=localStorage.getItem(saveKey);if(!raw)return false;const data=JSON.parse(raw);if(data&&data.hero){hero=data.hero;abyssFloor=Number(data.abyssFloor||1);abyssRoom=Number(data.abyssRoom||0);abyssBossDefeated=!!data.abyssBossDefeated;abyssRoomContent=String(data.abyssRoomContent||'Новая комната ещё не исследована.');journalEntries=Array.isArray(data.journal)?data.journal:[];allies=Array.isArray(data.allies)?data.allies:(Array.isArray(hero.allies)?hero.allies:[])}else{hero=data;resetAbyss()}if(!normalizeHero())return false;hero.allies=allies;localStorage.setItem('abyss_gold',String(hero.gold));return true}catch(e){return false}}
"""
NORMALIZE_NEW="""function finiteNumber(value,fallback){const n=Number(value);return Number.isFinite(n)?n:fallback}
function normalizeHero(){if(!hero||typeof hero!=='object')return false;const s=classStats[hero.class];if(!s)return false;hero.items=Array.isArray(hero.items)?hero.items:[];let storedGold=100;try{storedGold=finiteNumber(localStorage.getItem('abyss_gold'),100)}catch(e){}hero.gold=Math.max(0,finiteNumber(hero.gold,storedGold));hero.allies=Array.isArray(hero.allies)?hero.allies:[];hero.crit=Math.max(0,Math.min(1,finiteNumber(hero.crit,0)));hero.skillLevel=Math.max(1,Math.min(5,finiteNumber(hero.skillLevel,1)));hero.skillPoints=Math.max(0,finiteNumber(hero.skillPoints,0));hero.weapon=typeof hero.weapon==='string'&&hero.weapon?hero.weapon:'Нет';hero.armor=typeof hero.armor==='string'&&hero.armor?hero.armor:'Нет';hero.level=Math.max(1,Math.floor(finiteNumber(hero.level,1)));hero.xp=Math.max(0,finiteNumber(hero.xp,0));hero.maxHp=Math.max(finiteNumber(hero.maxHp,s.maxHp),1);hero.maxEnergy=Math.max(finiteNumber(hero.maxEnergy,s.maxEnergy),1);hero.hp=Math.min(Math.max(finiteNumber(hero.hp,hero.maxHp),0),hero.maxHp);hero.energy=Math.min(Math.max(finiteNumber(hero.energy,hero.maxEnergy),0),hero.maxEnergy);hero.attack=Math.max(1,finiteNumber(hero.attack,s.attack));hero.def=Math.max(0,finiteNumber(hero.def,s.def));return true}
function loadGame(){try{let raw=localStorage.getItem(saveKey);if(!raw)raw=localStorage.getItem(saveKey+'_backup');if(!raw)return false;const data=JSON.parse(raw);if(data&&data.hero){hero=data.hero;abyssFloor=Math.max(1,Math.floor(finiteNumber(data.abyssFloor,1)));abyssRoom=Math.max(0,Math.floor(finiteNumber(data.abyssRoom,0)));abyssBossDefeated=!!data.abyssBossDefeated;abyssRoomContent=String(data.abyssRoomContent||'Новая комната ещё не исследована.');journalEntries=Array.isArray(data.journal)?data.journal:[];allies=Array.isArray(data.allies)?data.allies:(Array.isArray(hero.allies)?hero.allies:[])}else{hero=data;resetAbyss()}if(!normalizeHero())return false;hero.allies=allies;try{localStorage.setItem('abyss_gold',String(hero.gold))}catch(e){}return true}catch(e){return false}}
"""
SAVE_OLD="function save(){localStorage.setItem(saveKey,JSON.stringify({version:SAVE_VERSION,hero,abyssFloor,abyssRoom,abyssBossDefeated,allies,journal:journalEntries}));localStorage.setItem('abyss_gold',String(hero.gold||0))}"
SAVE_NEW="function save(){const raw=JSON.stringify({version:SAVE_VERSION,hero,abyssFloor,abyssRoom,abyssBossDefeated,allies,journal:journalEntries});try{localStorage.setItem(saveKey,raw);localStorage.setItem(saveKey+'_backup',raw);localStorage.setItem('abyss_gold',String(hero.gold||0));return true}catch(e){try{localStorage.setItem(saveKey+'_backup',raw);return true}catch(_){return false}}}"

for p in FILES:
    s=p.read_text(encoding='utf-8')
    for marker in ['TOUCH-BUTTON-FIX-V39','ANDROID-TOUCH-FIX-V42','ANDROID-TOUCH-FIX-V54','ANDROID-CLASS-SELECT-FIX-V43']:
        s=re.sub(r'/\*\s*'+re.escape(marker)+r'.*?\}\)\(\);\s*','',s,flags=re.S)
    s=re.sub(r'\n<!--\s*(?:ANDROID-TOUCH-FIX|ANDROID-CLASS-SELECT-FIX)-[^>]+-->','',s)
    if NORMALIZE_OLD in s:s=s.replace(NORMALIZE_OLD,NORMALIZE_NEW,1)
    if SAVE_OLD in s:s=s.replace(SAVE_OLD,SAVE_NEW,1)
    s=s.replace('Следующий забег начинается с первого этажа.','Текущая глубина сохранена. Следующий забег продолжится с этой глубины.')
    s=s.replace('<button id="continueHit" class="continue-hit hidden" onclick="continueGame()">Продолжить</button>','<button id="continueHit" class="continue-hit" onclick="continueGame()">Продолжить</button>')
    if 'ANDROID-TOUCH-STABLE-V55' not in s:
        pos=s.rfind('</script>')
        if pos<0:raise SystemExit(f'{p}: script close missing')
        s=s[:pos]+'\n'+STABLE_TOUCH+s[pos:]
    p.write_text(s,encoding='utf-8')

for p in FILES:
    s=p.read_text(encoding='utf-8')
    if s.count('ANDROID-TOUCH-STABLE-V55')!=1:raise SystemExit(f'{p}: touch block count invalid')
    for marker in ['TOUCH-BUTTON-FIX-V39','ANDROID-TOUCH-FIX-V42','ANDROID-TOUCH-FIX-V54','ANDROID-CLASS-SELECT-FIX-V43']:
        if marker in s:raise SystemExit(f'{p}: obsolete touch marker remains: {marker}')
    if 'id="continueHit" class="continue-hit"' not in s:raise SystemExit(f'{p}: Continue missing')
    js='\n'.join(m.group(1) for m in re.finditer(r'<script[^>]*>(.*?)</script>',s,re.S))
    Path('/tmp/game.js').write_text(js,encoding='utf-8')
    subprocess.run(['node','--check','/tmp/game.js'],check=True)
print('FINAL STABILIZATION V55 OK')
