// Chronicles of the Abyss V5 — room encounter generator
import { createEnemy, createBoss } from "./enemies.js";

export const ROOM_TYPES = Object.freeze({
  trap:"trap", treasure:"treasure", crossroads:"crossroads", ambush:"ambush", elite:"elite", boss:"boss", shrine:"shrine"
});

export function createRoom(depth, room, random = Math.random) {
  if (room === 5) return { type:depth === 7 ? ROOM_TYPES.boss : ROOM_TYPES.elite, title:depth === 7 ? "Владыка глубины" : "Элитное логово", enemy:depth === 7 ? createBoss(depth) : createEnemy(depth, random, true) };
  const roll = random();
  if (roll < 0.18) return { type:ROOM_TYPES.trap, title:"Опасный механизм", actions:["inspect","disarm","rush"] };
  if (roll < 0.36) return { type:ROOM_TYPES.treasure, title:"Запечатанный тайник", actions:["inspect","open","leave"] };
  if (roll < 0.50) return { type:ROOM_TYPES.crossroads, title:"Развилка", actions:["left","straight","right"] };
  if (roll < 0.78) return { type:ROOM_TYPES.ambush, title:"Засада", enemy:createEnemy(depth, random), actions:["fight","evade"] };
  return { type:ROOM_TYPES.shrine, title:"Забытый алтарь", actions:["pray","search","leave"] };
}
