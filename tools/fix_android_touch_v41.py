from pathlib import Path
import re
import subprocess

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
    while True:
        start=s.find('/* TOUCH-BUTTON-FIX-V39')
        if start<0: break
        end=s.find('})();',start)
        if end<0: raise SystemExit(f'{p}: V39 closing marker not found')
        s=s[:start]+s[end+4:]
    while True:
        start=s.find('/* ANDROID-TOUCH-FIX-V42')
        if start<0: break
        end=s.find('})();',start)
        if end<0: raise SystemExit(f'{p}: V42 closing marker not found')
        s=s[:start]+s[end+4:]
    old="const __unequipAll=unequipAll; unequipAll=function(){ensureGear();__unequipAll.apply(this,arguments);Object.keys(hero.gear).forEach(k=>{hero.gear[k]='Нет'});save();update();renderHero();renderEquipment();renderInventory()};"
    new="const __unequipAll=unequipAll; unequipAll=function(){ensureGear();Object.keys(hero.gear).forEach(k=>{const name=hero.gear[k];if(!name||name==='Нет')return;const old=gearInfo({name});hero.def=Math.max(0,hero.def-Number(old.def||0));hero.crit=Math.max(0,hero.crit-Number(old.crit||0));hero.maxEnergy=Math.max(1,hero.maxEnergy-Number(old.maxEnergy||0));hero.energy=Math.min(hero.energy,hero.maxEnergy);hero.gear[k]='Нет'});__unequipAll.apply(this,arguments);save();update();renderHero();renderEquipment();renderInventory()};"
    if old in s:s=s.replace(old,new,1)
    pos=s.rfind('</script>')
    if pos<0: raise SystemExit(f'{p}: script closing tag missing')
    s=s[:pos]+'\n'+PATCH+s[pos:]
    s=s.replace('<!-- ANDROID-TOUCH-FIX-V4-FINAL: synthetic click now reaches the original button handler. -->','')
    s += f'\n<!-- {MARK}: native click is primary; delayed pointer/touch fallback is duplicate-safe. -->\n'
    js='\n'.join(m.group(1) for m in re.finditer(r'<script[^>]*>(.*?)</script>',s,re.S))
    Path('/tmp/final_game.js').write_text(js,encoding='utf-8')
    subprocess.run(['node','--check','/tmp/final_game.js'],check=True)
    ids=re.findall(r'\bid=["\']([^"\']+)',s,re.I)
    dup=sorted({x for x in ids if ids.count(x)>1})
    if dup: raise SystemExit(f'{p}: duplicate ids: {dup}')
    funcs=set(re.findall(r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\(',js))
    funcs|=set(re.findall(r'window\.([A-Za-z_$][\w$]*)\s*=\s*function',js))
    known={'if','for','while','switch','catch','setTimeout','clearTimeout'}
    missing=[]
    for m in re.finditer(r'onclick\s*=\s*["\']([^"\']+)',s,re.I):
        for fn in re.findall(r'\b([A-Za-z_$][\w$]*)\s*\(',m.group(1)):
            if fn not in funcs and fn not in known: missing.append(fn)
    if missing: raise SystemExit(f'{p}: missing onclick handlers: {sorted(set(missing))}')
    if 'TOUCH-BUTTON-FIX-V39' in s: raise SystemExit(f'{p}: obsolete V39 interceptor remains')
    if 'ANDROID-TOUCH-FIX-V42' not in s: raise SystemExit(f'{p}: V42 handler missing')
    if 'function inventoryHasSpace()' not in s: raise SystemExit(f'{p}: inventory guard missing')
    print(f'FINAL GAME AUDIT OK: {p}; buttons={len(re.findall(r"<button\\b",s,re.I))}; handlers={len(funcs)}')
    p.write_text(s,encoding='utf-8')

# V43 должен применяться после V41: иначе последующая стадия сборки затирает прямой обработчик классов.
subprocess.run(['python','tools/fix_android_touch_v42.py'],check=True)
print(MARK+' + V43')
