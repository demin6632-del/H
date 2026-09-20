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

      /* POTION-STACK-V1
         Только зелья здоровья и маны объединяются в один слот.
         Остальные предметы инвентаря работают без изменений. */
      const POTION_STACK_TYPES=['hp','mp'];
      function isStackablePotion(raw){const x=typeof itemInfo==='function'?itemInfo(raw):raw;return !!(x&&x.type==='consumable'&&POTION_STACK_TYPES.includes(String(x.effect||'')));}
      function potionKey(raw){const x=typeof itemInfo==='function'?itemInfo(raw):raw;return String(x&&x.effect||'');}
      function normalizePotionStacks(){if(!hero||!Array.isArray(hero.items))return;const first={};for(let i=hero.items.length-1;i>=0;i--){const raw=hero.items[i];if(!isStackablePotion(raw))continue;const key=potionKey(raw),q=Math.max(1,Number(raw&&raw.quantity||1));if(first[key]===undefined){raw.quantity=q;first[key]=i}else{hero.items[first[key]].quantity=Math.max(1,Number(hero.items[first[key]].quantity||1))+q;hero.items.splice(i,1);if(first[key]>i)first[key]--;}}}
      const __addItemToInventoryPotion=addItemToInventory;
      addItemToInventory=function(item){if(isStackablePotion(item)){normalizePotionStacks();const key=potionKey(item),existing=hero.items.find(raw=>isStackablePotion(raw)&&potionKey(raw)===key);if(existing){existing.quantity=Math.max(1,Number(existing.quantity||1))+Math.max(1,Number(item.quantity||1));return true}if(!inventoryHasSpace())return false;item.quantity=Math.max(1,Number(item.quantity||1));hero.items.push(item);return true}return __addItemToInventoryPotion.apply(this,arguments)};
      const __buyItemPotion=buyItem;
      buyItem=function(id){
        const item=shopItems.find(x=>x.id===id);
        if(item&&(item.id==='hp'||item.id==='mp')){
          normalizePotionStacks();
          if(getGold()<item.price){sfx('error');if(el('out'))el('out').innerHTML='<span class="red">Недостаточно золота.</span>';return}
          if(!inventoryHasSpace()&&!hero.items.some(raw=>isStackablePotion(raw)&&potionKey(raw)===String(item.id))){sfx('error');if(el('out'))el('out').innerHTML='<span class="red">Инвентарь заполнен (24/24).</span>';return}
          hero.gold=getGold()-item.price;
          const added=addItemToInventory({name:item.name,type:'consumable',effect:item.id==='hp'?'hp':'mp',icon:item.icon});
          if(!added){hero.gold+=item.price;sfx('error');if(el('out'))el('out').innerHTML='<span class="red">Инвентарь заполнен (24/24).</span>';return}
          save();update();sfx('buy');logEvent('МАГАЗИН','Куплено: '+item.name+' за '+item.price+' золота.');
          if(el('out'))el('out').innerHTML='<span class="green">Куплено: '+item.name+'. В стаке: '+(hero.items.find(raw=>isStackablePotion(raw)&&potionKey(raw)===(item.id==='hp'?'hp':'mp'))?.quantity||1)+'.</span>';
          shopTab(shopCategory);
          return;
        }
        return __buyItemPotion.apply(this,arguments);
      };
      const __useInventoryItemPotion=useInventoryItem;
      useInventoryItem=function(index){normalizePotionStacks();const raw=hero.items[index];if(isStackablePotion(raw)){const item=itemInfo(raw);if(item.effect==='hp')hero.hp=Math.min(hero.maxHp,hero.hp+50);if(item.effect==='mp')hero.energy=Math.min(hero.maxEnergy,hero.energy+30);raw.quantity=Math.max(0,Number(raw.quantity||1)-1);if(raw.quantity<=0)hero.items.splice(index,1);sfx('buy');logEvent('ПРЕДМЕТ',item.name+' использовано. Осталось: '+(raw.quantity>0?raw.quantity:0)+'.');save();update();renderInventory();const fromBattle=screenHistory[screenHistory.length-1]==='inventory'&&screenHistory[screenHistory.length-2]==='battle';if(fromBattle){goBack();enemyTurn()}return}return __useInventoryItemPotion.apply(this,arguments)};
      const __renderInventoryPotion=renderInventory;
      renderInventory=function(){normalizePotionStacks();__renderInventoryPotion.apply(this,arguments);const list=el('inventoryList');if(!list)return;list.querySelectorAll('button[onclick*="useInventoryItem("]').forEach(btn=>{const m=String(btn.getAttribute('onclick')||'').match(/useInventoryItem\((\d+)\)/);if(!m)return;const index=Number(m[1]),raw=hero.items[index];if(!isStackablePotion(raw)||Number(raw.quantity||1)<=1)return;const row=btn.closest('.item'),nameBox=row&&row.children&&row.children[1];if(!nameBox)return;const badge=document.createElement('span');badge.textContent=' ×'+Number(raw.quantity);badge.style.cssText='color:#e7b34a;font-weight:bold;margin-left:4px';nameBox.firstChild&&nameBox.firstChild.parentNode.insertBefore(badge,nameBox.firstChild.nextSibling)})};
      window.POTION_STACK_V1='POTION-STACK-V1';

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

      /* MYSTERY-KEY-STACK-V1
         Таинственные ключи объединяются в один стак.
         Остальные предметы не изменяются. */
      setTimeout(function(){
        try{
          function isMysteryKey(raw){return !!(raw&&String(raw.name||'')==='Таинственный ключ');}
          function normalizeMysteryKeys(){
            if(!hero||!Array.isArray(hero.items))return;
            let first=-1,total=0;
            for(let i=0;i<hero.items.length;i++){
              if(!isMysteryKey(hero.items[i]))continue;
              if(first<0){first=i;total=Math.max(1,Number(hero.items[i].quantity||1));hero.items[i].quantity=total}
              else{total+=Math.max(1,Number(hero.items[i].quantity||1));hero.items.splice(i,1);i--;}
            }
            if(first>=0)hero.items[first].quantity=total;
          }
          normalizeMysteryKeys();

          const __addItemWithKeys=addItemToInventory;
          addItemToInventory=function(item){
            if(isMysteryKey(item)){
              normalizeMysteryKeys();
              const existing=hero.items.find(isMysteryKey);
              if(existing){existing.quantity=Math.max(1,Number(existing.quantity||1))+Math.max(1,Number(item.quantity||1));return true;}
              if(!inventoryHasSpace())return false;
              item.quantity=Math.max(1,Number(item.quantity||1));
              hero.items.push(item);
              return true;
            }
            return __addItemWithKeys.apply(this,arguments);
          };

          const __buyKeyStack=buyKey;
          buyKey=function(){
            normalizeMysteryKeys();
            const existing=hero.items.find(isMysteryKey);
            if(existing){
              const price=75;
              if(getGold()<price){sfx('error');if(el('out'))el('out').innerHTML='<span class="red">Недостаточно золота.</span>';return;}
              hero.gold-=price;
              existing.quantity=Math.max(1,Number(existing.quantity||1))+1;
              save();update();sfx('buy');logEvent('МАГАЗИН','Куплен Таинственный ключ. В стаке: '+existing.quantity+'.');
              if(el('out'))el('out').innerHTML='<span class="green">Таинственный ключ ×'+existing.quantity+'.</span>';
              if(typeof shopTab==='function')shopTab('other');
              return;
            }
            return __buyKeyStack.apply(this,arguments);
          };

          const __useKeyStack=useInventoryItem;
          useInventoryItem=function(index){
            normalizeMysteryKeys();
            const raw=hero.items[index];
            if(isMysteryKey(raw)){
              const count=Math.max(1,Number(raw.quantity||1));
              raw.quantity=1;
              const result=__useKeyStack.apply(this,arguments);
              if(count>1){
                hero.items.splice(Math.min(index,hero.items.length),0,{name:'Таинственный ключ',type:'other',icon:'🔑',quantity:count-1});
                save();update();renderInventory();
              }
              return result;
            }
            return __useKeyStack.apply(this,arguments);
          };

          const __renderInventoryKeys=renderInventory;
          renderInventory=function(){
            normalizeMysteryKeys();
            __renderInventoryKeys.apply(this,arguments);
            const list=el('inventoryList'); if(!list)return;
            list.querySelectorAll('button[onclick*="useInventoryItem("]').forEach(btn=>{
              const m=String(btn.getAttribute('onclick')||'').match(/useInventoryItem\((\d+)\)/);
              if(!m)return;
              const raw=hero.items[Number(m[1])];
              if(!isMysteryKey(raw)||Number(raw.quantity||1)<=1)return;
              const row=btn.closest('.item'),nameBox=row&&row.children&&row.children[1];
              if(!nameBox)return;
              const badge=document.createElement('span');
              badge.textContent=' ×'+Number(raw.quantity);
              badge.style.cssText='color:#e7b34a;font-weight:bold;margin-left:4px';
              nameBox.appendChild(badge);
            });
          };
          window.MYSTERY_KEY_STACK_V1='MYSTERY-KEY-STACK-V1';
          save();
        }catch(e){console.warn('MYSTERY-KEY-STACK-V1',e);}
      },0);


      /* STACK-SELL-FIX-V1
         Для стакуемых предметов: цена продажи в инвентаре показывает стоимость всего стака,
         а кнопка продаёт только 1 экземпляр. Остальные предметы не изменяются. */
      setTimeout(function(){try{
        const __sellStackFix=window.sellInventoryItem;
        if(typeof __sellStackFix==='function'&&!__sellStackFix.__stackSellFix){
          const f=function(index,traderSale){
            const raw=hero&&Array.isArray(hero.items)?hero.items[index]:null;
            const q=raw?Math.max(1,Number(raw.quantity||1)):1;
            if(raw&&q>1){
              const unit=traderSale&&typeof window.sellCurrentPrice==='function'?Math.max(1,Number(window.sellCurrentPrice(raw)||0)):Math.max(1,Number(window.sellPrice(raw)||0));
              const name=(typeof itemInfo==='function'&&itemInfo(raw)||{}).name||raw.name||'Предмет';
              raw.quantity=q-1;hero.gold=Math.max(0,Number(hero.gold||0)+unit);save();update();
              if(typeof updateHud==='function')updateHud();if(typeof renderInventory==='function')renderInventory();if(typeof renderHero==='function')renderHero();if(typeof window.renderAbyssTraderSell==='function')window.renderAbyssTraderSell();
              sfx('buy');logEvent('ТОРГОВЕЦ','Продан 1: '+name+' за '+unit+' золота. Осталось: '+raw.quantity+'.');
              if(el('out'))el('out').innerHTML='<span class="green">Продан 1: '+name+' за '+unit+' золота. В стаке осталось: '+raw.quantity+'.</span>';return;
            }
            return __sellStackFix.apply(this,arguments);
          };f.__stackSellFix=true;window.sellInventoryItem=f;
        }
        const __renderStackSell=renderInventory;
        if(typeof __renderStackSell==='function'&&!__renderStackSell.__stackSellPriceFix){
          const f=function(){__renderStackSell.apply(this,arguments);const list=el('inventoryList');if(!list||!hero||!Array.isArray(hero.items))return;list.querySelectorAll('[data-base-sell-index]').forEach(btn=>{const index=Number(btn.dataset.baseSellIndex),raw=hero.items[index],q=raw?Math.max(1,Number(raw.quantity||1)):1;if(!raw||q<=1)return;const unit=Math.max(1,Number(typeof window.sellPrice==='function'?window.sellPrice(raw):0));btn.textContent='Продать 1 · '+unit+' 🪙  (всего: '+(unit*q)+' 🪙)';});};f.__stackSellPriceFix=true;window.renderInventory=f;
        }
        window.STACK_SELL_FIX_V1='STACK-SELL-FIX-V1';
      }catch(e){console.warn('STACK-SELL-FIX-V1',e);}},100);

      /* ABYSS-DEPTH7-ROOM-RECOVERY-V1
         Восстановление застрявшего состояния комнаты на глубине 7.
         Не пропускает непроигранную комнату: исправляет только устаревший
         pending/visited и приводит номера depth/room к числам. */
      setTimeout(function(){
        try{
          if(typeof renderDynamic!=='function'||typeof getRoom!=='function'||typeof state==='undefined'||!state)return;
          const oldRender=renderDynamic;
          if(oldRender.__depth7RoomRecovery)return;
          const f=function(){
            try{
              const d=Number(abyssFloor||1);
              if(d===7){
                if(state.pending&&typeof state.pending==='object'){
                  state.pending.depth=Number(state.pending.depth);
                  state.pending.room=Number(state.pending.room);
                }
                let completed=0;
                for(let r=1;r<=ROOMS_PER_FLOOR;r++){
                  const rr=getRoom(d,r);
                  if(rr&&rr.visited)completed=r;else break;
                }
                abyssRoom=Math.max(0,Math.min(ROOMS_PER_FLOOR,completed));
                const current=Math.max(1,Math.min(ROOMS_PER_FLOOR,Number(abyssRoom)+1));
                const room=getRoom(d,current);
                if(state.pending){
                  const pd=Number(state.pending.depth),pr=Number(state.pending.room);
                  if(pd!==d||pr!==current||(room&&room.visited)){
                    state.pending=null;
                    if(typeof saveState==='function')saveState();
                  }
                }
              }
            }catch(e){}
            return oldRender.apply(this,arguments);
          };
          f.__depth7RoomRecovery=true;
          window.renderDynamic=f;
        }catch(e){console.warn('ABYSS-DEPTH7-ROOM-RECOVERY-V1',e);}
      },350);

