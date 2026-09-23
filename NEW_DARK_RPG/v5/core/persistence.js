// Chronicles of the Abyss V5 — persistence foundation
import { SAVE_VERSION, createInitialState, normalizeState, migrateLegacyState } from "./state.js";

export const V5_SAVE_KEY = "chronicles_abyss_v5_state";
export const LEGACY_SAVE_KEYS = Object.freeze([
  "chronicles_abyss_save_v2",
  "chronicles_abyss_meta_v2",
  "chronicles_abyss_expedition_v2"
]);

export function serializeState(state) {
  return JSON.stringify(normalizeState(state));
}

export function loadState(storage = globalThis.localStorage) {
  try {
    const raw = storage.getItem(V5_SAVE_KEY);
    if (raw) return normalizeState(JSON.parse(raw));
  } catch (_) {}

  try {
    const legacy = {};
    for (const key of LEGACY_SAVE_KEYS) {
      const raw = storage.getItem(key);
      if (raw) legacy[key] = raw ? JSON.parse(raw) : null;
    }
    const migrated = migrateLegacyState({
      gold: legacy.chronicles_abyss_meta_v2?.gold ?? 0,
      abyssFloor: legacy.chronicles_abyss_save_v2?.abyssFloor ?? legacy.chronicles_abyss_expedition_v2?.depth,
      abyssRoom: legacy.chronicles_abyss_save_v2?.abyssRoom ?? legacy.chronicles_abyss_expedition_v2?.done,
      abyssRun: !!legacy.chronicles_abyss_expedition_v2?.active
    });
    return migrated;
  } catch (_) {
    return createInitialState();
  }
}

export function saveState(state, storage = globalThis.localStorage) {
  const normalized = normalizeState(state);
  storage.setItem(V5_SAVE_KEY, JSON.stringify(normalized));
  return normalized;
}

export function clearV5State(storage = globalThis.localStorage) {
  storage.removeItem(V5_SAVE_KEY);
}

export { SAVE_VERSION };
