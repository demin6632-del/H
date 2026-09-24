// Chronicles of the Abyss V5 — loot generation
import { createItem } from "./items.js";
import { createEquipment } from "./equipment.js";

export const LOOT_TABLE = Object.freeze([
  { id:"rust_blade", name:"Ржавая сабля", slot:"weapon", chance:0.45, stats:{power:4} },
  { id:"bone_armor", name:"Костяной доспех", slot:"armor", chance:0.30, stats:{defense:5} },
  { id:"dark_charm", name:"Тёмный оберег", slot:"amulet", chance:0.18, stats:{power:2, defense:2} },
  { id:"healing_potion", name:"Зелье лечения", slot:"consumable", chance:0.55, stackable:true, quantity:1, stats:{heal:30} }
]);

export function rollRarity(random = Math.random) {
  const r = random();
  if (r < 0.01) return "legendary";
  if (r < 0.05) return "epic";
  if (r < 0.18) return "rare";
  if (r < 0.40) return "uncommon";
  return "common";
}

export function rollLoot(depth = 1, random = Math.random) {
  const scale = Math.max(1, depth);
  const drops = [];
  for (const entry of LOOT_TABLE) {
    if (random() < entry.chance / 2) {
      const rarity = rollRarity(random);
      const stats = Object.fromEntries(
        Object.entries(entry.stats).map(([k,v]) => [k, Math.max(1, Math.round(v * scale / 2))])
      );
      const item = entry.slot === "consumable"
        ? createItem({ ...entry, rarity, level:scale, stats })
        : createEquipment({ ...entry, rarity, level:scale, stats }, random);
      drops.push(item);
    }
  }
  return drops;
}
