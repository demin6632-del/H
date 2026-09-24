// Chronicles of the Abyss V5 — endgame systems
import { addGold } from "./economy.js";
import { applyXp } from "./progression.js";
import { createEnemy } from "./enemies.js";
import { createCombatState } from "./combat.js";

export const ARENA_WAVES=20;

export const ACHIEVEMENTS=Object.freeze({
  first_depth:{name:"Первый спуск",type:"depth",target:1,reward:{gold:25,xp:25}},
  deep_walker:{name:"Глубокий след",type:"depth",target:7,reward:{gold:150,xp:150}},
  survivor:{name:"Выживший",type:"deaths",target:5,reward:{gold:100,xp:100}},
  collector:{name:"Собиратель",type:"items",target:10,reward:{gold:100,xp:100}}
});

export function unlockAchievement(state,id) {
  const a=ACHIEVEMENTS[id];
  if (!a) return {ok:false,reason:"unknown_achievement"};
  state.endgame.achievements ||= {};
  if (state.endgame.achievements[id]) return {ok:false,reason:"already_unlocked"};
  state.endgame.achievements[id]={unlockedAt:Date.now()};
  addGold(state,a.reward.gold||0);
  applyXp(state,a.reward.xp||0);
  return {ok:true,achievement:a};
}

export function checkAchievements(state) {
  const values={
    depth:state.meta.bestDepth||1,
    deaths:state.meta.deaths||0,
    items:state.inventory.reduce((n,x)=>n+(x.stackable?x.quantity:1),0)
  };
  const unlocked=[];
  for (const [id,a] of Object.entries(ACHIEVEMENTS)) {
    if (values[a.type] >= a.target && !state.endgame.achievements?.[id]) {
      const result=unlockAchievement(state,id);
      if (result.ok) unlocked.push(id);
    }
  }
  return unlocked;
}

export function enterArena(game) {
  const state=game.state;
  if ((state.meta.bestDepth||1)<3) return {ok:false,reason:"arena_locked"};
  game.arena={wave:1,bestWave:state.endgame.arena?.bestWave||0,hp:state.character.stats.maxHp||1};
  return {ok:true,wave:1};
}

export function startArenaWave(game) {
  if (!game.arena) return {ok:false,reason:"arena_not_started"};
  if (game.combat) return {ok:false,reason:"combat_active"};
  const wave=game.arena.wave;
  const depth=Math.min(7,3+Math.floor((wave-1)/4));
  const elite=wave%5===0;
  const enemy=createEnemy(depth,Math.random,elite);
  enemy.name="Арена: "+enemy.name;
  game.combat=createCombatState(game.state.character,enemy);
  game.arena.combatWave=wave;
  return {ok:true,wave,enemy};
}

export function resolveArenaWave(game,victory=true) {
  if (!game.arena) return {ok:false,reason:"arena_not_started"};
  if (!victory) {
    game.state.endgame.arena.bestWave=Math.max(game.state.endgame.arena.bestWave||0,game.arena.wave-1);
    game.arena=null;
    return {ok:true,finished:true};
  }
  const wave=game.arena.wave;
  game.combat=null;
  addGold(game.state,20+wave*8);
  applyXp(game.state,25+wave*10);
  game.state.endgame.arena.bestWave=Math.max(game.state.endgame.arena.bestWave||0,wave);
  if (wave>=ARENA_WAVES) {
    game.arena=null;
    return {ok:true,finished:true,wave};
  }
  game.arena.wave+=1;
  return {ok:true,finished:false,wave:game.arena.wave};
}

export function addCollection(state,collectionId,itemId) {
  state.endgame.collections ||= {};
  state.endgame.collections[collectionId] ||= [];
  if (!state.endgame.collections[collectionId].includes(itemId)) state.endgame.collections[collectionId].push(itemId);
  return state.endgame.collections[collectionId];
}

export function depthReward(state,depth) {
  const reward={gold:depth*35,xp:depth*45};
  addGold(state,reward.gold);
  applyXp(state,reward.xp);
  return reward;
}
