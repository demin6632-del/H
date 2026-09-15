from pathlib import Path

FILES = [Path('NEW_DARK_RPG/index.html'), Path('android/app/src/main/assets/index.html')]

NAV_OLD = '''<button onclick="heroRefNav('hero')"><b>▥</b>Статы</button><button onclick="heroRefNav('hero')"><b>♨</b>Навыки</button>'''
NAV_NEW = '''<button onclick="showStats()"><b>▥</b>Статы</button><button onclick="showSkills()"><b>♨</b>Навыки</button>'''

SCREENS_OLD = "const screens=['menu','classes','main','abyss','battle','inventory','equipment','hero','shop','tavern','settings','journal','death'];"
SCREENS_NEW = "const screens=['menu','classes','main','abyss','battle','inventory','equipment','hero','stats','skills','shop','tavern','settings','journal','death'];"

STATS_SCREEN = '''<div id="stats" class="screen hidden"><div class="screen-title"><button class="back-mini" onclick="goBack()">← Назад</button><h2>Статы</h2></div><div class="panel"><div id="statsContent"></div></div><div class="panel"><h3>Боевые параметры</h3><div class="stat-list" id="statsCombat"></div></div></div>'''
SKILLS_SCREEN = '''<div id="skills" class="screen hidden"><div class="screen-title"><button class="back-mini" onclick="goBack()">← Назад</button><h2>Навыки</h2></div><div class="panel"><div id="skillsContent"></div></div></div>'''

FUNCTIONS = '''function renderStats(){const s=classStats[hero.class]||{};const crit=Math.round((hero.crit||0)*100);if(el('statsContent'))el('statsContent').innerHTML='<div class="info-row"><span>Имя</span><b>'+hero.name+'</b></div><div class="info-row"><span>Класс</span><b>'+((hero.class)||'—')+'</b></div><div class="info-row"><span>Уровень</span><b>'+hero.level+'</b></div><div class="info-row"><span>Опыт</span><b>'+hero.xp+'/1000</b></div><div class="info-row"><span>Здоровье</span><b>'+hero.hp+'/'+hero.maxHp+'</b></div><div class="info-row"><span>Энергия</span><b>'+hero.energy+'/'+hero.maxEnergy+'</b></div>';if(el('statsCombat'))el('statsCombat').innerHTML='<div>⚔️ Сила: <b>'+hero.attack+'</b></div><div>🛡️ Защита: <b>'+hero.def+'</b></div><div>◆ Критический шанс: <b>'+crit+'%</b></div><div>🪙 Золото: <b>'+getGold()+'</b></div><div>⚔️ Оружие: <b>'+hero.weapon+'</b></div><div>🛡️ Броня: <b>'+hero.armor+'</b></div><div>⭐ Базовая сила класса: <b>'+((s.attack)||'—')+'</b></div><div>🛡️ Базовая защита класса: <b>'+((s.def)||'—')+'</b></div>'}
function renderSkills(){const s=classStats[hero.class]||{};const sk=skillStats[hero.class]||{};if(el('skillsContent'))el('skillsContent').innerHTML='<div class="info-card"><h3>'+((s.skill)||'Навык не выбран')+'</h3><div class="sep"></div><div class="info-row"><span>Класс</span><b>'+((hero.class)||'—')+'</b></div><div class="info-row"><span>Стоимость энергии</span><b>'+((sk.cost)||'—')+'</b></div><div class="info-row"><span>Базовый урон</span><b>'+((sk.damage)||'—')+'</b></div><p class="muted" style="text-align:center;line-height:1.5">Навык класса используется в бою. Параметры зависят от выбранного класса героя.</p></div>'}
function showStats(){setScreen('stats');renderStats()}
function showSkills(){setScreen('skills');renderSkills()}
'''

NAV_MARKER = '</div></div>\n<div id="shop" class="screen hidden">'

for path in FILES:
    if not path.exists():
        raise SystemExit(f'Missing file: {path}')
    s = path.read_text(encoding='utf-8')
    original = s
    s = s.replace(NAV_OLD, NAV_NEW)
    if s.count(NAV_NEW) == 0:
        raise SystemExit(f'Stats/skills navigation not found in {path}')
    s = s.replace(SCREENS_OLD, SCREENS_NEW, 1)
    if 'id="stats"' not in s:
        if NAV_MARKER not in s:
            raise SystemExit(f'Shop insertion marker not found in {path}')
        s = s.replace(NAV_MARKER, '</div></div>\n' + STATS_SCREEN + '\n' + SKILLS_SCREEN + '\n<div id="shop" class="screen hidden">', 1)
    if 'function renderStats(){' not in s:
        marker = 'function heroRefNav(id){'
        if marker not in s:
            raise SystemExit(f'heroRefNav marker not found in {path}')
        s = s.replace(marker, FUNCTIONS + marker, 1)
    old_nav = "function heroRefNav(id){document.querySelectorAll('.screen').forEach(s=>s.classList.add('hidden'));const target=el(id);if(target)target.classList.remove('hidden');if(id==='hero')renderHero();if(id==='inventory'&&typeof renderInventory==='function')renderInventory();if(id==='equipment'&&typeof renderEquipment==='function')renderEquipment();}"
    new_nav = "function heroRefNav(id){document.querySelectorAll('.screen').forEach(s=>s.classList.add('hidden'));const target=el(id);if(target)target.classList.remove('hidden');if(id==='hero')renderHero();if(id==='inventory'&&typeof renderInventory==='function')renderInventory();if(id==='equipment'&&typeof renderEquipment==='function')renderEquipment();if(id==='stats')renderStats();if(id==='skills')renderSkills();}"
    s = s.replace(old_nav, new_nav, 1)
    if s == original:
        print(f'No changes needed: {path}')
    else:
        path.write_text(s, encoding='utf-8')
        print(f'Patched: {path}')
