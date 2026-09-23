// Chronicles of the Abyss V5 — deterministic combat core
import { clampInteger } from "../core/state.js";
import { skillsForClass, useSkill } from "./skills.js";
import { tickStatuses, modifyDamage } from "./status.js";

export const COMBAT_PHASES = Object.freeze({ idle:"idle", player:"player", enemy:"enemy", victory:"victory", defeat:"defeat" });

function actorFromStats(source, fallback) {
  const s = source?.stats || {};
  return {
    hp: clampInteger(s.hp, 1, 999999, fallback.hp),
    maxHp: clampInteger(s.hp, 1, 999999, fallback.hp),
    power: clampInteger(s.power, 1, 99999, fallback.power),
    defense: clampInteger(s.defense, 0, 99999, fallback.defense),
    speed: clampInteger(s.speed, 1, 99999, fallback.speed)
  };
}

export function createCombatState(character, enemy) {
  const player = actorFromStats(character, { hp:100, power:10, defense:5, speed:10 });
  const foe = actorFromStats({stats: enemy}, { hp:50, power:8, defense:2, speed:8 });
  return { phase:COMBAT_PHASES.player, turn:1, player, enemy:foe, enemyId:enemy.id || "unknown", log:[] };
}

export function attack(combat, source = "player") {
  if (![COMBAT_PHASES.player, COMBAT_PHASES.enemy].includes(combat.phase)) return { damage:0, ended:true };
  const a = source === "player" ? combat.player : combat.enemy;
  const d = source === "player" ? combat.enemy : combat.player;
  const damage = modifyDamage(d, Math.max(1, a.power - Math.floor(d.defense / 2)));
  d.hp = Math.max(0, d.hp - damage);
  combat.log.push((source === "player" ? "Игрок" : "Враг") + " наносит " + damage + " урона.");
  if (d.hp <= 0) {
    combat.phase = source === "player" ? COMBAT_PHASES.victory : COMBAT_PHASES.defeat;
    return { damage, ended:true };
  }
  combat.phase = source === "player" ? COMBAT_PHASES.enemy : COMBAT_PHASES.player;
  if (source === "enemy") combat.turn += 1;
  return { damage, ended:false };
}

export function playerTurn(combat) {
  const result = attack(combat, "player");
  if (!result.ended && combat.phase === COMBAT_PHASES.enemy) attack(combat, "enemy");
  tickStatuses(combat.player);
  tickStatuses(combat.enemy);
  return combat;
}
