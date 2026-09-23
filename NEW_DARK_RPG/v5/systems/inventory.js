// Chronicles of the Abyss V5 — inventory operations
import { addItem, sellOne } from "./items.js";
import { recalculateCharacterStats } from "./equipment.js";

export const INVENTORY_CAPACITY = 24;

export function inventoryCount(state) {
  return state.inventory.reduce((sum, item) => sum + (item.stackable ? item.quantity : 1), 0);
}

export function canAdd(state, item) {
  if (item.stackable) {
    if (state.inventory.some(x => x.id === item.id && x.rarity === item.rarity)) return true;
    return inventoryCount(state) < INVENTORY_CAPACITY;
  }
  return inventoryCount(state) < INVENTORY_CAPACITY;
}

export function addToInventory(state, item) {
  if (!canAdd(state, item)) return { ok:false, reason:"inventory_full" };
  return { ok:true, item:addItem(state,item) };
}

export function removeOne(state, instanceId) {
  const item = sellOne(state, instanceId);
  if (state.character.equipment && Object.values(state.character.equipment).includes(item.instanceId)) {
    for (const [slot,id] of Object.entries(state.character.equipment)) if (id === item.instanceId) delete state.character.equipment[slot];
    recalculateCharacterStats(state);
  }
  return item;
}

export function sortInventory(state, mode = "rarity") {
  const rank = { legendary:5, epic:4, rare:3, uncommon:2, common:1 };
  state.inventory.sort((a,b) => {
    if (mode === "name") return a.name.localeCompare(b.name, "ru");
    if (mode === "level") return (b.level||1) - (a.level||1);
    return (rank[b.rarity]||0) - (rank[a.rarity]||0);
  });
  return state.inventory;
}
