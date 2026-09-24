// Chronicles of the Abyss V5 — integration bridge
import { createGame, continueRun, resetGame, saveActiveRun } from "./core/game.js";
import { selectClass } from "./systems/progression.js";
import { skillsForClass } from "./systems/skills.js";
import { recalculateCharacterStats } from "./systems/equipment.js";
import { createV5UI } from "./ui/dom-adapter.js";

let game = createGame();
let ui = null;

function activateV5Screen() {
  document.querySelectorAll(".screen").forEach(x => x.classList.add("hidden"));
  document.getElementById("menu")?.classList.add("hidden");
  document.getElementById("abyss")?.classList.remove("hidden");
}

function root() {
  let host = document.getElementById("abyss");
  if (!host) {
    host = document.createElement("div");
    host.id = "abyss";
    document.getElementById("game")?.appendChild(host);
  }
  let mount = document.getElementById("v5AbyssMount");
  if (!mount) {
    mount = document.createElement("div");
    mount.id = "v5AbyssMount";
    host.appendChild(mount);
  }
  return mount;
}

function chooseClassIfNeeded() {
  if (game.state.character.classId) return;
  const mount = root();
  mount.innerHTML = "";
  const panel = document.createElement("section");
  panel.className = "panel";
  panel.innerHTML = "<h3>👤 Выберите класс</h3><div class='muted' style='text-align:center;margin:8px 0'>Выбор определяет характеристики и навыки персонажа.</div>";
  const classes = [
    ["vanguard","🛡️ Страж","Высокая выносливость и защита"],
    ["hunter","🏹 Охотник","Скорость и точные удары"],
    ["occultist","🔮 Оккультист","Сила и мистические навыки"]
  ];
  for (const [id,name,desc] of classes) {
    const b=document.createElement("button");
    b.textContent=name+" — "+desc;
    b.onclick=()=>{selectClass(game.state,id);game.state.character.skills=skillsForClass(id).map(x=>x.id);recalculateCharacterStats(game.state);game.state.abyss.active=true;saveActiveRun(game);mount.innerHTML="";ui=createV5UI(game,mount);};
    panel.appendChild(b);
  }
  mount.appendChild(panel);
}

function showV5() {
  const restored=continueRun(game);
  if (!restored.ok) {
    game=createGame();
  }
  const mount=root();
  game.state.abyss.active = true;
  if (!game.state.character.classId) {
    chooseClassIfNeeded();
    return;
  }
  ui=createV5UI(game,mount);
  ui.render();
}

function newV5Game() {
  game=resetGame(game);
  const mount=root();
  mount.innerHTML="";
  chooseClassIfNeeded();
}

window.showClasses=newV5Game;
window.continueGame=showV5;
window.showAbyss=showV5;
window.startAbyssExpedition=showV5;
window.__COA_V5_NEW_GAME=newV5Game;
window.__COA_V5_GAME=()=>game;
