// Chronicles of the Abyss V5 — economy
import { clampInteger } from "../core/state.js";

export function addGold(state, amount) {
  state.meta.gold = clampInteger(state.meta.gold + Math.trunc(amount), 0, 999999999, state.meta.gold);
  return state.meta.gold;
}

export function spendGold(state, amount) {
  const cost = Math.max(0, Math.trunc(amount));
  if (state.meta.gold < cost) return false;
  state.meta.gold -= cost;
  return true;
}

export function itemSellPrice(item, merchantModifier = 1) {
  const base = Math.max(1, Math.round((Object.values(item.stats || {}).reduce((a,v) => a + Math.max(0, Number(v) || 0), 0) + item.level * 2) * 3));
  const rarity = { common:1, uncommon:1.2, rare:1.5, epic:2, legendary:3 }[item.rarity] || 1;
  return Math.max(1, Math.round(base * rarity * merchantModifier));
}

export function itemBuyPrice(item, merchantModifier = 1) {
  return Math.max(itemSellPrice(item, merchantModifier) * 2, 10);
}
