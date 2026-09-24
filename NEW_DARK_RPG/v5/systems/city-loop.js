// Chronicles of the Abyss V5 — city preparation and return loop
import { addGold, spendGold } from "./economy.js";
import { recalculateCharacterStats } from "../systems/equipment.js";
import { addToInventory } from "./inventory.js";
import { applyXp } from "./../systems/progression.js";

export const CITY_ACTIONS=Object.freeze({
  heal:"heal", train:"train", prepare:"prepare", collect:"collect"
});

export function healAtTavern(game, cost=25) {
  const state=game.state;
  if ((state.meta.gold||0)<cost) return {ok:false,reason:"not_enough_gold"};
  state.meta.gold-=cost;
  const stats=state.character.stats||{};
  stats.hp=stats.maxHp||stats.hp||1;
  stats.mp=stats.maxMp||stats.mp||0;
  return {ok:true,hp:stats.hp,mp:stats.mp};
}

export function trainCharacter(game, cost=50) {
  if ((game.state.meta.gold||0)<cost) return {ok:false,reason:"not_enough_gold"};
  game.state.meta.gold-=cost;
  applyXp(game.state,75);
  return {ok:true,level:game.state.character.level,xp:game.state.character.xp};
}

export function prepareRun(game) {
  const state=game.state;
  recalculateCharacterStats(state);
  state.character.stats.hp=state.character.stats.maxHp;
  state.character.stats.mp=state.character.stats.maxMp;
  return {ok:true,stats:{...state.character.stats}};
}

export function collectReturnRewards(game) {
  const state=game.state;
  const pending=state.abyss.returnRewards;
  if (!pending || pending.collected) return {ok:false,reason:"no_rewards"};
  pending.collected=true;
  addGold(state,pending.gold||0);
  applyXp(state,pending.xp||0);
  for (const item of pending.items||[]) {
    const result=addToInventory(state,item);
    if (!result.ok) break;
  }
  state.abyss.returnRewards=null;
  return {ok:true};
}

export function createReturnRewards(state, extra={}) {
  state.abyss.returnRewards={
    collected:false,
    gold:Math.max(0,Math.trunc(extra.gold||0)),
    xp:Math.max(0,Math.trunc(extra.xp||0)),
    items:Array.isArray(extra.items)?extra.items:[],
    depth:state.abyss.depth
  };
  return state.abyss.returnRewards;
}
