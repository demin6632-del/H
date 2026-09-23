// Chronicles of the Abyss V5 — city services
import { addGold, spendGold, itemBuyPrice } from "./economy.js";
import { addItem } from "./items.js";

export const CITY_SERVICES = Object.freeze(["tavern","merchant","forge","arena"]);

export function buyItem(state, item, modifier = 1) {
  const price = itemBuyPrice(item, modifier);
  if (!spendGold(state, price)) return { ok:false, reason:"not_enough_gold", price };
  addItem(state, item);
  return { ok:true, price, item };
}

export function rewardRun(state, { gold = 0, xp = 0 } = {}) {
  addGold(state, gold);
  return { gold, xp };
}

export function merchantModifier(state) {
  return state.economy.reputation >= 100 ? 0.9 : state.economy.reputation < 0 ? 1.1 : 1;
}
