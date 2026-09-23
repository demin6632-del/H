// Chronicles of the Abyss V5 — exploration/event integration
import { createRoom, ROOM_TYPES } from "./rooms.js";
import { addToInventory } from "./inventory.js";
import { progressContract } from "./merchant.js";
import { addGold } from "./economy.js";
import { applyXp } from "./progression.js";
import { rollLoot } from "./loot.js";
import { createReturnRewards } from "./city-loop.js";

export function openRoom(game, random = Math.random) {
  const state = game.state;
  if (!state.abyss.active) return null;
  const depth = state.abyss.depth;
  const room = state.abyss.room + 1;
  const event = createRoom(depth, room, random);
  state.abyss.pending = { depth, room, event, resolved:false };
  return event;
}

export function resolveRoomAction(game, action, random = Math.random) {
  const state = game.state;
  const pending = state.abyss.pending;
  if (!pending || pending.resolved || pending.transition) return {ok:false,reason:"no_pending_room"};
  const event = pending.event;

  if ((event.type === ROOM_TYPES.ambush || event.type === ROOM_TYPES.elite || event.type === ROOM_TYPES.boss) && action === "fight") {
    game.combat = { enemy:event.enemy, depth:state.abyss.depth };
    return {ok:true,type:"combat",enemy:event.enemy};
  }

  if (event.type === ROOM_TYPES.ambush && action === "evade") {
    state.abyss.risk = Math.min(100,state.abyss.risk + 12);
    pending.resolved = true;
    return completeIntegratedRoom(game);
  }

  if (event.type === ROOM_TYPES.treasure) {
    if (action === "leave") { pending.resolved = true; return completeIntegratedRoom(game); }
    if (action === "inspect") {
      state.abyss.awareness = Math.min(100,state.abyss.awareness + 8);
      return {ok:true,type:"inspected"};
    }
    if (action === "open") {
      if (random() < 0.22) {
        state.abyss.risk = Math.min(100,state.abyss.risk + 15);
      } else {
        const reward = { gold:10 + Math.floor(random()*31), xp:15 + Math.floor(random()*21) };
        addGold(state,reward.gold);
        applyXp(state,reward.xp);
        progressContract(state,"treasure");
        pending.resolved = true;
        return {ok:true,type:"reward",reward};
      }
    }
  }

  if (event.type === ROOM_TYPES.trap) {
    if (action === "inspect") {
      state.abyss.awareness = Math.min(100,state.abyss.awareness + 10);
      return {ok:true,type:"inspected"};
    }
    if (action === "disarm") {
      if (random() < 0.65 + state.abyss.awareness / 400) {
        pending.resolved = true;
        return completeIntegratedRoom(game);
      }
      state.character.stats.hp = Math.max(0,(state.character.stats.hp||1)-Math.max(3,state.abyss.depth*2));
      return {ok:true,type:"trap_damage",damage:Math.max(3,state.abyss.depth*2)};
    }
    if (action === "rush") {
      const damage = Math.max(2,state.abyss.depth*3);
      state.character.stats.hp = Math.max(0,(state.character.stats.hp||1)-damage);
      pending.resolved = true;
      if (state.character.stats.hp <= 0) return {ok:true,type:"death"};
      return completeIntegratedRoom(game);
    }
  }

  if (event.type === ROOM_TYPES.crossroads) {
    if (["left","straight","right"].includes(action)) {
      state.abyss.awareness = Math.max(0,Math.min(100,state.abyss.awareness + (action==="straight"?3:-2)));
      pending.resolved = true;
      return completeIntegratedRoom(game);
    }
  }

  if (event.type === ROOM_TYPES.shrine) {
    if (["pray","search","leave"].includes(action)) {
      if (action === "pray") state.abyss.morale = Math.min(100,state.abyss.morale+12);
      if (action === "search" && random()<0.5) state.meta.gold += 15 + Math.floor(random()*20);
      pending.resolved = true;
      return completeIntegratedRoom(game);
    }
  }

  return {ok:false,reason:"invalid_action"};
}

export function completeIntegratedRoom(game) {
  const state = game.state;
  const pending = state.abyss.pending;
  if (!pending || pending.resolved !== true) return {ok:false,reason:"room_not_resolved"};
  if (state.abyss.room !== pending.room - 1) return {ok:false,reason:"room_sequence_error"};
  state.abyss.room = pending.room;
  state.abyss.pending = null;
  progressContract(state,"rooms");
  applyXp(state,10 + state.abyss.depth * 2);
  if (state.abyss.room === 5) state.abyss.pending = { transition:true, depth:state.abyss.depth };
  return {ok:true,room:state.abyss.room,depth:state.abyss.depth,transition:state.abyss.room===5};
}

import { resolveCombat } from "./combat-resolution.js";

export function finishCurrentCombat(game) {
  const result = resolveCombat(game);
  if (!result.ok || result.victory === null) return result;
  return completeCombatRoom(game, result.victory);
}

export function completeCombatRoom(game, victory) {
  const state = game.state;
  const pending = state.abyss.pending;
  if (!pending) return {ok:false,reason:"no_pending_room"};
  if (!victory) return {ok:false,reason:"combat_lost"};
  pending.resolved = true;
  const reward = 20 + state.abyss.depth * 8;
  addGold(state,reward);
  applyXp(state,20 + state.abyss.depth * 8);
  progressContract(state,"kills");
  const drops=rollLoot(state.abyss.depth);
  createReturnRewards(state,{items:drops,gold:reward,xp:20 + state.abyss.depth * 8});
  game.combat = null;
  return completeIntegratedRoom(game);
}
