// Chronicles of the Abyss V5 — integration facade
// The UI will talk to this facade instead of mutating raw state directly.
import { createInitialState, normalizeState } from "../core/state.js";
import { beginRun, beginRoom, resolveChoice, completeRoom, nextDepth, die } from "./exploration.js";
import { applyXp } from "./progression.js";
import { addGold } from "./economy.js";
import { addItem } from "./items.js";
import { rollLoot } from "./loot.js";

export function createGame() {
  return { state:createInitialState(), combat:null };
}

export function startRun(game) {
  beginRun(game.state);
  beginRoom(game.state);
  return game;
}

export function choose(game, choice) {
  const result = resolveChoice(game.state, choice);
  if (result?.loot) result.loot.forEach(item => addItem(game.state, item));
  if (Number.isFinite(result?.gold)) addGold(game.state, result.gold);
  if (Number.isFinite(result?.xp)) applyXp(game.state, result.xp);
  return result;
}

export function finishRoom(game) {
  return completeRoom(game.state);
}

export function descend(game) {
  nextDepth(game.state);
  beginRoom(game.state);
  return game.state.abyss.depth;
}

export function killPlayer(game) {
  die(game.state);
  game.combat = null;
  return game.state;
}

export function grantCombatLoot(game, depth) {
  const drops = rollLoot(depth);
  drops.forEach(item => addItem(game.state, item));
  return drops;
}

export function loadGame(raw) {
  const game = createGame();
  game.state = normalizeState(raw);
  return game;
}
