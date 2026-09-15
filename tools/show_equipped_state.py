from pathlib import Path
import re

CSS = '''
.equip-slot{height:68px!important;display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:2px!important;font-size:20px!important;position:relative!important;text-align:center!important}.equip-slot .equip-name{font:10px monospace;color:#ddd;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.equip-slot .equip-state{font:9px monospace;color:#777;letter-spacing:.5px}.equip-slot.equipped{border-color:#4d9b55!important;background:linear-gradient(#0b160c,#070907)!important;box-shadow:0 0 9px rgba(80,190,90,.18),inset 0 0 10px rgba(70,180,80,.08)!important}.equip-slot.equipped .equip-state{color:#77db70;font-weight:bold}.equip-slot.empty{border-color:#4b1515!important;opacity:.72}.inventory-equipped{border-color:#4d9b55!important;background:linear-gradient(90deg,#080f09,#080808)!important;box-shadow:0 0 8px rgba(80,190,90,.14)}.inventory-equipped .item-icon{border-color:#4d9b55!important}.equipped-badge{display:inline-block;margin-left:5px;padding:2px 5px;border:1px solid #4d9b55;border-radius:3px;color:#77db70;font:9px monospace;letter-spacing:.3px;vertical-align:middle}.not-equipped-badge{display:inline-block;margin-left:5px;padding:2px 5px;border:1px solid #5b2929;border-radius:3px;color:#a66;font:9px monospace;letter-spacing:.3px;vertical-align:middle}
'''

INVENTORY_OLD = "const action=x.type==='random'?'Открыть':(x.type==='consumable'?'Использовать':x.type==='other'?'Использовать':equipped?'Экипировано':'Экипировать');const disabled=equipped?'disabled':'';return'<div class=\"item\"><div class=\"item-icon\">'+x.icon+'</div><div>'+x.name+'<small>"
INVENTORY_NEW = "const equippable=x.type==='weapon'||x.type==='armor';const action=x.type==='random'?'Открыть':(x.type==='consumable'?'Использовать':x.type==='other'?'Использовать':equipped?'Экипировано':'Экипировать');const disabled=equipped?'disabled':'';const rowClass=equipped?'item inventory-equipped':'item';const badge=equippable?(equipped?'<span class=\"equipped-badge\">✓ ЭКИПИРОВАНО</span>':'<span class=\"not-equipped-badge\">НЕ ЭКИПИРОВАНО</span>'):'';return'<div class=\"'+rowClass+'\"><div class=\"item-icon\">'+x.icon+'</div><div>'+x.name+badge+'<small>"

EQUIPMENT_RE = re.compile(r"function renderEquipment\(\)\{.*?\}\nfunction renderHero", re.S)
EQUIPMENT_NEW = '''function renderEquipment(){if(!el('equipStats'))return;const w=hero.weapon&&hero.weapon!=='Нет'?hero.weapon:'Нет';const a=hero.armor&&hero.armor!=='Нет'?hero.armor:'Нет';const setSlot=(id,icon,name)=>{const node=el(id);if(!node)return;const equipped=name!=='Нет';node.className='equip-slot '+(equipped?'equipped':'empty');node.innerHTML=`<div>${icon}</div><div class="equip-name">${equipped?name:'Пусто'}</div><div class="equip-state">${equipped?'✓ ЭКИПИРОВАНО':'— НЕ ЭКИПИРОВАНО'}</div>`};setSlot('equipWeapon',w==='Нет'?'🗡️':'⚔️',w);setSlot('equipArmor','🛡️',a);setSlot('equipHead','🪖','Нет');setSlot('equipRing','💍','Нет');setSlot('equipBody','🧥','Нет');setSlot('equipBoots','👢','Нет');el('equipStats').innerHTML=`Оружие: <b>${w}</b> ${w==='Нет'?'<span class="not-equipped-badge">НЕ ЭКИПИРОВАНО</span>':'<span class="equipped-badge">✓ ЭКИПИРОВАНО</span>'}<br>Броня: <b>${a}</b> ${a==='Нет'?'<span class="not-equipped-badge">НЕ ЭКИПИРОВАНО</span>':'<span class="equipped-badge">✓ ЭКИПИРОВАНО</span>'}<br>Здоровье: ${hero.maxHp}<br>Мана: ${hero.maxEnergy}<br>Сила: ${hero.attack}<br>Защита: ${hero.def}<br><br><span class="gold">Активные союзники: ${allies.length}</span>`}
function renderHero'''

def patch(path):
    p=Path(path); s=p.read_text()
    if '.equipped-badge' not in s:
        s=s.replace('</style>', CSS+'</style>', 1)
    if 'const equippable=x.type===' not in s and INVENTORY_OLD in s:
        s=s.replace(INVENTORY_OLD, INVENTORY_NEW, 1)
    if 'const setSlot=(id,icon,name)=>' not in s and EQUIPMENT_RE.search(s):
        s=EQUIPMENT_RE.sub(EQUIPMENT_NEW, s, count=1)
    p.write_text(s)

for path in ['NEW_DARK_RPG/index.html','android/app/src/main/assets/index.html']:
    patch(path)
print('Equipped-state UI patched in source and Android asset.')
