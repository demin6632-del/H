from pathlib import Path
import re

FILES=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]

FUNCTION_NAMES=['inventoryHasSpace','addItemToInventory','unequipItemType','unequipAll','showStats','showSkills','renderStats','renderSkills']

FUNCTIONS=r'''
function inventoryHasSpace(){return hero.items.length<24}
function addItemToInventory(item){if(!inventoryHasSpace())return false;hero.items.push(item);return true}
function unequipItemType(type){if(type==='weapon'){if(!hero.weapon||hero.weapon==='Нет')return;const old=itemInfo({name:hero.weapon});hero.attack=Math.max(0,hero.attack-Number(old.attack||2));hero.weapon='Нет'}else if(type==='armor'){if(!hero.armor||hero.armor==='Нет')return;const old=itemInfo({name:hero.armor});hero.def=Math.max(0,hero.def-Number(old.def||2));hero.armor='Нет'}save();update();renderHero();renderEquipment();renderInventory();logEvent('ЭКИПИРОВКА','Предмет снят.')}
function unequipAll(){let changed=false;if(hero.weapon&&hero.weapon!=='Нет'){const old=itemInfo({name:hero.weapon});hero.attack=Math.max(0,hero.attack-Number(old.attack||2));hero.weapon='Нет';changed=true}if(hero.armor&&hero.armor!=='Нет'){const old=itemInfo({name:hero.armor});hero.def=Math.max(0,hero.def-Number(old.def||2));hero.armor='Нет';changed=true}if(changed){sfx('back');logEvent('ЭКИПИРОВКА','Снято всё снаряжение.');save();update();renderHero();renderEquipment();renderInventory()}}
function showStats(){renderStats();setScreen('stats')}
function showSkills(){renderSkills();setScreen('skills')}
function renderStats(){const s=classStats[hero.class]||{};const crit=Math.round((hero.crit||0)*100);if(el('statsContent'))el('statsContent').innerHTML='<div class="info-row"><span>Имя</span><b>'+hero.name+'</b></div><div class="info-row"><span>Класс</span><b>'+((hero.class)||'—')+'</b></div><div class="info-row"><span>Уровень</span><b>'+hero.level+'</b></div><div class="info-row"><span>Опыт</span><b>'+hero.xp+'/100</b></div><div class="info-row"><span>Здоровье</span><b>'+hero.hp+'/'+hero.maxHp+'</b></div><div class="info-row"><span>Энергия</span><b>'+hero.energy+'/'+hero.maxEnergy+'</b></div>';if(el('statsCombat'))el('statsCombat').innerHTML='<div>⚔️ Сила: <b>'+hero.attack+'</b></div><div>🛡️ Защита: <b>'+hero.def+'</b></div><div>◆ Критический шанс: <b>'+crit+'%</b></div><div>🪙 Золото: <b>'+getGold()+'</b></div><div>⚔️ Оружие: <b>'+hero.weapon+'</b></div><div>🛡️ Броня: <b>'+hero.armor+'</b></div><div>⭐ Базовая сила класса: <b>'+((s.attack)||'—')+'</b></div><div>🛡️ Базовая защита класса: <b>'+((s.def)||'—')+'</b></div>'}
function renderSkills(){const s=classStats[hero.class]||{};const sk=skillStats[hero.class]||{};if(el('skillsContent'))el('skillsContent').innerHTML='<div class="info-card"><h3>'+((s.skill)||'Навык не выбран')+'</h3><div class="sep"></div><div class="info-row"><span>Класс</span><b>'+((hero.class)||'—')+'</b></div><div class="info-row"><span>Стоимость энергии</span><b>'+((sk.cost)||'—')+'</b></div><div class="info-row"><span>Базовый урон</span><b>'+((sk.damage)||'—')+'</b></div><p class="muted" style="text-align:center;line-height:1.5">Навык класса используется в бою. Параметры зависят от выбранного класса героя.</p></div>'}
'''

def remove_all_functions(src,names):
    for name in names:
        while True:
            marker='function '+name+'('
            p=src.find(marker)
            if p<0: break
            brace=src.find('{',p)
            if brace<0: break
            depth=1;i=brace+1
            while i<len(src) and depth:
                if src[i]=='{':depth+=1
                elif src[i]=='}':depth-=1
                i+=1
            src=src[:p]+src[i:]
    return src

def replace_function(src,name,new):
    marker='function '+name+'('
    p=src.find(marker)
    if p<0:return src,False
    brace=src.find('{',p)
    if brace<0:return src,False
    depth=1;i=brace+1
    while i<len(src) and depth:
        if src[i]=='{':depth+=1
        elif src[i]=='}':depth-=1
        i+=1
    return src[:p]+new+src[i:],True

for path in FILES:
    s=path.read_text(encoding='utf-8')
    original=s

    # Удаляем все накопившиеся версии этих обработчиков и ставим ровно одну финальную версию.
    s=remove_all_functions(s,FUNCTION_NAMES)
    marker='function levelUp(){'
    if marker not in s: raise SystemExit(f'levelUp marker missing: {path}')
    s=s.replace(marker,FUNCTIONS+'\n'+marker,1)

    s=s.replace('id="heroXp">0/1000','id="heroXp">0/100')
    s=s.replace('const xpNeed=1000;','const xpNeed=100;',1)
    s=s.replace('hero.xp+=xp;hero.gold+=gold;const loot=generateLoot();hero.items.push(loot);','hero.xp+=xp;hero.gold+=gold;levelUp();const loot=generateLoot();const lootAdded=addItemToInventory(loot);',1)
    s=s.replace("el('battleLog').innerHTML=sk.skill+' нанёс", "el('battleLog').innerHTML=((classStats[hero.class]||{}).skill||'Навык')+' нанёс",1)
    s=s.replace("logEvent('БОЙ',sk.skill+': '+dmg+' урона.')", "logEvent('БОЙ',((classStats[hero.class]||{}).skill||'Навык')+': '+dmg+' урона.')",1)

    buy_new="function buyItem(id){const item=shopItems.find(x=>x.id===id);if(!item)return;if(!inventoryHasSpace()){sfx('error');if(el('out'))el('out').innerHTML='<span class=\"red\">Инвентарь заполнен (24/24).</span>';return}const gold=getGold();if(gold<item.price){sfx('error');if(el('out'))el('out').innerHTML='<span class=\"red\">Недостаточно золота.</span>';return}hero.gold=gold-item.price;if(item.cat==='weapon'||item.cat==='armor')hero.items.push({name:item.name,type:item.cat,icon:item.icon,attack:item.attack||0,def:item.def||0});else hero.items.push({name:item.name,type:'consumable',effect:item.id==='hp'?'hp':'mp',icon:item.icon});save();update();sfx('buy');logEvent('МАГАЗИН','Куплено: '+item.name+' за '+item.price+' золота.');if(el('out'))el('out').innerHTML='<span class=\"green\">Куплено: '+item.name+'.</span>';shopTab(shopCategory)}"
    s,ok=replace_function(s,'buyItem',buy_new)
    if not ok: raise SystemExit(f'buyItem function missing: {path}')

    s=s.replace("'Победа. +'+xp+' XP, +'+gold+' золота, предмет: '+loot.name+'.'", "'Победа. +'+xp+' XP, +'+gold+' золота.'+(lootAdded?' Предмет: '+loot.name+'.':' Инвентарь заполнен — предмет не получен.')",1)

    if 'id="stats"' not in s:
        marker='<div id="shop" class="screen hidden">'
        stats="""<div id="stats" class="screen hidden"><div class="screen-title"><button class="back-mini" onclick="goBack()">← Назад</button><h2>Статы</h2></div><div class="panel"><div id="statsContent"></div></div><div class="panel"><h3>Боевые параметры</h3><div class="stat-list" id="statsCombat"></div></div></div>\n<div id="skills" class="screen hidden"><div class="screen-title"><button class="back-mini" onclick="goBack()">← Назад</button><h2>Навыки</h2></div><div class="panel"><div id="skillsContent"></div></div></div>\n"""
        if marker not in s: raise SystemExit(f'shop marker missing: {path}')
        s=s.replace(marker,stats+marker,1)

    m=re.search(r"const screens=\[([^\]]+)\];",s)
    if not m: raise SystemExit(f'screens array missing: {path}')
    vals=m.group(1)
    if "'stats'" not in vals: vals += ",'stats'"
    if "'skills'" not in vals: vals += ",'skills'"
    s=s[:m.start(1)]+vals+s[m.end(1):]

    s=re.sub(r'<button[^>]*onclick="(?:heroRefNav\(\'hero\'\)|showHero\(\))"[^>]*><b>▥</b>Статы</button>', '<button onclick="showStats()"><b>▥</b>Статы</button>', s, count=1)
    s=re.sub(r'<button[^>]*onclick="(?:heroRefNav\(\'hero\'\)|showHero\(\))"[^>]*><b>♨</b>Навыки</button>', '<button onclick="showSkills()"><b>♨</b>Навыки</button>', s, count=1)
    s=s.replace('<button onclick="showHero()"><span>◈</span>Статистика</button>','<button onclick="showStats()"><span>◈</span>Статистика</button>',1)

    old_nav="function heroRefNav(id){document.querySelectorAll('.screen').forEach(s=>s.classList.add('hidden'));const target=el(id);if(target)target.classList.remove('hidden');if(id==='hero')renderHero();if(id==='inventory'&&typeof renderInventory==='function')renderInventory();if(id==='equipment'&&typeof renderEquipment==='function')renderEquipment();}"
    new_nav="function heroRefNav(id){if(id==='stats'){showStats();return}if(id==='skills'){showSkills();return}if(id==='hero'){showHero();return}if(id==='inventory'){showInventory();return}if(id==='equipment'){showEquipment();return}setScreen(id)}"
    if old_nav in s: s=s.replace(old_nav,new_nav,1)

    battle_start=s.find('<div id="battle"')
    battle_end=s.find('<div id="inventory"',battle_start)
    if battle_start>=0 and battle_end>battle_start:
        block=s[battle_start:battle_end]
        block=block.replace('<button class="back-mini" onclick="goBack()">← Назад</button>','<button class="back-mini" onclick="escapeBattle()">← Отступить</button>',1)
        block=block.replace('<button onclick="goBack()">← Назад</button>','<button onclick="escapeBattle()">← Отступить</button>',1)
        block=block.replace('<button onclick="escapeBattle()">↩ Отступить</button><button onclick="escapeBattle()">← Отступить</button>','<button onclick="escapeBattle()">↩ Отступить</button>',1)
        s=s[:battle_start]+block+s[battle_end:]

    old_escape="function escapeBattle(){goBack()}"
    new_escape="function escapeBattle(){if(!enemy)return;enemy=null;guard=false;logEvent('БОЙ','Герой отступил. Бой прерван.');save();screenHistory=['menu','main','abyss'];history.replaceState({screen:'abyss'},'','#abyss');setScreen('abyss',false);updateAbyss()}"
    if old_escape in s: s=s.replace(old_escape,new_escape,1)

    style='''<style id="hero-character-scale-final-v1">\n.hero-ref .hero-figure .hero-character-image{display:block!important;width:190px!important;height:auto!important;max-width:none!important;max-height:560px!important;object-fit:contain!important;object-position:center bottom!important;transform:none!important;flex:0 0 auto!important}\n@media(max-width:390px){.hero-ref .hero-figure .hero-character-image{width:170px!important;max-height:500px!important}}\n</style>\n'''
    if 'id="hero-character-scale-final-v1"' not in s:
        s=s.replace('</body></html>',style+'</body></html>')

    if s!=original:
        path.write_text(s,encoding='utf-8')
        print('Patched',path)
    else:
        print('No changes',path)
