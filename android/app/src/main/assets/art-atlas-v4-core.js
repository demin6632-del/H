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