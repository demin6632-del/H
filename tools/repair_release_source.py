from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
web=root/'NEW_DARK_RPG/index.html'
canonical=root/'android/app/src/main/assets/index.html'
if web.read_text(encoding='utf-8').strip() == '<!DOCTYPE html>PLACEHOLDER':
    shutil.copy2(canonical, web)
s=web.read_text(encoding='utf-8')
s=s.replace("function start(className){gameMusicAllowed=true;resetAbyss();let st=classStats[className];hero={", "function start(className){gameMusicAllowed=true;abyssKeyCaches={};window.abyssKeyCaches=abyssKeyCaches;try{localStorage.removeItem('abyss_key_caches');localStorage.removeItem('abyss_gear');}catch(e){}resetAbyss();let st=classStats[className];hero={",1)
s=s.replace("function heroRefNav(id){document.querySelectorAll('.screen').forEach(s=>s.classList.add('hidden'));const target=el(id);if(target)target.classList.remove('hidden');if(id==='hero')renderHero();if(id==='inventory'&&typeof renderInventory==='function')renderInventory();if(id==='equipment'&&typeof renderEquipment==='function')renderEquipment();if(id==='stats')renderStats();if(id==='skills')renderSkills();}", "function heroRefNav(id){if(!screens.includes(id))return;if(id==='hero')renderHero();if(id==='inventory'&&typeof renderInventory==='function')renderInventory();if(id==='equipment'&&typeof renderEquipment==='function')renderEquipment();if(id==='stats')renderStats();if(id==='skills')renderSkills();setScreen(id);}",1)
s=s.replace("function restoreBest(){if(typeof abyssFloor!=='number')return;const best=readBest();if(best>abyssFloor)abyssFloor=best;}", "function restoreBest(){if(typeof abyssFloor!=='number')return;const best=readBest();if(best<1)localStorage.setItem(BEST_KEY,'1');}",1)
s=s.replace("      try{restoreBest()}catch(e){}\n      const r=__updateAbyss.apply(this,arguments);", "      const r=__updateAbyss.apply(this,arguments);",1)
s=s.replace("function hasSave(){return !!localStorage.getItem(saveKey)}", "function hasSave(){return !!localStorage.getItem(saveKey)||!!localStorage.getItem(saveKey+'_backup')}",1)
s=s.replace("const __save=save; save=function(){ensureGear();localStorage.setItem('abyss_gear',JSON.stringify(hero.gear));localStorage.setItem('abyss_key_caches',JSON.stringify(abyssKeyCaches||{}));return __save.apply(this,arguments)};", "const __save=save; save=function(){ensureGear();try{localStorage.setItem('abyss_gear',JSON.stringify(hero.gear));localStorage.setItem('abyss_key_caches',JSON.stringify(abyssKeyCaches||{}));}catch(e){}return __save.apply(this,arguments)};",1)
s=s.replace("Начат новый забег: '+className+' .", "Начато восхождение: '+className+' .")
s=s.replace("Начат новый забег: '+className+'.", "Начато восхождение: '+className+'.")
s=s.replace("Следующий забег продолжится с этой глубины.", "Восхождение продолжится с этой глубины.")
s=s.replace("Текущий забег завершён. Уровень, предметы и золото сохранены.", "Текущее восхождение завершено. Уровень, предметы и золото сохранены.")
needle='<script src="art-atlas-v4.js"></script>'
if 'art-atlas-v4-fix.js' not in s and needle in s:
    s=s.replace(needle,needle+'<script src="art-atlas-v4-fix.js"></script>',1)
web.write_text(s,encoding='utf-8')
shutil.copy2(web,canonical)
