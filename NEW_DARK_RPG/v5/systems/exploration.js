// Chronicles of the Abyss V5 — exploration state machine foundation
import { MAX_DEPTH, ROOMS_PER_DEPTH, clampInteger } from "./state.js";

export const PHASES = Object.freeze({
  IDLE: "idle",
  CHOOSING: "choosing",
  RESOLVING: "resolving",
  COMPLETE: "complete",
  DEAD: "dead"
});

export function beginRun(state) {
  state.abyss.active = true;
  state.abyss.pending = null;
  state.abyss.depth = clampInteger(state.abyss.depth, 1, MAX_DEPTH, 1);
  state.abyss.room = clampInteger(state.abyss.room, 0, ROOMS_PER_DEPTH, 0);
  state.abyss.morale = 100;
  state.abyss.risk = 0;
  state.abyss.awareness = 50;
  state.abyss.tempo = 50;
  return state;
}

export function beginRoom(state, event) {
  if (!state.abyss.active) throw new Error("Expedition is not active");
  if (state.abyss.room >= ROOMS_PER_DEPTH) throw new Error("Depth is already complete");
  state.abyss.pending = {
    phase: PHASES.CHOOSING,
    event: structuredClone(event)
  };
  return state;
}

export function resolveChoice(state, result) {
  if (!state.abyss.pending || state.abyss.pending.phase !== PHASES.CHOOSING) {
    throw new Error("No room choice is pending");
  }

  state.abyss.pending.phase = PHASES.RESOLVING;
  if (result?.moraleDelta) state.abyss.morale = clampInteger(state.abyss.morale + result.moraleDelta, 0, 100, state.abyss.morale);
  if (result?.riskDelta) state.abyss.risk = clampInteger(state.abyss.risk + result.riskDelta, 0, 100, state.abyss.risk);
  if (result?.awarenessDelta) state.abyss.awareness = clampInteger(state.abyss.awareness + result.awarenessDelta, 0, 100, state.abyss.awareness);
  if (result?.tempoDelta) state.abyss.tempo = clampInteger(state.abyss.tempo + result.tempoDelta, 0, 100, state.abyss.tempo);
  return state;
}

export function completeRoom(state) {
  if (!state.abyss.pending || state.abyss.pending.phase !== PHASES.RESOLVING) {
    throw new Error("Room cannot be completed from the current phase");
  }
  state.abyss.room = Math.min(ROOMS_PER_DEPTH, state.abyss.room + 1);
  state.abyss.pending = null;
  return state;
}

export function nextDepth(state) {
  if (state.abyss.room !== ROOMS_PER_DEPTH) throw new Error("Current depth is not complete");
  if (state.abyss.depth >= MAX_DEPTH) {
    state.abyss.active = false;
    return state;
  }
  state.abyss.depth += 1;
  state.abyss.room = 0;
  state.abyss.pending = null;
  state.abyss.morale = clampInteger(state.abyss.morale + 5, 0, 100, 100);
  state.abyss.risk = clampInteger(state.abyss.risk - 10, 0, 100, 0);
  state.abyss.awareness = clampInteger(state.abyss.awareness + 3, 0, 100, 50);
  state.abyss.tempo = 50;
  return state;
}

export function die(state) {
  state.meta.deaths += 1;
  state.abyss.active = false;
  state.abyss.room = 0;
  state.abyss.pending = null;
  state.abyss.morale = 100;
  state.abyss.risk = 0;
  state.abyss.awareness = 50;
  state.abyss.tempo = 50;
  return state;
}
