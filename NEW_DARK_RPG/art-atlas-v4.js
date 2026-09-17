/* ART-ATLAS-V4-RUNTIME — сохраняет оригинальный V4-атлас и накладывает только технические исправления. */
(function(){
  if(window.__ART_ATLAS_V4_RUNTIME)return;
  window.__ART_ATLAS_V4_RUNTIME=true;
  const core=document.createElement('script');core.src='art-atlas-v4-core.js';
  core.onload=function(){
    const patch=function(){try{
      if(typeof restoreBest==='function'&&!restoreBest.__fixed){const f=function(){};f.__fixed=true;window.restoreBest=f;}
      if(typeof hasSave==='function'&&!hasSave.__fixed){const f=function(){return !!localStorage.getItem(saveKey)||!!localStorage.getItem(saveKey+'_backup')};f.__fixed=true;window.hasSave=f;}
      if(typeof heroRefNav==='function'&&!heroRefNav.__fixed){const f=function(id){if(!screens.includes(id))return;if(id==='hero')renderHero();if(id==='inventory'&&typeof renderInventory==='function')renderInventory();if(id==='equipment'&&typeof renderEquipment==='function')renderEquipment();if(id==='stats')renderStats();if(id==='skills')renderSkills();setScreen(id)};f.__fixed=true;window.heroRefNav=f;}
      if(typeof start==='function'&&!start.__fixed){const old=start;const f=function(className){try{abyssKeyCaches={};window.abyssKeyCaches=abyssKeyCaches;localStorage.removeItem('abyss_key_caches');localStorage.removeItem('abyss_gear')}catch(e){}return old.apply(this,arguments)};f.__fixed=true;window.start=f;}
      if(typeof save==='function'&&!save.__fixed){const old=save;const f=function(){try{if(typeof ensureGear==='function')ensureGear();localStorage.setItem('abyss_gear',JSON.stringify(hero.gear));localStorage.setItem('abyss_key_caches',JSON.stringify(abyssKeyCaches||{}))}catch(e){}return old.apply(this,arguments)};f.__fixed=true;window.save=f;}
      if(typeof updateBattle==='function'&&!updateBattle.__battleArtRuntimeFix){const old=updateBattle;const f=function(){old.apply(this,arguments);const b=document.getElementById('enemyArt');if(!b)return;const bg=document.querySelector('.scene.art-v4-scene')?.style.backgroundImage||'';const m=bg.match(/^url\(\"?(data:image\/webp;base64,[^\"\)]+)\"?\)$/);if(!m)return;let k='shadow';if(typeof enemy!=='undefined'&&enemy){if(enemy.isBoss)k='boss';else if(enemy.isElite)k='elite';else k=({'Теневой зверь':'shadow','Заражённый охотник':'hunter','Мутант пустоши':'mutant','Пожиратель костей':'bones'})[enemy.name]||'shadow'}const idx={shadow:0,hunter:1,mutant:2,bones:3,elite:4,boss:5},i=idx[k];b.innerHTML='<span class="atlas-creature-v4"></span>';const e=b.firstElementChild;if(!e)return;e.style.display='block';e.style.width='min(72vw,256px)';e.style.height='min(72vw,256px)';e.style.margin='auto';e.style.backgroundImage='url("'+m[1]+'")';e.style.backgroundRepeat='no-repeat';e.style.setProperty('background-size','400% 600%','important');e.style.setProperty('background-position',((i%4)*100/3)+'% '+(Math.floor(i/4)*100/5)+'%','important');e.style.border='1px solid rgba(45,125,170,.65)';e.style.boxShadow='0 0 22px rgba(0,70,110,.28)'};f.__battleArtRuntimeFix=true;window.updateBattle=f;}
    }catch(e){}};
    patch();setInterval(patch,300);
  };document.head.appendChild(core);
})();
