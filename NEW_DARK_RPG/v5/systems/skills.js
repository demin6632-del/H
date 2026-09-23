// Chronicles of the Abyss V5 — class skills
import { addStatus, STATUS } from "./status.js";

export const SKILLS = Object.freeze({
  vanguard: [
    { id:"shield_break", name:"Разлом щита", cost:8, type:"damage", multiplier:1.35, effect:{ id:STATUS.bleed, turns:2, power:3 } },
    { id:"iron_guard", name:"Железная стойка", cost:10, type:"defense", effect:{ id:STATUS.fortify, turns:2, power:1 } }
  ],
  hunter: [
    { id:"aimed_shot", name:"Прицельный выстрел", cost:9, type:"damage", multiplier:1.65 },
    { id:"crippling_shot", name:"Калечащий выстрел", cost:7, type:"damage", multiplier:0.9, effect:{ id:STATUS.slow, turns:2, power:1 } }
  ],
  occultist: [
    { id:"ember_curse", name:"Пепельное проклятие", cost:10, type:"damage", multiplier:1.15, effect:{ id:STATUS.burn, turns:3, power:4 } },
    { id:"dark_ritual", name:"Тёмный ритуал", cost:12, type:"heal", multiplier:1.0, effect:{ id:STATUS.regen, turns:3, power:5 } }
  ]
});

export function skillsForClass(classId) {
  return SKILLS[classId] ? SKILLS[classId].map(skill => ({...skill, effect:skill.effect ? {...skill.effect} : undefined})) : [];
}

export function useSkill(combat, skillId) {
  const skill = combat.skills?.find(s => s.id === skillId);
  if (!skill || combat.phase !== "player") return { ok:false, reason:"skill_unavailable" };
  if (combat.player.mp < skill.cost) return { ok:false, reason:"not_enough_mp" };
  combat.player.mp -= skill.cost;
  const damage = skill.type === "damage"
    ? Math.max(1, Math.floor(combat.player.power * skill.multiplier) - Math.floor(combat.enemy.defense / 2))
    : 0;
  if (skill.type === "damage") combat.enemy.hp = Math.max(0, combat.enemy.hp - damage);
  if (skill.type === "heal") combat.player.hp = Math.min(combat.player.maxHp, combat.player.hp + Math.max(1, Math.floor(combat.player.maxHp * 0.15)));
  if (skill.effect) {
    if (skill.type === "defense" || skill.type === "heal") addStatus(combat.player, skill.effect.id, skill.effect.turns, skill.effect.power);
    else addStatus(combat.enemy, skill.effect.id, skill.effect.turns, skill.effect.power);
  }
  combat.log.push("Использовано: " + skill.name + ".");
  return { ok:true, damage, skill };
}
