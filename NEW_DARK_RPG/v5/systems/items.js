// Chronicles of the Abyss V5 — itemisation foundation
import { clampInteger } from "../core/state.js";

export const RARITIES = Object.freeze({
  common: { id: "common", name: "Обычный", power: 1 },
  uncommon: { id: "uncommon", name: "Необычный", power: 1.15 },
  rare: { id: "rare", name: "Редкий", power: 1.35 },
  epic: { id: "epic", name: "Эпический", power: 1.7 },
  legendary: { id: "legendary", name: "Легендарный", power: 2.2 }
});

export function createItem({ id, name, slot, rarity = "common", level = 1, stats = {}, stackable = false, quantity = 1 }) {
  if (!id || !name || !slot || !RARITIES[rarity]) throw new Error("Invalid item definition");
  return {
    instanceId: crypto.randomUUID(),
    id, name, slot, rarity,
    level: clampInteger(level, 1, 999, 1),
    stats: { ...stats },
    stackable: !!stackable,
    quantity: stackable ? Math.max(1, Math.trunc(quantity)) : 1
  };
}

export function addItem(state, item) {
  if (item.stackable) {
    const existing = state.inventory.find(x => x.id === item.id && x.rarity === item.rarity);
    if (existing) {
      existing.quantity += item.quantity;
      return existing;
    }
  }
  state.inventory.push(item);
  return item;
}

export function equipItem(state, instanceId) {
  const item = state.inventory.find(x => x.instanceId === instanceId);
  if (!item) throw new Error("Item not found");
  state.character.equipment[item.slot] = item.instanceId;
  return item;
}

export function unequipItem(state, slot) {
  delete state.character.equipment[slot];
}

export function sellOne(state, instanceId) {
  const index = state.inventory.findIndex(x => x.instanceId === instanceId);
  if (index < 0) throw new Error("Item not found");
  const item = state.inventory[index];
  if (item.stackable && item.quantity > 1) {
    item.quantity -= 1;
  } else {
    state.inventory.splice(index, 1);
  }
  return item;
}
