// Chronicles of the Abyss V5 — DOM adapter
import { openRoom, resolveRoomAction, finishCurrentCombat } from "../systems/abyss-events.js";
import { createCombatState, playerAttack, playerSkill, playerDefend } from "../systems/combat.js";
import { saveActiveRun, descend, killPlayer } from "../core/game.js";

export function createV5UI(game, root) {
  if (!root) throw new Error("V5 UI root is required");
  const ui={game,root};

  function persist(){ saveActiveRun(game); }

  function render() {
    const s=game.state, c=game.combat;
    root.innerHTML="";
    const panel=document.createElement("section");
    panel.className="panel v5-panel";
    const title=document.createElement("h3");
    title.textContent=c ? "⚔️ Бой" : "🌑 Бездна";
    panel.appendChild(title);

    const info=document.createElement("div");
    info.className="info-card";
    info.innerHTML="<div class='info-row'><span>Глубина</span><b>"+s.abyss.depth+"/7</b></div>"+
      "<div class='info-row'><span>Комната</span><b>"+s.abyss.room+"/5</b></div>"+
      "<div class='info-row'><span>Золото</span><b>"+s.meta.gold+"</b></div>";
    panel.appendChild(info);

    if (c) {
      const hp=document.createElement("div");
      hp.className="log";
      hp.textContent="HP "+c.player.hp+"/"+c.player.maxHp+"  MP "+c.player.mp+"/"+c.player.maxMp+
        " | Враг: "+c.enemy.hp+"/"+c.enemy.maxHp;
      panel.appendChild(hp);
      if (c.log?.length) {
        const log=document.createElement("div"); log.className="log";
        log.textContent=c.log.slice(-5).join("\n"); panel.appendChild(log);
      }
      if (c.phase==="player") {
        addButton(panel,"⚔️ Атаковать",()=>{ playerAttack(c); persist(); render(); });
        addButton(panel,"🛡️ Защита",()=>{ playerDefend(c); persist(); render(); });
        for (const skill of c.skills||[]) addButton(panel,"🔮 "+skill.name+" ("+skill.cost+" MP)",()=>{
          playerSkill(c,skill.id); persist(); render();
        });
      }
      if (["victory","defeat"].includes(c.phase)) addButton(panel,c.phase==="victory"?"🏆 Забрать результат":"💀 Завершить",()=>{
        if(c.phase==="defeat") killPlayer(game); else finishCurrentCombat(game); persist(); render();
      });
    } else if (s.abyss.pending?.transition) {
      addButton(panel,s.abyss.depth<7?"⬇️ Перейти на следующую глубину":"🏆 Завершить забег",()=>{
        if(s.abyss.depth<7){ descend(game); s.meta.bestDepth=Math.max(s.meta.bestDepth,s.abyss.depth); persist(); }
        else { s.abyss.active=false; s.abyss.pending=null; persist(); }
        render();
      });
    } else if (s.abyss.pending?.event) {
      const event=s.abyss.pending.event;
      const text=document.createElement("div"); text.className="log"; text.textContent=event.title; panel.appendChild(text);
      for (const action of event.actions||["fight"]) addButton(panel,actionLabel(action),()=>{
        const result=resolveRoomAction(game,action);
        if(result.type==="combat") game.combat=createCombatState(game.state,result.enemy);
        persist(); render();
      });
    } else {
      addButton(panel,"🔎 Исследовать комнату",()=>{ openRoom(game); persist(); render(); });
    }
    root.appendChild(panel);
  }

  function addButton(parent,label,handler){const b=document.createElement("button");b.type="button";b.textContent=label;b.addEventListener("click",handler);parent.appendChild(b);}
  function actionLabel(action){return({inspect:"🔎 Осмотреть",disarm:"🧰 Обезвредить",rush:"🏃 Пройти напролом",open:"🎁 Открыть",leave:"🚶 Уйти",left:"⬅️ Налево",straight:"⬆️ Прямо",right:"➡️ Направо",fight:"⚔️ Сражаться",evade:"💨 Уклониться",pray:"🛐 Помолиться",search:"🔍 Искать"})[action]||action;}
  render();
  return {render};
}
