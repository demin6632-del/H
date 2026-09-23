// Chronicles of the Abyss V5 — equipment stats, affixes and forge
import { RARITIES, createItem } from "./items.js";

export const SLOTS = Object.freeze(["weapon","armor","helmet","gloves","boots","amulet","ring"]);

export const AFFIXES = Object.freeze({
  power:{name:"Мощь",stat:"power",min:1,max:8},
  defense:{name:"Защита",stat:"defense",min:1,max:8},
  vitality:{name:"Живучесть",stat:"maxHp",min:3,max:20},
  precision:{name:"Точность",stat:"speed",min:1,max:5},
  focus:{name:"Фокус",stat:"maxMp",min:3,max:15},
  resilience:{name:"Стойкость",stat:"resistance",min:1,max:5}
});

function uuid() {
  return globalThis.crypto?.randomUUID?.() || "itm_" + Date.now().toString(36) + Math.random().toString(36).slice(2);
}

export function rollAffixes(rarity = "common", random = Math.random) {
  const count = rarity === "legendary" ? 3 : rarity === "epic" ? 2 : rarity === "rare" ? 1 : 0;
  const keys = Object.keys(AFFIXES);
  const out = [];
  const used = new Set();
  while (out.length < count) {
    const key = keys[Math.floor(random() * keys.length)];
    if (used.has(key)) continue;
    used.add(key);
    const a = AFFIXES[key];
    out.push({ id:key, name:a.name, stat:a.stat, value:a.min + Math.floor(random() * (a.max-a.min+1)) });
  }
  return out;
}

export function createEquipment(def, random = Math.random) {
  const item = createItem(def);
  item.affixes = rollAffixes(item.rarity, random);
  item.upgrade = 0;
  item.baseStats = {...item.stats};
  item.stats = {...item.stats};
  for (const a of item.affixes) item.stats[a.stat] = (item.stats[a.stat] || 0) + a.value;
  return item;
}

export function equipmentStats(state) {
  const total = {};
  for (const slot of SLOTS) {
    const id = state.character.equipment?.[slot];
    const item = state.inventory.find(x => x.instanceId === id);
    if (!item) continue;
    for (const [stat,value] of Object.entries(item.stats || {})) total[stat] = (total[stat] || 0) + value;
  }
  return total;
}

export function recalculateCharacterStats(state) {
  const base = state.character.baseStats || state.character.stats || {};
  const gear = equipmentStats(state);
  state.character.stats = {
    ...base,
    hp: Math.max(1, (base.hp || 1) + (gear.maxHp || 0)),
    maxHp: Math.max(1, (base.maxHp || base.hp || 1) + (gear.maxHp || 0)),
    power: Math.max(0, (base.power || 0) + (gear.power || 0)),
    defense: Math.max(0, (base.defense || 0) + (gear.defense || 0)),
    speed: Math.max(0, (base.speed || 0) + (gear.speed || 0)),
    maxMp: Math.max(0, (base.maxMp || 30) + (gear.maxMp || 0)),
    resistance: Math.max(0, (base.resistance || 0) + (gear.resistance || 0))
  };
  state.character.stats.hp = Math.min(state.character.stats.hp, state.character.stats.maxHp);
  return state.character.stats;
}

export function upgradeEquipment(state, instanceId, cost) {
  const item = state.inventory.find(x => x.instanceId === instanceId);
  if (!item || !item.affixes) throw new Error("Equipment not found");
  if (item.upgrade >= 10) throw new Error("Maximum upgrade reached");
  if ((state.economy.gold || 0) < cost) throw new Error("Not enough gold");
  state.economy.gold -= cost;
  item.upgrade += 1;
  for (const stat of Object.keys(item.stats)) {
    if (stat === "maxHp" || stat === "power" || stat === "defense" || stat === "speed" || stat === "maxMp" || stat === "resistance") {
      item.stats[stat] += 1;
    }
  }
  recalculateCharacterStats(state);
  return item;
}

export function forgeCost(item) {
  return Math.max(10, Math.round((item.level || 1) * (1 + (item.upgrade || 0)) * (RARITIES[item.rarity]?.power || 1)));
}

export function cloneEquipment(item, random = Math.random) {
  return createEquipment({
    id:item.id, name:item.name, slot:item.slot, rarity:item.rarity,
    level:item.level, stats:item.baseStats || item.stats, stackable:false
  }, random);
}
