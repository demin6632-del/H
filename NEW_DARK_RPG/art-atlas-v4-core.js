/* ART-ATLAS-V5 — generated PNG visual layer. Gameplay/UI untouched. */
(function(){
if(window.__ART_ATLAS_V5)return;
window.__ART_ATLAS_V5=true;

const SCENE={
start:'abyss_gate',ordinary:'void_bridge',treasure:'ancient_gate',shop:'obsidian_hall',
forge:'iron_ruins',tavern:'black_keep',sanctuary:'abyss_core',cursed:'bone_catacomb',
library:'cursed_library',altar:'blood_rift',trap:'red_chasm',labyrinth:'shadow_forest',
portal:'abyss_core',bossroom:'rift_lord',eliteroom:'archon_chamber',event:'endless_depth'
};
const CREATURE=['shadow','hunter','mutant','bones','elite','boss','hero'];

function generatedScene(key){return SCENE[key]||'void_bridge';}
function generatedCreature(key){return CREATURE.includes(key)?key:'shadow';}

function renderV4Tile(el,key,w,h){
 if(!el)return false;
 const name=generatedScene(key);
 el.style.setProperty('background-image','linear-gradient(rgba(5,0,4,.18),rgba(0,0,0,.42)),url("generated/'+name+'.png")','important');
 el.style.setProperty('background-size','cover','important');
 el.style.setProperty('background-position','center center','important');
 el.style.setProperty('background-repeat','no-repeat','important');
 el.style.setProperty('image-rendering','auto','important');
 el.dataset.v4QualityKey=name;
 return true;
}
window.renderV4Tile=renderV4Tile;

function installSceneArtFix(){
 const id='art-v5-scene-clean';
 if(document.getElementById(id))return;
 const style=document.createElement('style');
 style.id=id;
 style.textContent='.scene.art-v5-scene:before,.scene.art-v5-scene:after{display:none!important}';
 document.head.appendChild(style);
}

function setScene(id,key){
 const s=document.querySelector('#'+id+' .scene');
 if(!s)return;
 s.classList.add('art-v5-scene');
 renderV4Tile(s,key,s.clientWidth||700,s.clientHeight||390);
}
function roomKeyV4(){
 const c=String(typeof abyssRoomContent!=='undefined'?abyssRoomContent:'');
 if(c.includes('Кровавый алтарь'))return'altar';
 if(c.includes('Забытый тайник'))return'treasure';
 if(c.includes('Источник Бездны'))return'portal';
 if(c.includes('Босс:'))return'bossroom';
 if(c.includes('Элитный враг:'))return'eliteroom';
 if(c.includes('Пустой проход')||c.includes('Побеждён'))return'ordinary';
 return'labyrinth';
}
function updateScenesV4(){
 setScene('main','start');setScene('shop','shop');setScene('tavern','tavern');
 setScene('equipment','forge');setScene('stats','library');setScene('journal','ordinary');
 setScene('death','cursed');
 const a=document.getElementById('abyss');
 if(a&&!a.classList.contains('hidden'))setScene('abyss',roomKeyV4());
}
function installBattleV4(){
 const old=window.updateBattle;
 if(typeof old!=='function'||old.__artV4)return false;
 function wrapped(){
  old.apply(this,arguments);
  const b=document.getElementById('enemyArt');if(!b)return;
  let k='shadow';
  if(typeof enemy!=='undefined'&&enemy){
   if(enemy.isBoss)k='boss';
   else if(enemy.isElite)k='elite';
   else k=({'Теневой зверь':'shadow','Заражённый охотник':'hunter','Мутант пустоши':'mutant','Пожиратель костей':'bones'})[enemy.name]||'shadow';
  }
  b.innerHTML='<img src="generated/'+generatedCreature(k)+'.png" alt="" style="display:block;width:min(86vw,360px);height:min(86vw,300px);object-fit:cover;object-position:center;margin:auto;border:1px solid rgba(45,125,170,.65);box-shadow:0 0 22px rgba(0,70,110,.28)">';
 }
 wrapped.__artV4=true;wrapped.__battleArtRuntimeFix=true;window.updateBattle=wrapped;return true;
}
function installAbyssV4(){
 const old=window.updateAbyss;
 if(typeof old!=='function'||old.__artV4)return false;
 function wrapped(){old.apply(this,arguments);setTimeout(updateScenesV4,0);}
 wrapped.__artV4=true;window.updateAbyss=wrapped;return true;
}
function installScreenV4(){
 const old=window.setScreen;
 if(typeof old!=='function'||old.__artV4)return false;
 function wrapped(){old.apply(this,arguments);setTimeout(updateScenesV4,0);}
 wrapped.__artV4=true;window.setScreen=wrapped;return true;
}
function bootV4(){installSceneArtFix();installBattleV4();installAbyssV4();installScreenV4();updateScenesV4();}
bootV4();document.addEventListener('DOMContentLoaded',bootV4);setTimeout(bootV4,250);
})();

/* === ABYSS-EXPEDITION-INSPIRED-V1 ===
   Самостоятельный слой экспедиционных контрактов.
   Не копирует тексты/персонажей/ассеты сторонней игры.
   Работает поверх существующей Бездны и не заменяет её state machine.
*/
(function(){
 if(window.__COA_EXPEDITION_INSPIRED_V1__)return;
 window.__COA_EXPEDITION_INSPIRED_V1__=true;

 const CONTRACT_KEY='chronicles_abyss_contract_v1';
 const CONTRACTS=[
  {id:'scout',icon:'🔎',name:'Следопыт',desc:'Исследовать участок внимательно и не спешить.',goal:2,reward:55},
  {id:'survivor',icon:'🛡️',name:'Выживший',desc:'Завершить глубину с риском не выше 55.',goal:5,reward:70},
  {id:'hunter',icon:'⚔️',name:'Охотник',desc:'Победить существо в ходе экспедиции.',goal:1,reward:85},
  {id:'relic',icon:'📦',name:'Искатель реликвий',desc:'Забрать находку или изучить руины.',goal:1,reward:65}
 ];

 function read(){
  try{
   const x=JSON.parse(localStorage.getItem(CONTRACT_KEY)||'null');
   return x&&typeof x==='object'?x:null;
  }catch(e){return null}
 }
 function write(x){
  try{localStorage.setItem(CONTRACT_KEY,JSON.stringify(x))}catch(e){}
 }
 function depth(){
  return Math.max(1,Math.min(7,Number(window.abyssFloor||1)||1));
 }
 function syncDepthColor(){ window.depthColor=color(depth()); }
 syncDepthColor();
 function chooseContract(){
  const pool=CONTRACTS.slice().sort(()=>Math.random()-.5);
  return pool.slice(0,3);
 }
 function ensure(){
  const old=read();
  if(old&&old.depth===depth()&&old.contract)return old;
  const choices=chooseContract();
  const x={depth:depth(),choices,contract:null,progress:0,completed:false};
  write(x);
  return x;
 }
 function color(d){
  return d<=2?'#77db70':d<=5?'#d9a52b':'#e22';
 }
 function reward(amount){
  if(typeof hero==='undefined'||!hero)return;
  hero.gold=Math.max(0,Number(hero.gold||0)+amount);
  try{localStorage.setItem('abyss_gold',String(hero.gold))}catch(e){}
  if(typeof render==='function')render();
 }
 function panel(){
  const host=document.getElementById('abyss');
  if(!host||host.classList.contains('hidden'))return;
  const root=document.getElementById('abyssExpeditionUI');
  if(!root)return;
  let p=document.getElementById('abyssContractUI');
  if(!p){
   p=document.createElement('div');
   p.id='abyssContractUI';
   p.className='panel';
   p.style.cssText='margin:8px 0 0;padding:9px;border-color:#6b1b1b';
   root.parentNode.insertBefore(p,root);
  }
  const state=ensure();
  const d=depth();
  if(!state.contract){
   p.innerHTML='<div style="text-align:center;color:'+color(d)+';font-weight:bold">📜 КОНТРАКТ ЭКСПЕДИЦИИ</div>'+
    '<div class="muted" style="text-align:center;font-size:11px;margin:5px 0 8px">Выбери цель забега. Это дополнительная задача, а не обязательный путь.</div>'+
    '<div id="abyssContractChoices" style="display:grid;gap:6px">'+
    state.choices.map((c,i)=>'<button data-contract-index="'+i+'" style="margin:0;text-align:left"><b>'+c.icon+' '+c.name+'</b><br><small style="color:#999">'+c.desc+' · награда '+c.reward+' золота</small></button>').join('')+
    '</div>';
   p.querySelectorAll('[data-contract-index]').forEach(b=>b.onclick=function(){
    const i=Number(this.dataset.contractIndex);
    state.contract=state.choices[i];
    state.progress=0;
    state.completed=false;
    write(state);
    panel();
   });
   return;
  }
  const c=state.contract;
  if(!state.completed && c.id==='survivor' && state.progress>=5){
   state.completed=true;write(state);reward(c.reward);
  }
  p.innerHTML='<div style="display:flex;justify-content:space-between;gap:8px"><b>'+c.icon+' '+c.name+'</b><b style="color:'+color(d)+'">Глубина '+d+'/7</b></div>'+
   '<div class="muted" style="font-size:11px;margin-top:4px">'+c.desc+'</div>'+
   '<div style="margin-top:7px;font:11px monospace;color:'+(state.completed?'#77db70':'#d9a52b')+'">'+
   (state.completed?'✓ Контракт выполнен · +'+c.reward+' золота':'Прогресс: '+Math.min(c.goal,state.progress)+'/'+c.goal)+'</div>';
 }
 function bump(type){
  const s=read();
  if(!s||!s.contract||s.completed)return;
  const c=s.contract;
  if(c.id==='survivor'){
   try{const e=JSON.parse(localStorage.getItem('chronicles_abyss_expedition_v2')||'null');s.progress=Math.min(c.goal,Number(e&&e.done||0));if(s.progress>=c.goal){s.completed=true;write(s);reward(c.reward);setTimeout(panel,0);return}}catch(e){}
  }
  let add=0;
  if(c.id==='scout'&&type==='inspect')add=1;
  if(c.id==='hunter'&&type==='battle')add=1;
  if(c.id==='relic'&&(type==='take'||type==='search'))add=1;
  if(add){
   s.progress=Math.min(c.goal,s.progress+add);
   if(s.progress>=c.goal){s.completed=true;write(s);reward(c.reward);setTimeout(panel,0);return}
   write(s);
  }
  setTimeout(panel,0);
 }
 function resetForNewDepth(){
  try{
   const s=read();
   if(s&&s.depth!==depth())localStorage.removeItem(CONTRACT_KEY);
  }catch(e){}
  setTimeout(panel,0);
 }

 const oldShow=window.showAbyss;
 if(typeof oldShow==='function'&&!oldShow.__expeditionInspired){
  const wrapped=function(){
   const out=oldShow.apply(this,arguments);
   setTimeout(panel,0);
   return out;
  };
  wrapped.__expeditionInspired=true;
  window.showAbyss=wrapped;
  window.startAbyssExpedition=wrapped;
 }
 document.addEventListener('click',function(e){
  const b=e.target&&e.target.closest?e.target.closest('[data-action]'):null;
  if(!b)return;
  const a=b.getAttribute('data-action');
  if(a==='inspect')bump('inspect');
  else if(a==='fight')bump('battle');
  else if(a==='take'||a==='search')bump(a);
  else if(a==='start')setTimeout(panel,120);
 },true);
 let lastDepth=depth();
 setInterval(function(){
  const d=depth();
  syncDepthColor();
  if(d!==lastDepth){lastDepth=d;resetForNewDepth();}
  const host=document.getElementById('abyss');
  if(host&&!host.classList.contains('hidden'))panel();
 },900);
})();


/* === ABYSS-ROUTE-CHOICE-V1 === */
(function(){
 if(window.__COA_ROUTE_CHOICE_V1__)return; window.__COA_ROUTE_CHOICE_V1__=true;
 const KEY='chronicles_abyss_route_v1';
 function read(){try{return JSON.parse(localStorage.getItem(KEY)||'null')}catch(e){return null}}
 function write(x){try{localStorage.setItem(KEY,JSON.stringify(x))}catch(e){}}
 function depth(){return Math.max(1,Math.min(7,Number(window.abyssFloor||1)||1))}
 function state(){let s=read();if(!s||s.depth!==depth()){s={depth:depth(),route:null,history:[]};write(s)}return s}
 function render(){
  const root=document.getElementById('abyssExpeditionUI'); if(!root||document.getElementById('abyssRouteUI'))return;
  const s=state(); if(s.route)return;
  const p=document.createElement('div');p.id='abyssRouteUI';p.className='panel';p.style.cssText='margin:8px 0;padding:9px;border-color:#342c20';
  p.innerHTML='<div style="text-align:center;font-weight:bold">🧭 Выбор пути</div><div class="muted" style="text-align:center;font-size:11px;margin:5px 0 8px">Перед исследованием выбери направление. Оно меняет характер следующего события.</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:6px"><button data-route="careful">🕯 Осторожный путь<br><small>меньше риска</small></button><button data-route="danger">🩸 Опасный путь<br><small>выше шанс награды</small></button></div>';
  root.parentNode.insertBefore(p,root);
  p.querySelectorAll('[data-route]').forEach(b=>b.onclick=function(){const x=state();x.route=this.dataset.route;x.history.push({depth:depth(),route:x.route,applied:false});write(x);p.remove();applyRouteEffects(x);if(typeof window.showAbyss==='function')window.showAbyss()});
 }
 function applyRouteEffects(x){if(!x||x.applied)return;try{const e=JSON.parse(localStorage.getItem('chronicles_abyss_expedition_v2')||'null');if(!e||typeof e!=='object')return;if(x.route==='careful'){e.risk=Math.max(0,Number(e.risk||0)-12);e.awareness=Math.min(100,Number(e.awareness||0)+8);e.tempo=Math.max(0,Number(e.tempo||0)-5);}else if(x.route==='danger'){e.risk=Math.min(100,Number(e.risk||0)+12);e.awareness=Math.max(0,Number(e.awareness||0)-8);e.tempo=Math.min(100,Number(e.tempo||0)+8);}localStorage.setItem('chronicles_abyss_expedition_v2',JSON.stringify(e));x.applied=true;write(x);}catch(e){}}
window.__coaAbyssRoute=state;
 const old=window.showAbyss;
 if(typeof old==='function'&&!old.__routeWrapped){const w=function(){const r=old.apply(this,arguments);setTimeout(render,80);return r};w.__routeWrapped=true;window.showAbyss=w;window.startAbyssExpedition=w}
 document.addEventListener('click',function(e){const b=e.target&&e.target.closest?e.target.closest('[data-action]'):null;if(!b)return;const a=b.getAttribute('data-action');if(a!=='take'&&a!=='search')return;const x=state();if(x.route!=='danger'||!x.applied)return;setTimeout(function(){try{const bonus=a==='take'?Math.max(8,Math.round(25+depth()*7)*0.35):Math.max(5,Math.round((10+depth()*3)*0.35));const fresh=state();if(fresh.route!=='danger'||!fresh.applied)return;if(typeof hero!=='undefined'&&hero){hero.gold=Math.max(0,Number(hero.gold||0)+bonus);try{localStorage.setItem('abyss_gold',String(hero.gold))}catch(_){}if(typeof save==='function')save();if(typeof render==='function')render();logEvent('ПУТЬ','Опасный маршрут принёс дополнительную добычу: +'+bonus+' золота.');}}catch(_){}},120);},true);
 let last=depth();setInterval(()=>{const d=depth();if(d!==last){last=d;try{localStorage.removeItem(KEY)}catch(e){}}const h=document.getElementById('abyss');if(h&&!h.classList.contains('hidden'))render()},1000);
})();
