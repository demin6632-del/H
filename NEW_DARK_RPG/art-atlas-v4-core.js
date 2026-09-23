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
  if(d!==lastDepth){lastDepth=d;resetForNewDepth();}
  const host=document.getElementById('abyss');
  if(host&&!host.classList.contains('hidden'))panel();
 },900);
})();
