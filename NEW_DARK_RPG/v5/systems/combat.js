// Chronicles of the Abyss V5 — turn combat
import { clampInteger } from "../core/state.js";
import { skillsForClass, useSkill } from "./skills.js";
import { tickStatuses, modifyDamage, hasStatus, STATUS } from "./status.js";
import { bossPhase } from "./combat-resolution.js";

export const COMBAT_PHASES = Object.freeze({ idle:"idle", player:"player", enemy:"enemy", victory:"victory", defeat:"defeat" });

function actorFromStats(source, fallback) {
  const s = source?.stats || {};
  return {
    hp: clampInteger(s.hp ?? s.maxHp, 1, 999999, fallback.hp),
    maxHp: clampInteger(s.maxHp ?? s.hp, 1, 999999, fallback.hp),
    power: clampInteger(s.power, 1, 99999, fallback.power),
    defense: clampInteger(s.defense, 0, 99999, fallback.defense),
    speed: clampInteger(s.speed, 1, 99999, fallback.speed),
    mp: clampInteger(s.maxMp, 0, 99999, fallback.mp || 0),
    maxMp: clampInteger(s.maxMp, 0, 99999, fallback.mp || 0),
    resistance: clampInteger(s.resistance, 0, 100, fallback.resistance || 0),
    statuses: {}
  };
}

export function createCombatState(character, enemy) {
  const player = actorFromStats(character, {hp:100,power:10,defense:5,speed:10,mp:30});
  const foe = actorFromStats({stats:enemy}, {hp:50,power:8,defense:2,speed:8,mp:0});
  return {
    phase: COMBAT_PHASES.player, turn:1, player, enemy:foe,
    enemyId:enemy.id || "unknown", enemyMeta:enemy,
    skills:skillsForClass(character?.classId), log:[], criticals:0
  };
}

function damageValue(attacker, defender, multiplier=1) {
  const critical = Math.random() < Math.min(0.25, 0.05 + attacker.speed / 500);
  const resistance = Math.max(0, defender.resistance || 0);
  const raw = Math.max(1, Math.floor(attacker.power * multiplier) - Math.floor(defender.defense / 2));
  const resisted = Math.max(1, Math.floor(raw * Math.max(0.5, 1 - resistance * 0.02)));
  return { damage:modifyDamage(defender, critical ? resisted * 2 : resisted), critical };
}

function endCheck(combat) {
  if (combat.enemy.hp <= 0) combat.phase = COMBAT_PHASES.victory;
  else if (combat.player.hp <= 0) combat.phase = COMBAT_PHASES.defeat;
  return combat.phase === COMBAT_PHASES.victory || combat.phase === COMBAT_PHASES.defeat;
}

export function basicAttack(combat, source="player") {
  if (combat.phase !== COMBAT_PHASES.player && combat.phase !== COMBAT_PHASES.enemy) return {ok:false,reason:"wrong_phase"};
  if (source === "player" && hasStatus(combat.player, STATUS.stun)) return {ok:false,reason:"stunned"};
  const a = source === "player" ? combat.player : combat.enemy;
  const d = source === "player" ? combat.enemy : combat.player;
  const hit = damageValue(a,d);
  d.hp = Math.max(0,d.hp-hit.damage);
  if (hit.critical && source==="player") combat.criticals++;
  combat.log.push((source==="player"?"Игрок":"Враг")+" наносит "+hit.damage+(hit.critical?" критический":"")+" урона.");
  endCheck(combat);
  if (source==="player" && !combat.enemyMeta?.boss) bossPhase(combat);
  if (source==="player" && combat.enemyMeta?.boss && combat.enemy.hp>0) bossPhase(combat);
  return {ok:true,damage:hit.damage,critical:hit.critical,ended:endCheck(combat)};
}

function enemyAction(combat) {
  if (hasStatus(combat.enemy, STATUS.stun)) {
    combat.log.push("Враг оглушён.");
    return;
  }
  let multiplier = 1;
  if (hasStatus(combat.enemy, STATUS.slow)) multiplier *= 0.9;
  const hit = damageValue(combat.enemy,combat.player,multiplier);
  combat.player.hp = Math.max(0,combat.player.hp-hit.damage);
  combat.log.push("Враг атакует и наносит "+hit.damage+" урона.");
}

function finishTurn(combat) {
  const playerEffects=tickStatuses(combat.player);
  const enemyEffects=tickStatuses(combat.enemy);
  if (playerEffects.length) combat.log.push("Состояния игрока обработаны.");
  if (enemyEffects.length) combat.log.push("Состояния врага обработаны.");
  if (endCheck(combat)) return;
  combat.turn++;
  combat.phase=COMBAT_PHASES.player;
}

export function playerAttack(combat) {
  const result=basicAttack(combat,"player");
  if (!result.ok || result.ended) return result;
  enemyAction(combat);
  if (endCheck(combat)) return {...result,ended:true};
  finishTurn(combat);
  return {...result,ended:false};
}

export function playerSkill(combat, skillId) {
  if (combat.phase!==COMBAT_PHASES.player) return {ok:false,reason:"wrong_phase"};
  if (hasStatus(combat.player,STATUS.stun)) return {ok:false,reason:"stunned"};
  const result=useSkill(combat,skillId);
  if (!result.ok) return result;
  if (endCheck(combat)) return {...result,ended:true};
  enemyAction(combat);
  if (endCheck(combat)) return {...result,ended:true};
  finishTurn(combat);
  return {...result,ended:false};
}

export function playerDefend(combat) {
  if (combat.phase!==COMBAT_PHASES.player) return {ok:false,reason:"wrong_phase"};
  combat.player.statuses.fortify={turns:1,power:1};
  combat.log.push("Игрок принимает защитную стойку.");
  enemyAction(combat);
  if (endCheck(combat)) return {ok:true,ended:true};
  finishTurn(combat);
  return {ok:true,ended:false};
}

export function playerTurn(combat) {
  return playerAttack(combat);
}

export const attack = basicAttack;
