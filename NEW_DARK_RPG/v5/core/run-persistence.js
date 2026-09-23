// Chronicles of the Abyss V5 — run snapshot persistence
import { normalizeState } from "./state.js";
import { clone } from "./clone.js";

export const V5_RUN_KEY="chronicles_abyss_v5_run";

export function snapshotRun(game) {
  return {
    version:5,
    state:normalizeState(game.state),
    combat:game.combat ? clone(game.combat) : null,
    savedAt:Date.now()
  };
}

export function saveRun(game, storage=globalThis.localStorage) {
  const snapshot=snapshotRun(game);
  storage.setItem(V5_RUN_KEY,JSON.stringify(snapshot));
  return snapshot;
}

export function loadRun(storage=globalThis.localStorage) {
  try {
    const raw=storage.getItem(V5_RUN_KEY);
    if (!raw) return null;
    const snapshot=JSON.parse(raw);
    if (!snapshot || snapshot.version!==5) return null;
    return {
      state:normalizeState(snapshot.state),
      combat:snapshot.combat ? clone(snapshot.combat) : null,
      savedAt:Number(snapshot.savedAt)||0
    };
  } catch (_) { return null; }
}

export function clearRun(storage=globalThis.localStorage) {
  storage.removeItem(V5_RUN_KEY);
}

export function hasRun(storage=globalThis.localStorage) {
  return !!storage.getItem(V5_RUN_KEY);
}
