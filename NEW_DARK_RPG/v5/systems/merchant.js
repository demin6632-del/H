// Chronicles of the Abyss V5 — merchant, consumables and contracts
import { createItem } from "./items.js";
import { addGold } from "./economy.js";
import { addToInventory } from "./inventory.js";

export const SHOP_ITEMS = Object.freeze({
  healing_potion:{id:"healing_potion",name:"Зелье лечения",slot:"consumable",rarity:"common",stackable:true,stats:{},basePrice:18},
  mana_potion:{id:"mana_potion",name:"Зелье маны",slot:"consumable",rarity:"common",stackable:true,stats:{},basePrice:20},
  abyss_key:{id:"abyss_key",name:"Ключ Бездны",slot:"resource",rarity:"uncommon",stackable:true,stats:{},basePrice:45},
  iron_shard:{id:"iron_shard",name:"Осколок железа",slot:"resource",rarity:"common",stackable:true,stats:{},basePrice:12}
});

export function merchantPrice(item, reputation = 0, modifier = 1) {
  const rep = Math.max(-0.2, Math.min(0.2, reputation * 0.01));
  return Math.max(1, Math.round((item.basePrice || 10) * modifier * (1 - rep)));
}

export function buy(state, itemId, quantity = 1, modifier = 1) {
  const def = SHOP_ITEMS[itemId];
  if (!def || quantity < 1) return {ok:false,reason:"invalid_item"};
  const price = merchantPrice(def, state.economy.reputation || 0, modifier);
  const total = price * Math.floor(quantity);
  if ((state.meta.gold || 0) < total) return {ok:false,reason:"not_enough_gold"};
  const item = createItem({...def, quantity});
  const result = addToInventory(state,item);
  if (!result.ok) return result;
  state.meta.gold -= total;
  return {ok:true,item:result.item,total};
}

export function sellPrice(item, state) {
  const base = SHOP_ITEMS[item.id]?.basePrice || 10;
  const reputation = state.economy.reputation || 0;
  return Math.max(1, Math.round(base * 0.5 * (1 + Math.max(-0.2,Math.min(0.2,reputation*0.01)))));
}

export function sell(state, instanceId) {
  const item = state.inventory.find(x => x.instanceId === instanceId);
  if (!item) return {ok:false,reason:"not_found"};
  const price = sellPrice(item,state);
  const sold = item.stackable && item.quantity > 1 ? {...item,quantity:1} : item;
  if (item.stackable && item.quantity > 1) item.quantity -= 1;
  else state.inventory.splice(state.inventory.indexOf(item),1);
  addGold(state,price);
  return {ok:true,item:sold,price};
}

export const CONTRACTS = Object.freeze([
  {id:"first_blood",name:"Первая кровь",type:"kills",target:3,reward:{gold:50,xp:40}},
  {id:"deep_steps",name:"Шаги в глубину",type:"rooms",target:5,reward:{gold:70,xp:60}},
  {id:"treasure_hunter",name:"Охотник за тайниками",type:"treasure",target:2,reward:{gold:90,xp:75}}
]);

export function acceptContract(state,id) {
  const contract = CONTRACTS.find(x => x.id === id);
  if (!contract) return {ok:false,reason:"contract_not_found"};
  state.endgame.contracts = state.endgame.contracts || {};
  state.endgame.contracts[id] = {id,progress:0,completed:false};
  return {ok:true,contract};
}

export function progressContract(state,type,amount=1) {
  for (const progress of Object.values(state.endgame.contracts || {})) {
    const contract = CONTRACTS.find(x => x.id === progress.id);
    if (!contract || progress.completed || contract.type !== type) continue;
    progress.progress = Math.min(contract.target, progress.progress + amount);
    if (progress.progress >= contract.target) progress.completed = true;
  }
  return state;
}

export function claimContract(state,id) {
  const progress = state.endgame.contracts?.[id];
  const contract = CONTRACTS.find(x => x.id === id);
  if (!progress || !contract) return {ok:false,reason:"contract_not_found"};
  if (!progress.completed || progress.claimed) return {ok:false,reason:"not_ready"};
  addGold(state,contract.reward.gold||0);
  state.endgame.contracts[id].claimed=true;
  return {ok:true,reward:contract.reward};
}
