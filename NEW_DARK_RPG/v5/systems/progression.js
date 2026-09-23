// Chronicles of the Abyss V5 — RPG progression foundation
import { clampInteger } from "../core/state.js";

export const LEVEL_XP = Object.freeze([
  0, 100, 250, 450, 700, 1000, 1400, 1850, 2350, 2900,
  3500, 4150, 4850, 5600, 6400, 7250, 8150, 9100, 10100, 11150
]);

export const CLASSES = Object.freeze({
  vanguard: { id: "vanguard", name: "Страж", base: { hp: 120, power: 12, defense: 10, speed: 7 } },
  hunter: { id: "hunter", name: "Охотник", base: { hp: 90, power: 14, defense: 6, speed: 12 } },
  occultist: { id: "occultist", name: "Оккультист", base: { hp: 80, power: 16, defense: 5, speed: 10 } }
});

export function xpForLevel(level) {
  const n = clampInteger(level, 1, 999, 1);
  if (n <= LEVEL_XP.length) return LEVEL_XP[n - 1];
  const last = LEVEL_XP[LEVEL_XP.length - 1];
  return last + (n - LEVEL_XP.length) * 700;
}

export function levelForXp(xp) {
  const value = Math.max(0, Number(xp) || 0);
  let level = 1;
  while (level < 999 && value >= xpForLevel(level + 1)) level += 1;
  return level;
}

export function applyXp(state, amount) {
  const gain = Math.max(0, Math.trunc(Number(amount) || 0));
  state.character.xp += gain;
  state.character.level = levelForXp(state.character.xp);
  return state.character.level;
}

export function selectClass(state, classId) {
  if (!CLASSES[classId]) throw new Error("Unknown class");
  state.character.classId = classId;
  state.character.baseStats = { ...CLASSES[classId].base, maxHp: CLASSES[classId].base.hp, maxMp: 30 };
  state.character.stats = { ...state.character.baseStats };
  return state;
}
