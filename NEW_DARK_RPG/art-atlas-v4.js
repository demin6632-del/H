/* ART-ATLAS-V4-RUNTIME — сохраняет оригинальный V4-атлас и накладывает только технические исправления. */
(function(){
  if(window.__ART_ATLAS_V4_RUNTIME)return;
  window.__ART_ATLAS_V4_RUNTIME=true;
  const core=document.createElement('script');core.src='art-atlas-v4-core.js';
  core.onload=function(){
    const patch=function(){try{
      const style=document.createElement('style');
      style.textContent='.scene.battle:before,.scene.battle:after{display:none!important}.scene.battle{overflow:hidden!important}.enemy-art{filter:none!important;background:transparent!important;border:0!important;box-shadow:none!important}.enemy-art .atlas-creature-v4{filter:drop-shadow(0 8px 12px rgba(0,0,0,.65));}';
      if(!document.getElementById('art-v4-battle-clean')){style.id='art-v4-battle-clean';document.head.appendChild(style)}

      if(typeof restoreBest==='function'&&!restoreBest.__fixed){const f=function(){};f.__fixed=true;window.restoreBest=f;}
      if(typeof hasSave==='function'&&!hasSave.__fixed){const f=function(){return !!localStorage.getItem(saveKey)||!!localStorage.getItem(saveKey+'_backup')};f.__fixed=true;window.hasSave=f;}
      if(typeof heroRefNav==='function'&&!heroRefNav.__fixed){const f=function(id){if(!screens.includes(id))return;if(id==='hero')renderHero();if(id==='inventory'&&typeof renderInventory==='function')renderInventory();if(id==='equipment'&&typeof renderEquipment==='function')renderEquipment();if(id==='stats')renderStats();if(id==='skills')renderSkills();setScreen(id)};f.__fixed=true;window.heroRefNav=f;}
      if(typeof start==='function'&&!start.__fixed){const old=start;const f=function(className){try{abyssKeyCaches={};window.abyssKeyCaches=abyssKeyCaches;localStorage.removeItem('abyss_key_caches');localStorage.removeItem('abyss_gear')}catch(e){}return old.apply(this,arguments)};f.__fixed=true;window.start=f;}
      if(typeof save==='function'&&!save.__fixed){const old=save;const f=function(){try{if(typeof ensureGear==='function')ensureGear();localStorage.setItem('abyss_gear',JSON.stringify(hero.gear));localStorage.setItem('abyss_key_caches',JSON.stringify(abyssKeyCaches||{}))}catch(e){}return old.apply(this,arguments)};f.__fixed=true;window.save=f;}

      /* ABYSS-DEPTH-PROGRESS-FIX-V5
         При возврате на уже открытую глубину восстанавливаем непрерывный
         прогресс комнат вместо принудительного возврата к комнате 1. */
      function syncAbyssDepthProgress(){
        try{
          if(typeof abyssFloor==='undefined'||typeof state==='undefined'||!state||!state.rooms)return;
          const d=Math.max(1,Number(abyssFloor||1));
          const max=typeof ROOMS_PER_FLOOR==='number'?ROOMS_PER_FLOOR:5;
          let completed=0;
          for(let r=1;r<=max;r++){
            const k=typeof roomKey==='function'?roomKey(d,r):(d+':'+r);
            const room=state.rooms[k];
            if(room&&room.visited)completed=r;else break;
          }
          abyssRoom=Math.max(0,Math.min(max,completed));
          if(state.pending&&Number(state.pending.depth)===d&&Number(state.pending.room)<=completed)state.pending=null;
        }catch(e){}
      }
      if(typeof renderDynamic==='function'&&!renderDynamic.__abyssDepthProgressFix){
        const oldRenderDynamic=renderDynamic;
        const f=function(){
          syncAbyssDepthProgress();
          const r=oldRenderDynamic.apply(this,arguments);
          syncAbyssDepthProgress();
          return r;
        };
        f.__abyssDepthProgressFix=true;
        window.renderDynamic=f;
      }
      if(typeof selectAbyssDepth==='function'&&!selectAbyssDepth.__abyssDepthProgressFix){
        const oldSelectAbyssDepth=selectAbyssDepth;
        const f=function(){
          const r=oldSelectAbyssDepth.apply(this,arguments);
          syncAbyssDepthProgress();
          if(typeof saveState==='function')saveState();
          return r;
        };
        f.__abyssDepthProgressFix=true;
        window.selectAbyssDepth=f;
      }

      if(typeof updateBattle==='function'&&!updateBattle.__battleArtRuntimeFix){
        const old=updateBattle;
        const f=function(){
          old.apply(this,arguments);
          const b=document.getElementById('enemyArt');
          if(!b)return;
          const scene=b.closest('.scene.battle');
          if(scene){scene.style.overflow='hidden';scene.classList.add('art-v4-battle-clean');}
          const bg=document.querySelector('.scene.art-v4-scene')?.style.backgroundImage||'';
          const m=bg.match(/data:image\/webp;base64,[^\")]+/);
          if(!m)return;

          let k='shadow';
          if(typeof enemy!=='undefined'&&enemy){
            if(enemy.isBoss)k='boss';
            else if(enemy.isElite)k='elite';
            else k=({'Теневой зверь':'shadow','Заражённый охотник':'hunter','Мутант пустоши':'mutant','Пожиратель костей':'bones'})[enemy.name]||'shadow';
          }
          const idx={shadow:0,hunter:1,mutant:2,bones:3,elite:4,boss:5},i=idx[k];

          const hpBox=document.getElementById('enemyBar')?.parentElement;
          b.innerHTML='';
          b.style.position='absolute';
          b.style.left='50%';
          b.style.top='50%';
          b.style.transform='translate(-50%,-50%)';
          b.style.width='min(78vw,300px)';
          b.style.height='min(78vw,300px)';
          b.style.margin='0';
          b.style.padding='0';
          b.style.zIndex='3';
          b.style.display='block';
          b.style.background='transparent';
          b.style.border='0';
          b.style.boxShadow='none';
          b.style.filter='none';
          b.style.overflow='visible';
          b.style.mixBlendMode='normal';

          const e=document.createElement('span');
          e.className='atlas-creature-v4';
          e.style.display='block';
          e.style.width='100%';
          e.style.height='100%';
          e.style.margin='0';
          e.style.backgroundColor='transparent';
          if(window.renderV4Tile) window.renderV4Tile(e,k,280,280);
          else{
            e.style.backgroundImage='url("'+m[1]+'")';
            e.style.backgroundRepeat='no-repeat';
            e.style.setProperty('background-size','400% 600%','important');
            e.style.setProperty('background-position',((i%4)*100/3)+'% '+(Math.floor(i/4)*100/5)+'%','important');
          }
          e.style.border='0';
          e.style.boxShadow='none';
          e.style.filter='drop-shadow(0 8px 12px rgba(0,0,0,.72))';e.style.mixBlendMode='screen';
          b.appendChild(e);
          /* Центрируем именно видимую фигуру: чёрный фон атласа убирается режимом screen. */
          e.style.transform='translateY(7%)';
        };
        f.__battleArtRuntimeFix=true;
        f.__artV4=true;
        window.updateBattle=f;
      }
    }catch(e){}};
    patch();setTimeout(patch,250);
  };
  document.head.appendChild(core);
})();
