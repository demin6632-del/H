// Chronicles of the Abyss V5 — DOM adapter
// This adapter owns presentation only; game systems remain the source of truth.
import { openRoom, resolveRoomAction, finishCurrentCombat } from "../systems/abyss-events.js";
import { playerAttack, playerSkill, playerDefend } from "../systems/combat.js";

export function createV5UI(game, root) {
  if (!root) throw new Error("V5 UI root is required");
  const ui={game,root};

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
        "  |  Враг: "+c.enemy.hp+"/"+c.enemy.maxHp;
      panel.appendChild(hp);
      addButton(panel,"⚔️ Атаковать",()=>{ playerAttack(c); render(); });
      addButton(panel,"🛡️ Защита",()=>{ playerDefend(c); render(); });
      for (const skill of c.skills||[]) addButton(panel,"🔮 "+skill.name+" ("+skill.cost+" MP)",()=>{ playerSkill(c,skill.id); render(); });
      if (["victory","defeat"].includes(c.phase)) addButton(panel,c.phase==="victory"?"🏆 Забрать результат":"💀 Завершить",()=>{ finishCurrentCombat(game); render(); });
    } else if (s.abyss.pending?.event) {
      const event=s.abyss.pending.event;
      const text=document.createElement("div");
      text.className="log";
      text.textContent=event.title;
      panel.appendChild(text);
      for (const action of event.actions||["fight"]) addButton(panel,actionLabel(action),()=>{ resolveRoomAction(game,action); render(); });
    } else {
      addButton(panel,"🔎 Исследовать комнату",()=>{ openRoom(game); render(); });
    }
    root.appendChild(panel);
  }

  function addButton(parent,label,handler) {
    const b=document.createElement("button");
    b.type="button"; b.textContent=label; b.addEventListener("click",handler);
    parent.appendChild(b);
  }
  function actionLabel(action) {
    return ({inspect:"🔎 Осмотреть",disarm:"🧰 Обезвредить",rush:"🏃 Пройти напролом",open:"🎁 Открыть",leave:"🚶 Уйти",left:"⬅️ Налево",straight:"⬆️ Прямо",right:"➡️ Направо",fight:"⚔️ Сражаться",evade:"💨 Уклониться",pray:"🛐 Помолиться",search:"🔍 Искать"})[action] || action;
  }
  render();
  return {render};
}
