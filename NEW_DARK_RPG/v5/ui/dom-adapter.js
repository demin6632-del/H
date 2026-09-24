// Chronicles of the Abyss V5 — connected game UI
import { openRoom, resolveRoomAction, finishCurrentCombat } from "../systems/abyss-events.js";
import { createCombatState, playerAttack, playerSkill, playerDefend } from "../systems/combat.js";
import { saveActiveRun, descend, killPlayer } from "../core/game.js";
import { equipItem, unequipItem } from "../systems/items.js";
import { recalculateCharacterStats, upgradeEquipment, forgeCost, SLOTS } from "../systems/equipment.js";
import { sell } from "../systems/merchant.js";
import { buy } from "../systems/merchant.js";
import { healAtTavern, trainCharacter, prepareRun, collectReturnRewards } from "../systems/city-loop.js";
import { checkAchievements, enterArena, resolveArenaWave, ACHIEVEMENTS } from "../systems/endgame.js";

export function createV5UI(game, root) {
  if (!root) throw new Error("V5 UI root is required");
  const ui={game,root};
  let tab="abyss";

  function persist(){ saveActiveRun(game); checkAchievements(game.state); }
  function el(tag="div",cls="",text=""){
    const n=document.createElement(tag);
    if(cls)n.className=cls;
    if(text)n.textContent=text;
    return n;
  }
  function button(parent,label,handler,disabled=false){
    const b=document.createElement("button");
    b.type="button"; b.textContent=label; b.disabled=disabled;
    b.addEventListener("click",handler);
    parent.appendChild(b);
    return b;
  }
  function nav(panel){
    const nav=el("div","v5-tabs");
    const tabs=[
      ["abyss","🌑 Бездна"],["character","👤 Герой"],["inventory","🎒 Инвентарь"],
      ["equipment","⚔️ Снаряжение"],["city","🏙️ Город"],["endgame","🏆 Испытания"]
    ];
    for(const [id,label] of tabs) {
      const b=button(nav,label,()=>{tab=id;render();});
      if(tab===id)b.classList.add("active");
    }
    panel.appendChild(nav);
  }
  function header(panel,title){
    panel.appendChild(el("h3", "", title));
    const info=el("div","info-card");
    const s=game.state;
    info.innerHTML="<div class='info-row'><span>Уровень</span><b>"+s.character.level+"</b></div>"+
      "<div class='info-row'><span>Золото</span><b>"+s.meta.gold+"</b></div>"+
      "<div class='info-row'><span>Глубина</span><b>"+s.abyss.depth+"/7</b></div>";
    panel.appendChild(info);
  }

  function renderAbyss(panel){
    const s=game.state,c=game.combat;
    const info=el("div","info-card");
    info.innerHTML="<div class='info-row'><span>Глубина</span><b>"+s.abyss.depth+"/7</b></div>"+
      "<div class='info-row'><span>Комната</span><b>"+s.abyss.room+"/5</b></div>"+
      "<div class='info-row'><span>Мораль</span><b>"+s.abyss.morale+"</b></div>"+
      "<div class='info-row'><span>Риск</span><b>"+s.abyss.risk+"</b></div>"+
      "<div class='info-row'><span>Внимательность</span><b>"+s.abyss.awareness+"</b></div>";
    panel.appendChild(info);

    if(c){
      panel.appendChild(el("div","log","⚔️ "+c.enemy.name+" — HP "+c.enemy.hp+"/"+c.enemy.maxHp+" | Ваше HP "+c.player.hp+"/"+c.player.maxHp+" MP "+c.player.mp+"/"+c.player.maxMp));
      if(c.log?.length)panel.appendChild(el("div","log",c.log.slice(-6).join("\n")));
      if(c.phase==="player"){
        button(panel,"⚔️ Атаковать",()=>{playerAttack(c);persist();render();});
        button(panel,"🛡️ Защита",()=>{playerDefend(c);persist();render();});
        for(const skill of c.skills||[])button(panel,"✦ "+skill.name+" ("+skill.cost+" MP)",()=>{playerSkill(c,skill.id);persist();render();},c.player.mp<skill.cost);
      } else if(c.phase==="enemy"){
        panel.appendChild(el("div","muted","Враг готовит действие…"));
      }
      if(c.phase==="victory")button(panel,"🏆 Забрать результат",()=>{finishCurrentCombat(game);persist();render();});
      if(c.phase==="defeat")button(panel,"💀 Завершить забег",()=>{killPlayer(game);tab="city";persist();render();});
      return;
    }

    if(s.abyss.returnRewards){
      const r=s.abyss.returnRewards;
      const p=el("div","log","🎁 Награды готовы: "+(r.gold||0)+" золота, "+(r.xp||0)+" XP, предметов: "+(r.items?.length||0));
      panel.appendChild(p);
      button(panel,"🎁 Забрать награды",()=>{collectReturnRewards(game);persist();render();});
    }

    if(s.abyss.pending?.transition){
      button(panel,s.abyss.depth<7?"⬇️ Перейти на следующую глубину":"🏆 Завершить забег",()=>{
        if(s.abyss.depth<7){descend(game);s.meta.bestDepth=Math.max(s.meta.bestDepth,s.abyss.depth);persist();}
        else{s.abyss.active=false;s.abyss.pending=null;persist();}
        render();
      });
      return;
    }

    if(s.abyss.pending?.event){
      const event=s.abyss.pending.event;
      panel.appendChild(el("div","log","◆ "+event.title+"\n"+(event.description||"")));
      for(const action of event.actions||["fight"]){
        button(panel,actionLabel(action),()=>{
          const result=resolveRoomAction(game,action);
          if(result.type==="combat")game.combat=createCombatState(game.state,result.enemy);
          if(result.type==="death")killPlayer(game);
          persist();render();
        });
      }
      return;
    }
    button(panel,"🔎 Исследовать комнату",()=>{openRoom(game);persist();render();});
    panel.appendChild(el("div","muted","Игрок сам решает, когда исследовать комнату и какое действие выбрать."));
  }

  function renderCharacter(panel){
    const s=game.state,c=s.character,st=c.stats||{};
    panel.appendChild(el("div","hero-panel"));
    panel.appendChild(el("h3","", "👤 "+(c.classId||"Класс не выбран")));
    panel.appendChild(el("div","log","Уровень "+c.level+" · XP "+c.xp+"\nHP "+(st.hp||0)+"/"+(st.maxHp||0)+" · MP "+(st.mp||0)+"/"+(st.maxMp||0)+"\nМощь "+(st.power||0)+" · Защита "+(st.defense||0)+" · Скорость "+(st.speed||0)));
    panel.appendChild(el("div","muted","Навыки класса"));
    const skills=c.skills||[];
    if(!skills.length)panel.appendChild(el("div","log","Навыки назначаются системой боя по выбранному классу."));
    for(const sk of skills)panel.appendChild(el("div","item","✦ "+sk));
  }

  function renderInventory(panel){
    const inv=game.state.inventory;
    panel.appendChild(el("div","log","Предметов: "+inv.reduce((n,x)=>n+(x.stackable?x.quantity:1),0)+"/24"));
    if(!inv.length){panel.appendChild(el("div","muted","Инвентарь пуст."));return;}
    for(const item of inv){
      const row=el("div","item");
      const equipped=Object.values(game.state.character.equipment||{}).includes(item.instanceId);
      const title=el("div","",item.name+" · "+(item.rarity||"common")+(item.stackable?" ×"+item.quantity:""));
      const desc=el("small","",item.slot+(equipped?" · ЭКИПИРОВАНО":""));
      title.appendChild(desc);row.appendChild(title);
      if(!item.stackable && item.slot!=="consumable"){
        if(equipped){
          button(row,"Снять",()=>{unequipItem(game.state,item.slot);recalculateCharacterStats(game.state);persist();render();});
        }else{
          button(row,"Экипировать",()=>{equipItem(game.state,item.instanceId);recalculateCharacterStats(game.state);persist();render();});
        }
      }
      button(row,"Продать",()=>{sell(game.state,item.instanceId);persist();render();});
      panel.appendChild(row);
    }
  }

  function renderEquipment(panel){
    const eq=game.state.character.equipment||{};
    panel.appendChild(el("div","log","Слоты: оружие, броня, шлем, перчатки, сапоги, амулет, кольцо. Экипировка выбирается вручную."));
    for(const slot of SLOTS){
      const id=eq[slot];
      const item=id?game.state.inventory.find(x=>x.instanceId===id):null;
      const row=el("div","item");
      row.innerHTML="<b>"+slot+"</b><span>"+(item?item.name+" · +"+(item.upgrade||0):"Пусто")+"</span>";
      if(item){
        button(row,"Снять",()=>{unequipItem(game.state,slot);recalculateCharacterStats(game.state);persist();render();});
        button(row,"Улучшить",()=>{
          try{upgradeEquipment(game.state,item.instanceId,forgeCost(item));persist();render();}catch(e){alert(e.message);}
        },(item.upgrade||0)>=10);
      }
      panel.appendChild(row);
    }
  }

  function renderCity(panel){
    const s=game.state;
    panel.appendChild(el("div","log","Город — подготовка между забегами. Здесь можно восстановиться, обучиться, пересчитать экипировку и забрать трофеи."));
    button(panel,"🍺 Таверна — восстановить HP/MP (25 🪙)",()=>{healAtTavern(game);persist();render();},s.meta.gold<25);
    button(panel,"📚 Обучение — +75 XP (50 🪙)",()=>{trainCharacter(game);persist();render();},s.meta.gold<50);
    button(panel,"⚒️ Подготовить персонажа",()=>{prepareRun(game);persist();render();});
    if(s.abyss.returnRewards)button(panel,"🎁 Забрать трофеи",()=>{collectReturnRewards(game);persist();render();});
    panel.appendChild(el("div","muted","Торговля и контракты"));
    const shop=[["healing_potion","🧪 Зелье лечения"],["mana_potion","🔵 Зелье маны"],["abyss_key","🗝️ Ключ Бездны"],["iron_shard","⚙️ Железный осколок"]];
    for(const [id,label] of shop){
      button(panel,label,()=>{const r=buy(game.state,id,1);if(!r.ok)alert("Не удалось купить: "+r.reason);persist();render();});
    }
  }

  function renderEndgame(panel){
    const s=game.state;
    panel.appendChild(el("div","log","Испытания открываются по мере прохождения Бездны. Лучший результат арены: "+(s.endgame.arena?.bestWave||0)+" волн."));
    const arena=enterArena(game);
    button(panel,arena.ok?"⚔️ Начать арену":"🔒 Арена закрыта до глубины 3",()=>{
      const a=enterArena(game);
      if(a.ok){game.arena=a;render();}
    },!arena.ok);
    if(game.arena){
      panel.appendChild(el("div","log","Волна "+game.arena.wave+" / 20"));
      button(panel,"Победить волну",()=>{resolveArenaWave(game,true);persist();render();});
      button(panel,"Завершить испытание",()=>{resolveArenaWave(game,false);persist();render();});
    }
    panel.appendChild(el("div","muted","Достижения"));
    for(const [id,a] of Object.entries(ACHIEVEMENTS)){
      const done=!!s.endgame.achievements?.[id];
      panel.appendChild(el("div","item",(done?"🏆 ":"🔒 ")+a.name+" — "+(done?"получено":"условие: "+a.target)));
    }
  }

  function render(){
    root.innerHTML="";
    const panel=el("section","panel v5-panel");
    nav(panel);
    if(tab==="abyss"){header(panel,"🌑 Бездна");renderAbyss(panel);}
    if(tab==="character"){header(panel,"👤 Герой");renderCharacter(panel);}
    if(tab==="inventory"){header(panel,"🎒 Инвентарь");renderInventory(panel);}
    if(tab==="equipment"){header(panel,"⚔️ Снаряжение");renderEquipment(panel);}
    if(tab==="city"){header(panel,"🏙️ Город");renderCity(panel);}
    if(tab==="endgame"){header(panel,"🏆 Испытания");renderEndgame(panel);}
    root.appendChild(panel);
  }

  function actionLabel(action){
    return({inspect:"🔎 Осмотреть",disarm:"🧰 Обезвредить",rush:"🏃 Пройти напролом",open:"🎁 Открыть",leave:"🚶 Уйти",left:"⬅️ Налево",straight:"⬆️ Прямо",right:"➡️ Направо",fight:"⚔️ Сражаться",evade:"💨 Уклониться",pray:"🛐 Помолиться",search:"🔍 Искать"})[action]||action;
  }

  render();
  return {render};
}
