from pathlib import Path

paths=[Path('NEW_DARK_RPG/index.html'),Path('android/app/src/main/assets/index.html')]

set_screen_old="function setScreen(screen,push=true){screens.forEach(s=>{if(el(s))el(s).classList.toggle('hidden',s!==screen)});if(push){if(screenHistory[screenHistory.length-1]!==screen)screenHistory.push(screen);history.pushState({screen:screen},'','#'+screen);if(hero.class)save()}updateHud()}"
set_screen_new="function setScreen(screen,push=true){if(el('menu'))el('menu').classList.toggle('hidden',screen!=='menu');screens.forEach(s=>{if(el(s))el(s).classList.toggle('hidden',s!==screen)});if(push){if(screenHistory[screenHistory.length-1]!==screen)screenHistory.push(screen);history.pushState({screen:screen},'','#'+screen);if(hero.class)save()}updateHud()}"
inv_start="function inventoryType(name){"
inv_end="function renderEquipment(){"
inv_block="""function inventoryType(name){const n=String(name).toLowerCase();if(n.includes('брон')||n.includes('щит'))return'armor';if(n.includes('зель')||n.includes('эликс')||n.includes('мана')||n.includes('здоров'))return'consumable';if(n.includes('ключ'))return'other';return'weapon'}
function itemInfo(raw){if(raw&&typeof raw==='object'&&raw.type)return raw;const name=String(raw&&typeof raw==='object'&&raw.name!==undefined?raw.name:raw);if(name==='Случайный предмет')return{name,type:'random',icon:'🎁'};if(name==='Зелье здоровья')return{name,type:'consumable',effect:'hp',icon:'🧪'};if(name==='Зелье маны')return{name,type:'consumable',effect:'mp',icon:'🔵'};if(name==='Железный меч')return{name,type:'weapon',icon:'🗡️',attack:2};if(name==='Кожаная броня')return{name,type:'armor',icon:'🛡️',def:2};return{name,type:inventoryType(name),icon:inventoryType(name)==='armor'?'🛡️':inventoryType(name)==='consumable'?'🧪':inventoryType(name)==='other'?'🔑':'🗝️'}}
let inventoryCategory='all';
function inventoryTab(cat){inventoryCategory=cat;renderInventory()}
function renderInventory(){const filtered=[];hero.items.forEach((raw,index)=>{const x=itemInfo(raw);if(inventoryCategory==='all'||x.type===inventoryCategory)filtered.push({item:x,index})});if(!filtered.length){if(el('inventoryList'))el('inventoryList').innerHTML='<div class="muted" style="padding:14px;text-align:center">Инвентарь пуст.</div>';return}if(el('inventoryList'))el('inventoryList').innerHTML=filtered.map(({item:x,index})=>{const equipped=(x.type==='weapon'&&hero.weapon===x.name)||(x.type==='armor'&&hero.armor===x.name);const action=x.type==='random'?'Открыть':(x.type==='consumable'?'Использовать':x.type==='other'?'Использовать':equipped?'Экипировано':'Экипировать');const disabled=equipped?'disabled':'';return'<div class="item"><div class="item-icon">'+x.icon+'</div><div>'+x.name+'<small>'+((x.type==='consumable')?(x.effect==='hp'?'Восстанавливает 50 HP':'Восстанавливает 30 MP'):(x.type==='weapon'?'+2 к атаке':x.type==='armor'?'+2 к защите':'Предмет из Бездны'))+'</small></div><button style="width:auto;min-width:92px;margin:0;padding:7px 8px;font-size:12px" '+disabled+' onclick="useInventoryItem('+index+')">'+action+'</button></div>'}).join('')}
function equipItem(index,item){if(item.type==='weapon'){if(hero.weapon===item.name)return;const old=hero.weapon&&hero.weapon!=='Нет'?itemInfo({name:hero.weapon}):null;if(old)hero.attack-=Number(old.attack||2);hero.weapon=item.name;hero.attack+=Number(item.attack||2)}else if(item.type==='armor'){if(hero.armor===item.name)return;const old=hero.armor&&hero.armor!=='Нет'?itemInfo({name:hero.armor}):null;if(old)hero.def-=Number(old.def||2);hero.armor=item.name;hero.def+=Number(item.def||2)}}
function useInventoryItem(index){const raw=hero.items[index];if(raw===undefined)return;const item=itemInfo(raw);const fromBattle=screenHistory[screenHistory.length-1]==='inventory'&&screenHistory[screenHistory.length-2]==='battle';if(item.type==='random'){hero.items[index]=generateLoot();save();sfx('open');logEvent('ПРЕДМЕТ','Случайный предмет открыт: '+hero.items[index].name+'.');renderInventory();if(fromBattle){goBack();enemyTurn()}return}if(item.type==='consumable'){if(item.effect==='hp')hero.hp=Math.min(hero.maxHp,hero.hp+50);if(item.effect==='mp')hero.energy=Math.min(hero.maxEnergy,hero.energy+30);hero.items.splice(index,1);sfx('buy');logEvent('ПРЕДМЕТ',item.name+' использовано.');save();update();renderInventory()}else if(item.type==='weapon'||item.type==='armor'){equipItem(index,item);sfx('buy');logEvent('ЭКИПИРОВКА','Экипировано: '+item.name+'.');save();update();renderInventory()}else if(item.type==='other'){if(item.name==='Таинственный ключ'){hero.items.splice(index,1);logEvent('ПРЕДМЕТ','Таинственный ключ использован.');save();renderInventory()}}if(fromBattle){goBack();enemyTurn()}}
"""

for p in paths:
    s=p.read_text(encoding='utf-8')
    if set_screen_old in s:
        s=s.replace(set_screen_old,set_screen_new,1)
    elif set_screen_new not in s:
        raise SystemExit(f'setScreen target not found: {p}')
    a=s.find(inv_start)
    b=s.find(inv_end,a)
    if a<0 or b<0:
        raise SystemExit(f'inventory block not found: {p}')
    s=s[:a]+inv_block+s[b:]
    p.write_text(s,encoding='utf-8')
    print('repaired',p)
