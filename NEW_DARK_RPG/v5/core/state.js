// Chronicles of the Abyss V5 — canonical state foundation
// This module is intentionally isolated from the current release until Phase A integration passes.

export const SAVE_VERSION = 5;
export const MAX_DEPTH = 7;
export const ROOMS_PER_DEPTH = 5;

export function createInitialState() {
  return {
    version: SAVE_VERSION,
    meta: {
      deaths: 0,
      gold: 0,
      bestDepth: 1
    },
    character: {
      level: 1,
      xp: 0,
      classId: null,
      stats: {},
      skills: [],
      equipment: {}
    },
    inventory: [],
    abyss: {
      active: false,
      depth: 1,
      room: 0,
      pending: null,
      morale: 100,
      risk: 0,
      awareness: 50,
      tempo: 50,
      returnRewards: null
    },
    economy: {
      reputation: 0,
      merchants: {}
    },
    endgame: {
      arena: { bestWave: 0 },
      achievements: {},
      collections: {}
    }
  };
}

export function clampInteger(value, min, max, fallback) {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  return Math.max(min, Math.min(max, Math.trunc(n)));
}

export function normalizeState(input) {
  const base = createInitialState();
  const src = input && typeof input === "object" ? input : {};
  const out = structuredClone(base);

  out.version = SAVE_VERSION;
  out.meta.deaths = clampInteger(src.meta?.deaths, 0, 999999, 0);
  out.meta.gold = clampInteger(src.meta?.gold, 0, 999999999, 0);
  out.meta.bestDepth = clampInteger(src.meta?.bestDepth, 1, MAX_DEPTH, 1);

  out.character.level = clampInteger(src.character?.level, 1, 999, 1);
  out.character.xp = clampInteger(src.character?.xp, 0, 2147483647, 0);
  out.character.classId = typeof src.character?.classId === "string" ? src.character.classId : null;
  out.character.stats = src.character?.stats && typeof src.character.stats === "object" ? structuredClone(src.character.stats) : {};
  out.character.skills = Array.isArray(src.character?.skills) ? [...src.character.skills] : [];
  out.character.equipment = src.character?.equipment && typeof src.character.equipment === "object" ? structuredClone(src.character.equipment) : {};

  out.inventory = Array.isArray(src.inventory) ? structuredClone(src.inventory) : [];

  out.abyss.active = !!src.abyss?.active;
  out.abyss.depth = clampInteger(src.abyss?.depth, 1, MAX_DEPTH, 1);
  out.abyss.room = clampInteger(src.abyss?.room, 0, ROOMS_PER_DEPTH, 0);
  out.abyss.pending = src.abyss?.pending && typeof src.abyss.pending === "object" ? structuredClone(src.abyss.pending) : null;
  out.abyss.morale = clampInteger(src.abyss?.morale, 0, 100, 100);
  out.abyss.risk = clampInteger(src.abyss?.risk, 0, 100, 0);
  out.abyss.awareness = clampInteger(src.abyss?.awareness, 0, 100, 50);
  out.abyss.tempo = clampInteger(src.abyss?.tempo, 0, 100, 50);
  out.abyss.returnRewards = src.abyss?.returnRewards && typeof src.abyss.returnRewards === "object" ? structuredClone(src.abyss.returnRewards) : null;

  out.economy.reputation = clampInteger(src.economy?.reputation, 0, 9999999, 0);
  out.economy.merchants = src.economy?.merchants && typeof src.economy.merchants === "object" ? structuredClone(src.economy.merchants) : {};

  out.endgame = src.endgame && typeof src.endgame === "object" ? structuredClone(src.endgame) : base.endgame;
  return out;
}

export function migrateLegacyState(legacy) {
  const state = createInitialState();
  if (!legacy || typeof legacy !== "object") return state;

  state.meta.gold = clampInteger(legacy.gold, 0, 999999999, 0);
  state.abyss.depth = clampInteger(legacy.abyssFloor, 1, MAX_DEPTH, 1);
  state.abyss.room = clampInteger(legacy.abyssRoom, 0, ROOMS_PER_DEPTH, 0);
  state.abyss.active = !!legacy.abyssRun;
  return state;
}
